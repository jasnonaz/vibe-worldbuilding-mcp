#!/usr/bin/env python3
"""
Test Suite Runner for Vibe Worldbuilding System

This script provides a unified interface for running all tests in the system.

Usage:
    python run_tests.py [test_type] [options]
    
Test Types:
    unit        - Run unit tests for individual components
    integration - Run end-to-end integration tests  
    performance - Run performance and load tests
    all         - Run all test types (default)
"""

import asyncio
import argparse
import sys
import time
from pathlib import Path
import subprocess


class TestSuiteRunner:
    """Manages and executes the complete test suite."""
    
    def __init__(self, verbose: bool = False, cleanup: bool = True):
        self.verbose = verbose
        self.cleanup = cleanup
        self.test_dir = Path("test-worlds")
        self.results = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with level."""
        if self.verbose or level in ["ERROR", "SUCCESS", "SUMMARY"]:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")
    
    def ensure_test_dir(self):
        """Ensure test directories exist."""
        self.test_dir.mkdir(exist_ok=True)
        (self.test_dir / "unit").mkdir(exist_ok=True)
        (self.test_dir / "integration").mkdir(exist_ok=True)
        (self.test_dir / "performance").mkdir(exist_ok=True)
    
    async def run_unit_tests(self) -> bool:
        """Run unit tests for individual components."""
        self.log("Running unit tests...")
        
        # For now, unit tests are placeholder - we'll add specific component tests later
        self.log("Unit tests: PLACEHOLDER - No specific unit tests implemented yet")
        
        # Add basic import tests
        try:
            from vibe_worldbuilding import server
            from vibe_worldbuilding.tools import world, taxonomy, entries, site
            from vibe_worldbuilding.types import schemas
            from vibe_worldbuilding.utils import content_parsing, file_ops, path_helpers
            
            self.log("✅ All imports successful", "SUCCESS")
            self.results["unit_imports"] = True
            return True
            
        except Exception as e:
            self.log(f"❌ Import test failed: {e}", "ERROR")
            self.results["unit_imports"] = False
            return False
    
    async def run_integration_tests(self) -> bool:
        """Run end-to-end integration tests."""
        self.log("Running integration tests...")
        
        try:
            # Run the comprehensive E2E test
            cmd = [
                sys.executable, "tests/test_e2e_comprehensive.py",
                "--base-dir", str(self.test_dir / "integration"),
                "--verbose" if self.verbose else "",
                "--cleanup" if self.cleanup else "",
                "--skip-images"  # Skip images in automated tests
            ]
            
            # Filter out empty strings
            cmd = [arg for arg in cmd if arg]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ Integration tests passed", "SUCCESS")
                self.results["integration"] = True
                return True
            else:
                self.log(f"❌ Integration tests failed", "ERROR")
                if self.verbose:
                    self.log(f"STDOUT: {result.stdout}")
                    self.log(f"STDERR: {result.stderr}")
                self.results["integration"] = False
                return False
                
        except Exception as e:
            self.log(f"❌ Integration test error: {e}", "ERROR")
            self.results["integration"] = False
            return False
    
    async def run_performance_tests(self) -> bool:
        """Run performance and load tests."""
        self.log("Running performance tests...")
        
        # For now, performance tests are placeholder
        self.log("Performance tests: PLACEHOLDER - Will add timing benchmarks")
        
        # Add basic timing test for world creation
        try:
            start_time = time.time()
            
            # Import and test basic functionality timing
            from vibe_worldbuilding.tools.world import handle_world_tool
            
            # Time a simple operation
            result = await handle_world_tool("instantiate_world", {
                "world_name": "perf-test",
                "world_content": "# Performance Test World\n\nTesting creation speed.",
                "base_directory": str(self.test_dir / "performance")
            })
            
            duration = time.time() - start_time
            
            # Check if world was created within reasonable time (5 seconds)
            if duration < 5.0 and result and "successfully" in result[0].text:
                self.log(f"✅ Performance test passed ({duration:.2f}s)", "SUCCESS")
                self.results["performance"] = True
                
                # Cleanup performance test world
                if self.cleanup:
                    import shutil
                    perf_dirs = list((self.test_dir / "performance").glob("perf-test-*"))
                    for perf_dir in perf_dirs:
                        shutil.rmtree(perf_dir)
                
                return True
            else:
                self.log(f"❌ Performance test failed (too slow: {duration:.2f}s)", "ERROR")
                self.results["performance"] = False
                return False
                
        except Exception as e:
            self.log(f"❌ Performance test error: {e}", "ERROR")
            self.results["performance"] = False
            return False
    
    async def run_all_tests(self, test_types: list = None) -> dict:
        """Run specified test types or all tests."""
        if test_types is None:
            test_types = ["unit", "integration", "performance"]
        
        self.log("Starting test suite execution", "SUMMARY")
        self.ensure_test_dir()
        
        overall_success = True
        start_time = time.time()
        
        if "unit" in test_types:
            success = await self.run_unit_tests()
            overall_success = overall_success and success
        
        if "integration" in test_types:
            success = await self.run_integration_tests()
            overall_success = overall_success and success
        
        if "performance" in test_types:
            success = await self.run_performance_tests()
            overall_success = overall_success and success
        
        duration = time.time() - start_time
        
        # Summary
        passed = sum(1 for result in self.results.values() if result)
        total = len(self.results)
        
        self.log("="*60, "SUMMARY")
        self.log("TEST SUITE RESULTS", "SUMMARY")
        self.log("="*60, "SUMMARY")
        
        for test_name, success in self.results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            self.log(f"{status} {test_name}", "SUMMARY")
        
        self.log("-"*60, "SUMMARY")
        self.log(f"Overall: {passed}/{total} test groups passed", "SUMMARY")
        self.log(f"Duration: {duration:.2f} seconds", "SUMMARY")
        self.log(f"Status: {'SUCCESS' if overall_success else 'FAILED'}", 
                "SUCCESS" if overall_success else "ERROR")
        
        return {
            "success": overall_success,
            "results": self.results,
            "duration": duration,
            "passed": passed,
            "total": total
        }


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run vibe-worldbuilding test suite")
    parser.add_argument("test_type", nargs="?", default="all",
                       choices=["unit", "integration", "performance", "all"],
                       help="Type of tests to run (default: all)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--no-cleanup", action="store_true", help="Don't clean up test artifacts")
    
    args = parser.parse_args()
    
    # Determine test types to run
    if args.test_type == "all":
        test_types = ["unit", "integration", "performance"]
    else:
        test_types = [args.test_type]
    
    # Run the test suite
    runner = TestSuiteRunner(
        verbose=args.verbose,
        cleanup=not args.no_cleanup
    )
    
    try:
        results = await runner.run_all_tests(test_types)
        
        if results["success"]:
            print(f"\n🎉 TEST SUITE PASSED ({results['passed']}/{results['total']})")
            sys.exit(0)
        else:
            print(f"\n❌ TEST SUITE FAILED ({results['passed']}/{results['total']})")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nTest suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test suite error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())