#!/usr/bin/env python3
"""
Simple End-to-End Integration Test for Vibe Worldbuilding System

This script tests the key integration points by directly importing and using
the MCP tool functions in a way that mimics how they would be called.

Usage:
    python test_e2e_simple.py [--cleanup] [--verbose]
"""

import asyncio
import sys
import time
import shutil
from pathlib import Path
import argparse

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import the tool handlers directly
from vibe_worldbuilding.tools.world import handle_world_tool
from vibe_worldbuilding.tools.taxonomy import handle_taxonomy_tool
from vibe_worldbuilding.tools.entries import handle_entry_tool
from vibe_worldbuilding.tools.site import handle_site_tool


class SimpleE2ETest:
    """Simple end-to-end test using direct tool handler calls."""
    
    def __init__(self, base_dir: str, verbose: bool = False):
        self.base_dir = Path(base_dir)
        self.verbose = verbose
        self.test_world_name = f"test-world-{int(time.time())}"
        self.world_directory = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message."""
        if self.verbose or level in ["ERROR", "SUCCESS"]:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")
    
    async def run_test(self) -> bool:
        """Run the complete end-to-end test."""
        self.log("Starting simple E2E integration test")
        
        try:
            # Test 1: World Creation
            self.log("Creating test world...")
            world_result = await handle_world_tool("instantiate_world", {
                "world_name": self.test_world_name,
                "world_content": "# Test World\n\nA simple test world for integration testing.",
                "taxonomies": [
                    {"name": "characters", "description": "Test characters"},
                    {"name": "locations", "description": "Test locations"}
                ],
                "base_directory": str(self.base_dir)
            })
            
            result_text = world_result[0].text if world_result else ""
            if "successfully" not in result_text.lower():
                self.log(f"World creation failed: {result_text}", "ERROR")
                return False
                
            self.log("✅ World creation successful", "SUCCESS")
            
            # Find the created world directory
            world_dirs = list(self.base_dir.glob(f"{self.test_world_name}-*"))
            if not world_dirs:
                self.log("World directory not found", "ERROR")
                return False
                
            self.world_directory = world_dirs[0]
            self.log(f"Found world directory: {self.world_directory}")
            
            # Test 2: Entry Creation
            self.log("Creating test entry...")
            entry_result = await handle_entry_tool("create_world_entry", {
                "world_directory": str(self.world_directory),
                "taxonomy": "characters",
                "entry_name": "Test Hero",
                "entry_content": "A brave hero who wields the Sword of Light and protects the Crystal City."
            })
            
            entry_text = entry_result[0].text if entry_result else ""
            if "successfully" not in entry_text.lower():
                self.log(f"Entry creation failed: {entry_text}", "ERROR")
                return False
                
            self.log("✅ Entry creation successful", "SUCCESS")
            
            # Test 3: Site Building
            self.log("Building static site...")
            site_result = await handle_site_tool("build_static_site", {
                "world_directory": str(self.world_directory),
                "action": "build"
            })
            
            site_text = site_result[0].text if site_result else ""
            if "successfully" not in site_text.lower():
                self.log(f"Site building failed: {site_text}", "ERROR")
                return False
                
            self.log("✅ Site building successful", "SUCCESS")
            
            # Test 4: Validation
            self.log("Validating generated content...")
            
            # Check if site directory exists
            site_dir = self.world_directory / "site"
            if not site_dir.exists():
                self.log("Site directory not found", "ERROR")
                return False
                
            # Check for key files
            required_files = ["index.html", "gallery/index.html"]
            for file_path in required_files:
                if not (site_dir / file_path).exists():
                    self.log(f"Required file missing: {file_path}", "ERROR")
                    return False
                    
            # Check if entry was created
            entry_file = self.world_directory / "entries" / "characters" / "test-hero.md"
            if not entry_file.exists():
                self.log("Entry file not found", "ERROR")
                return False
                
            self.log("✅ Content validation successful", "SUCCESS")
            
            self.log("🎉 All tests passed! End-to-end integration successful.", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Test failed with exception: {e}", "ERROR")
            return False
    
    def cleanup(self):
        """Clean up test world."""
        if self.world_directory and self.world_directory.exists():
            shutil.rmtree(self.world_directory)
            self.log(f"Cleaned up test world: {self.world_directory}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run simple E2E integration test")
    parser.add_argument("--cleanup", action="store_true", help="Clean up after test")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--base-dir", default="./test-worlds", help="Base directory for test")
    
    args = parser.parse_args()
    
    # Run the test
    test = SimpleE2ETest(args.base_dir, args.verbose)
    
    try:
        success = await test.run_test()
        
        if args.cleanup:
            test.cleanup()
            
        if success:
            print("\n🎉 INTEGRATION TEST PASSED")
            print("The worldbuilding system is working correctly end-to-end!")
            sys.exit(0)
        else:
            print("\n❌ INTEGRATION TEST FAILED")
            print("Check the output above for specific failure details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        if args.cleanup:
            test.cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"Test runner error: {e}")
        if args.cleanup:
            test.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())