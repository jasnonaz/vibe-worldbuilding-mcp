#!/usr/bin/env python3
"""
End-to-End Integration Test for Vibe Worldbuilding System

This script tests the complete workflow from world creation to static site generation
by acting as an MCP client and calling the worldbuilding tools:

1. World instantiation with taxonomies
2. Taxonomy creation with custom guidelines
3. Entry creation with auto-stub generation
4. Image generation for entries
5. Static site building with gallery functionality
6. Validation of generated content

Usage:
    python test_e2e_integration.py [--cleanup] [--verbose]
"""

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional


class MCPClient:
    """Simple MCP client for testing the worldbuilding server."""

    def __init__(self, server_script: str):
        self.server_script = server_script
        self.process = None

    async def start_server(self):
        """Start the MCP server process."""
        self.process = await asyncio.create_subprocess_exec(
            sys.executable,
            self.server_script,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Send initialization
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }
        await self._send_message(init_msg)
        response = await self._read_message()

        # Send initialized notification
        initialized_msg = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        await self._send_message(initialized_msg)

        return response

    async def call_tool(self, name: str, arguments: dict) -> dict:
        """Call an MCP tool."""
        msg = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
        await self._send_message(msg)
        return await self._read_message()

    async def list_tools(self) -> dict:
        """List available tools."""
        msg = {"jsonrpc": "2.0", "id": int(time.time() * 1000), "method": "tools/list"}
        await self._send_message(msg)
        return await self._read_message()

    async def _send_message(self, message: dict):
        """Send a JSON-RPC message to the server."""
        json_msg = json.dumps(message) + "\n"
        self.process.stdin.write(json_msg.encode())
        await self.process.stdin.drain()

    async def _read_message(self) -> dict:
        """Read a JSON-RPC message from the server."""
        line = await self.process.stdout.readline()
        if line:
            return json.loads(line.decode().strip())
        return {}

    async def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()


class E2ETestRunner:
    """End-to-end integration test runner for the worldbuilding system."""

    def __init__(self, base_dir: str, verbose: bool = False):
        self.base_dir = Path(base_dir)
        self.verbose = verbose
        self.test_world_name = f"test-world-{int(time.time())}"
        self.world_directory = None
        self.results = []
        self.mcp_client = None

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        if self.verbose or level in ["ERROR", "SUCCESS"]:
            print(f"[{timestamp}] {level}: {message}")

    def record_result(
        self, test_name: str, success: bool, message: str = "", duration: float = 0
    ):
        """Record a test result."""
        self.results.append(
            {
                "test": test_name,
                "success": success,
                "message": message,
                "duration": duration,
            }
        )
        status = "✅ PASS" if success else "❌ FAIL"
        self.log(
            f"{status} {test_name} ({duration:.2f}s) - {message}",
            "SUCCESS" if success else "ERROR",
        )

    async def setup_mcp_client(self) -> bool:
        """Setup and initialize the MCP client."""
        try:
            server_script = Path(__file__).parent / "vibe_worldbuilding" / "server.py"
            self.mcp_client = MCPClient(str(server_script))

            init_response = await self.mcp_client.start_server()
            self.log(
                f"MCP server initialized: {init_response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}"
            )

            # List available tools
            tools_response = await self.mcp_client.list_tools()
            tools = tools_response.get("result", {}).get("tools", [])
            self.log(f"Available tools: {len(tools)}")

            return True

        except Exception as e:
            self.log(f"MCP client setup failed: {e}", "ERROR")
            return False

    async def test_world_instantiation(self) -> bool:
        """Test 1: Create a new world with initial taxonomies."""
        start_time = time.time()

        try:
            world_content = """# Test Fantasy Realm

A magical world filled with ancient mysteries, diverse cultures, and powerful artifacts.

## Core Concept

Magic flows through crystalline networks that connect floating islands across a vast sky realm. Different cultures have developed unique relationships with these magical crystals, leading to diverse societies and conflicts.

## Current Situation

The Great Crystal Network is failing, causing islands to drift apart and magic to become unstable. Heroes must discover the cause and restore balance before the realm fractures completely."""

            taxonomies = [
                {
                    "name": "characters",
                    "description": "People, heroes, villains, and notable figures in the fantasy realm",
                },
                {
                    "name": "locations",
                    "description": "Magical places, cities, dungeons, and significant geographical features",
                },
                {
                    "name": "artifacts",
                    "description": "Magical items, weapons, and mystical objects of power",
                },
                {
                    "name": "cultures",
                    "description": "Societies, races, and civilizations in the fantasy realm",
                },
            ]

            response = await self.mcp_client.call_tool(
                "instantiate_world",
                {
                    "world_name": self.test_world_name,
                    "world_content": world_content,
                    "taxonomies": taxonomies,
                    "base_directory": str(self.base_dir),
                },
            )

            # Extract result text from MCP response
            result = ""
            if "result" in response and "content" in response["result"]:
                content = response["result"]["content"]
                if isinstance(content, list) and len(content) > 0:
                    result = content[0].get("text", "")

            # Parse the result to get the world directory
            if "successfully" in result:
                # Extract world directory from result message
                world_dirs = list(self.base_dir.glob(f"{self.test_world_name}-*"))
                if world_dirs:
                    self.world_directory = world_dirs[0]
                    self.log(f"World created at: {self.world_directory}")

                    # Verify structure
                    required_dirs = ["entries", "taxonomies", "overview", "notes"]
                    missing_dirs = [
                        d
                        for d in required_dirs
                        if not (self.world_directory / d).exists()
                    ]

                    if missing_dirs:
                        self.record_result(
                            "World Instantiation",
                            False,
                            f"Missing directories: {missing_dirs}",
                            time.time() - start_time,
                        )
                        return False

                    self.record_result(
                        "World Instantiation",
                        True,
                        f"Created world with {len(taxonomies)} taxonomies",
                        time.time() - start_time,
                    )
                    return True
                else:
                    self.record_result(
                        "World Instantiation",
                        False,
                        "World directory not found",
                        time.time() - start_time,
                    )
                    return False
            else:
                self.record_result(
                    "World Instantiation",
                    False,
                    f"Creation failed: {result}",
                    time.time() - start_time,
                )
                return False

        except Exception as e:
            self.record_result(
                "World Instantiation",
                False,
                f"Exception: {str(e)}",
                time.time() - start_time,
            )
            return False

    async def test_taxonomy_guidelines(self) -> bool:
        """Test 2: Generate and apply custom taxonomy guidelines."""
        start_time = time.time()

        try:
            # Test generating guidelines for the characters taxonomy
            guidelines_result = generate_taxonomy_guidelines(
                taxonomy_name="characters",
                taxonomy_description="People, heroes, villains, and notable figures in the fantasy realm",
            )

            if "guidelines" not in guidelines_result.lower():
                self.record_result(
                    "Taxonomy Guidelines",
                    False,
                    "Guidelines generation failed",
                    time.time() - start_time,
                )
                return False

            # Create taxonomy with custom guidelines
            taxonomy_result = create_taxonomy_folders(
                world_directory=str(self.world_directory),
                taxonomy_name="characters",
                taxonomy_description="People, heroes, villains, and notable figures in the fantasy realm",
                custom_guidelines=guidelines_result,
            )

            if "successfully" in taxonomy_result:
                # Verify taxonomy structure
                chars_dir = self.world_directory / "entries" / "characters"
                if chars_dir.exists():
                    self.record_result(
                        "Taxonomy Guidelines",
                        True,
                        "Generated guidelines and created taxonomy structure",
                        time.time() - start_time,
                    )
                    return True
                else:
                    self.record_result(
                        "Taxonomy Guidelines",
                        False,
                        "Taxonomy directory not created",
                        time.time() - start_time,
                    )
                    return False
            else:
                self.record_result(
                    "Taxonomy Guidelines",
                    False,
                    f"Taxonomy creation failed: {taxonomy_result}",
                    time.time() - start_time,
                )
                return False

        except Exception as e:
            self.record_result(
                "Taxonomy Guidelines",
                False,
                f"Exception: {str(e)}",
                time.time() - start_time,
            )
            return False

    async def test_entry_creation(self) -> bool:
        """Test 3: Create entries with auto-stub generation."""
        start_time = time.time()

        try:
            # Create a character entry that should generate stubs
            entry_content = """A legendary warrior who wields the Crystal Sword of Lumina. She leads the Sky Guard from the floating city of Aerialis and has sworn to protect the Great Crystal Network. 

She discovered the magical Orb of Winds during her quest in the Whispering Caverns and now seeks to prevent the Shadow Cult from corrupting the crystal network."""

            result = create_world_entry(
                world_directory=str(self.world_directory),
                taxonomy="characters",
                entry_name="Lyra Skyward",
                entry_content=entry_content,
            )

            if "successfully" in result:
                # Check if entry was created
                entry_file = (
                    self.world_directory / "entries" / "characters" / "lyra-skyward.md"
                )
                if entry_file.exists():
                    # Check for stub generation (should create stubs for mentioned entities)
                    entries_dir = self.world_directory / "entries"
                    all_entries = []
                    for taxonomy_dir in entries_dir.iterdir():
                        if taxonomy_dir.is_dir():
                            for entry_file in taxonomy_dir.glob("*.md"):
                                all_entries.append(entry_file.name)

                    self.log(f"Found {len(all_entries)} total entries after creation")

                    self.record_result(
                        "Entry Creation",
                        True,
                        f"Created entry and {len(all_entries) - 1} potential stubs",
                        time.time() - start_time,
                    )
                    return True
                else:
                    self.record_result(
                        "Entry Creation",
                        False,
                        "Entry file not created",
                        time.time() - start_time,
                    )
                    return False
            else:
                self.record_result(
                    "Entry Creation",
                    False,
                    f"Entry creation failed: {result}",
                    time.time() - start_time,
                )
                return False

        except Exception as e:
            self.record_result(
                "Entry Creation",
                False,
                f"Exception: {str(e)}",
                time.time() - start_time,
            )
            return False

    async def test_image_generation(self) -> bool:
        """Test 4: Generate images for created entries."""
        start_time = time.time()

        try:
            # Find the character entry we created
            entry_file = (
                self.world_directory / "entries" / "characters" / "lyra-skyward.md"
            )

            if not entry_file.exists():
                self.record_result(
                    "Image Generation",
                    False,
                    "Entry file not found for image generation",
                    time.time() - start_time,
                )
                return False

            # Generate image for the entry
            result = generate_image_from_markdown_file(
                filepath=str(entry_file),
                style="fantasy illustration",
                aspect_ratio="1:1",
            )

            if "successfully" in result:
                # Check if image was created
                image_file = (
                    self.world_directory / "images" / "characters" / "lyra-skyward.png"
                )
                if image_file.exists():
                    self.record_result(
                        "Image Generation",
                        True,
                        "Generated image for character entry",
                        time.time() - start_time,
                    )
                    return True
                else:
                    self.record_result(
                        "Image Generation",
                        False,
                        "Image file not created",
                        time.time() - start_time,
                    )
                    return False
            else:
                self.record_result(
                    "Image Generation",
                    False,
                    f"Image generation failed: {result}",
                    time.time() - start_time,
                )
                return False

        except Exception as e:
            self.record_result(
                "Image Generation",
                False,
                f"Exception: {str(e)}",
                time.time() - start_time,
            )
            return False

    async def test_site_building(self) -> bool:
        """Test 5: Build static site with gallery functionality."""
        start_time = time.time()

        try:
            # Build the static site
            result = build_static_site(
                world_directory=str(self.world_directory), action="build"
            )

            if "successfully" in result:
                # Check if site was built
                site_dir = self.world_directory / "site"
                if site_dir.exists():
                    # Verify key files exist
                    required_files = ["index.html", "gallery/index.html"]

                    missing_files = [
                        f for f in required_files if not (site_dir / f).exists()
                    ]

                    if missing_files:
                        self.record_result(
                            "Site Building",
                            False,
                            f"Missing site files: {missing_files}",
                            time.time() - start_time,
                        )
                        return False

                    # Count generated pages
                    html_files = list(site_dir.rglob("*.html"))

                    self.record_result(
                        "Site Building",
                        True,
                        f"Built site with {len(html_files)} HTML pages",
                        time.time() - start_time,
                    )
                    return True
                else:
                    self.record_result(
                        "Site Building",
                        False,
                        "Site directory not created",
                        time.time() - start_time,
                    )
                    return False
            else:
                self.record_result(
                    "Site Building",
                    False,
                    f"Site building failed: {result}",
                    time.time() - start_time,
                )
                return False

        except Exception as e:
            self.record_result(
                "Site Building", False, f"Exception: {str(e)}", time.time() - start_time
            )
            return False

    async def test_content_validation(self) -> bool:
        """Test 6: Validate generated content structure and links."""
        start_time = time.time()

        try:
            site_dir = self.world_directory / "site"

            # Check homepage content
            index_file = site_dir / "index.html"
            if index_file.exists():
                content = index_file.read_text()

                # Check for gallery link
                if "gallery" not in content.lower():
                    self.record_result(
                        "Content Validation",
                        False,
                        "Gallery link not found in homepage",
                        time.time() - start_time,
                    )
                    return False

                # Check for character entry
                if "lyra" not in content.lower():
                    self.record_result(
                        "Content Validation",
                        False,
                        "Character entry not found in homepage",
                        time.time() - start_time,
                    )
                    return False

            # Check gallery functionality
            gallery_file = site_dir / "gallery" / "index.html"
            if gallery_file.exists():
                gallery_content = gallery_file.read_text()

                # Check for fullscreen functionality
                if "fullscreenmodal" not in gallery_content.lower():
                    self.record_result(
                        "Content Validation",
                        False,
                        "Fullscreen modal not found in gallery",
                        time.time() - start_time,
                    )
                    return False

                # Check for image references
                if "lyra-skyward" not in gallery_content.lower():
                    self.record_result(
                        "Content Validation",
                        False,
                        "Character image not found in gallery",
                        time.time() - start_time,
                    )
                    return False

            self.record_result(
                "Content Validation",
                True,
                "All content validation checks passed",
                time.time() - start_time,
            )
            return True

        except Exception as e:
            self.record_result(
                "Content Validation",
                False,
                f"Exception: {str(e)}",
                time.time() - start_time,
            )
            return False

    async def run_all_tests(self) -> Dict:
        """Run all end-to-end tests in sequence."""
        self.log("Starting end-to-end integration tests", "INFO")
        total_start = time.time()

        tests = [
            ("World Instantiation", self.test_world_instantiation),
            ("Taxonomy Guidelines", self.test_taxonomy_guidelines),
            ("Entry Creation", self.test_entry_creation),
            ("Image Generation", self.test_image_generation),
            ("Site Building", self.test_site_building),
            ("Content Validation", self.test_content_validation),
        ]

        overall_success = True

        for test_name, test_func in tests:
            self.log(f"Running {test_name}...", "INFO")
            success = await test_func()
            if not success:
                overall_success = False
                # Continue with remaining tests even if one fails

        total_duration = time.time() - total_start

        # Generate summary
        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)

        summary = {
            "overall_success": overall_success,
            "passed": passed,
            "total": total,
            "duration": total_duration,
            "world_directory": (
                str(self.world_directory) if self.world_directory else None
            ),
            "results": self.results,
        }

        self.log(
            f"Tests completed: {passed}/{total} passed in {total_duration:.2f}s",
            "SUCCESS" if overall_success else "ERROR",
        )

        return summary

    def cleanup_test_world(self):
        """Remove the test world directory."""
        if self.world_directory and self.world_directory.exists():
            shutil.rmtree(self.world_directory)
            self.log(f"Cleaned up test world: {self.world_directory}", "INFO")


async def main():
    """Main entry point for the integration test."""
    parser = argparse.ArgumentParser(description="Run end-to-end integration tests")
    parser.add_argument(
        "--cleanup", action="store_true", help="Clean up test world after completion"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--base-dir", default=".", help="Base directory for test world creation"
    )

    args = parser.parse_args()

    # Create test runner
    runner = E2ETestRunner(args.base_dir, args.verbose)

    try:
        # Run all tests
        summary = await runner.run_all_tests()

        # Print detailed results
        print("\n" + "=" * 60)
        print("END-TO-END INTEGRATION TEST RESULTS")
        print("=" * 60)

        for result in summary["results"]:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']:<25} ({result['duration']:.2f}s)")
            if result["message"]:
                print(f"     └─ {result['message']}")

        print("-" * 60)
        print(f"Overall: {summary['passed']}/{summary['total']} tests passed")
        print(f"Duration: {summary['duration']:.2f} seconds")

        if summary["world_directory"]:
            print(f"Test world: {summary['world_directory']}")

        # Cleanup if requested
        if args.cleanup:
            runner.cleanup_test_world()

        # Exit with appropriate code
        sys.exit(0 if summary["overall_success"] else 1)

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        if args.cleanup:
            runner.cleanup_test_world()
        sys.exit(1)
    except Exception as e:
        print(f"Test runner error: {e}")
        if args.cleanup:
            runner.cleanup_test_world()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
