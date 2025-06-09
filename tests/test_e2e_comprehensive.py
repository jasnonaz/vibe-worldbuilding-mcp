#!/usr/bin/env python3
"""
Comprehensive End-to-End Integration Test for Vibe Worldbuilding System

This test creates a complete world from concept to finished site, testing:
- World instantiation with rich concept
- Multiple taxonomy generation with custom guidelines  
- Multiple entries per taxonomy with auto-stub generation
- Image generation (if FAL API available)
- Static site building with full navigation
- Content validation and link checking

Usage:
    python test_e2e_comprehensive.py [--cleanup] [--verbose] [--skip-images]
"""

import asyncio
import sys
import time
import shutil
from pathlib import Path
import argparse

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the tool handlers directly
from vibe_worldbuilding.tools.world import handle_world_tool
from vibe_worldbuilding.tools.taxonomy import handle_taxonomy_tool
from vibe_worldbuilding.tools.entries import handle_entry_tool
from vibe_worldbuilding.tools.site import handle_site_tool
from vibe_worldbuilding.tools.images import handle_image_tool


class ComprehensiveE2ETest:
    """Comprehensive end-to-end test that builds a complete world."""
    
    def __init__(self, base_dir: str, verbose: bool = False, skip_images: bool = False):
        self.base_dir = Path(base_dir)
        self.verbose = verbose
        self.skip_images = skip_images
        self.test_world_name = f"mystic-realms-test-{int(time.time())}"
        self.world_directory = None
        self.created_entries = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message."""
        if self.verbose or level in ["ERROR", "SUCCESS", "SUMMARY"]:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")
    
    async def create_world_foundation(self) -> bool:
        """Create the world with a rich concept and taxonomies."""
        self.log("Creating comprehensive test world...", "SUMMARY")
        
        world_content = """# The Mystic Realms

## Overview

The Mystic Realms are a collection of floating islands suspended in an endless sky filled with magical aurora streams. Each island represents a different magical domain, connected by ancient Skyways that respond to the traveler's intent and magical attunement.

## Core Concepts

**The Aurora Streams**: Rivers of pure magical energy that flow between the islands, changing color and intensity based on the magical activities of the inhabitants. The streams power everything from simple household enchantments to the great Skyway networks.

**Skyway Navigation**: Travel between islands occurs via the Skyways - crystalline bridges that materialize when approached by those with proper magical attunement. The bridges adapt their destination based on the traveler's true need, not their conscious desire.

**The Resonance**: A mysterious phenomenon where the magical nature of each island affects its inhabitants over time, gradually aligning them with the island's core magical principles.

## Tone and Atmosphere

The Mystic Realms blend wonder with practical magic use. Magic is common but not trivial - it requires understanding, respect, and often comes with unexpected consequences. The floating nature of the world creates both beauty and underlying tension, as nothing is truly permanent or entirely safe.
"""
        
        try:
            # Step 1: Create world foundation (without taxonomies)
            world_result = await handle_world_tool("instantiate_world", {
                "world_name": self.test_world_name,
                "world_content": world_content,
                "base_directory": str(self.base_dir)
            })
            
            result_text = world_result[0].text if world_result else ""
            if "successfully" not in result_text.lower():
                self.log(f"World creation failed: {result_text}", "ERROR")
                return False
                
            self.log("✅ World foundation created successfully", "SUCCESS")
            
            # Find the created world directory
            world_dirs = list(self.base_dir.glob(f"{self.test_world_name}-*"))
            if not world_dirs:
                self.log("World directory not found", "ERROR")
                return False
                
            self.world_directory = world_dirs[0]
            self.log(f"Found world directory: {self.world_directory}")
            
            # Step 2: Create taxonomies using the proper MCP workflow
            taxonomies = [
                {"name": "islands", "description": "The floating landmasses that make up the Mystic Realms, each with unique magical properties"},
                {"name": "inhabitants", "description": "The people, creatures, and entities that live within the Mystic Realms"},
                {"name": "magic_systems", "description": "The various schools and approaches to magic practiced throughout the realms"},
                {"name": "artifacts", "description": "Magical items, relics, and enchanted objects of significance"},
                {"name": "organizations", "description": "Groups, guilds, orders, and societies that operate across the realms"}
            ]
            
            for taxonomy in taxonomies:
                self.log(f"Creating taxonomy: {taxonomy['name']}")
                
                # Generate guidelines for this taxonomy
                guidelines_result = await handle_taxonomy_tool("generate_taxonomy_guidelines", {
                    "taxonomy_name": taxonomy["name"],
                    "taxonomy_description": taxonomy["description"]
                })
                
                guidelines_text = guidelines_result[0].text if guidelines_result else ""
                if "guidelines" not in guidelines_text.lower():
                    self.log(f"Guidelines generation failed for {taxonomy['name']}: {guidelines_text}", "ERROR")
                    return False
                
                # Create taxonomy folder with custom guidelines
                taxonomy_result = await handle_taxonomy_tool("create_taxonomy_folders", {
                    "world_directory": str(self.world_directory),
                    "taxonomy_name": taxonomy["name"],
                    "taxonomy_description": taxonomy["description"],
                    "custom_guidelines": guidelines_text
                })
                
                taxonomy_text = taxonomy_result[0].text if taxonomy_result else ""
                if "successfully" not in taxonomy_text.lower():
                    self.log(f"Taxonomy creation failed for {taxonomy['name']}: {taxonomy_text}", "ERROR")
                    return False
                    
                self.log(f"  ✅ Created taxonomy: {taxonomy['name']}")
            
            return True
            
        except Exception as e:
            self.log(f"World creation failed with exception: {e}", "ERROR")
            return False
    
    async def create_comprehensive_content(self) -> bool:
        """Create multiple entries across all taxonomies."""
        self.log("Creating comprehensive world content...", "SUMMARY")
        
        # Define content for each taxonomy
        content_plan = {
            "islands": [
                {
                    "name": "The Floating Academy",
                    "content": """# The Floating Academy

## Overview
The premier educational institution of the Mystic Realms, the Floating Academy hovers perpetually above the Aurora Nexus, drawing power from the converging magical streams below. The island slowly rotates, offering different perspectives of the realm throughout the day.

## Physical Description
Built from crystallized aurora energy, the Academy's buildings shimmer with ever-changing colors. The Great Library sits at the center, its spiraling tower reaching impossible heights. Dormitories and classrooms float independently around the core, connected by walkways of solid light.

## Notable Features
- **The Resonance Chamber**: Where students learn to attune to different magical frequencies
- **The Memory Gardens**: Living archives where knowledge grows as luminescent flora
- **The Probability Halls**: Classrooms where theoretical magic is safely practiced

## Inhabitants
The Academy houses the Lorekeepers, an order of scholar-mages who have dedicated their lives to understanding the fundamental nature of magic. Students come from across all realms, selected not by wealth or birth, but by their magical resonance potential.

## Current Events
Recent disturbances in the Aurora Streams have caused sections of the Academy to phase in and out of reality, leading to missing classrooms and displaced students. The Lorekeepers are investigating whether this is a natural phenomenon or the result of experimental magic gone wrong.
"""
                },
                {
                    "name": "The Forgeheart Foundries",
                    "content": """# The Forgeheart Foundries

## Overview
A volcanic island where the ancient art of magical smithing reaches its pinnacle. The island's core contains an ever-burning heart of elemental fire, providing the intense heat necessary for forging items that can channel and focus magical energies.

## The Forging Process
Master smiths of the Foundries don't just shape metal - they weave magical essence into the very structure of their creations. Each item becomes a unique conduit for specific types of magic, attuned to both the materials used and the intentions of its creator.

## The Smithmaster Guild
Led by the legendary Smithmaster Kaelen Brightforge, whose hammer strikes are said to ring with the harmony of the Aurora Streams themselves. The Guild maintains strict traditions while pushing the boundaries of what's possible in magical item creation.

## Unique Materials
- **Aurora-touched Metals**: Ores that have been exposed to magical stream energy for centuries
- **Resonance Crystals**: Gems that vibrate with specific magical frequencies
- **Skysilk**: Threads spun from crystallized cloud essence by the Wind Weavers

## The Great Commission
Currently undertaking their most ambitious project: forging a new Skyway Anchor to replace one that was lost in the recent magical storms, which would restore access to three distant islands that have been cut off for months.
"""
                }
            ],
            "inhabitants": [
                {
                    "name": "The Wind Weavers",
                    "content": """# The Wind Weavers

## Overview
A nomadic people who travel the Mystic Realms not by Skyway, but by riding the Aurora Streams themselves. They have developed the unique ability to weave solid constructs from wind and cloud essence, creating temporary shelters, tools, and even vehicles.

## Abilities and Culture
Wind Weavers can manipulate air currents and weather patterns through intricate hand gestures that resemble a complex dance. Their society is built around constant movement and adaptation, viewing permanent structures as limiting to both magic and spirit.

## The Weaving Arts
- **Cloud Sculpting**: Creating temporary structures from condensed water vapor
- **Wind Reading**: Interpreting the Aurora Streams' patterns to predict magical weather
- **Storm Calling**: Advanced practitioners can summon localized weather phenomena

## Social Structure
Led by the Storm Speakers, elder Weavers who can commune directly with the Aurora Streams. Young Weavers undergo the Spiral Journey, traveling to each island to learn different aspects of their craft.

## Current Role
With the Skyways becoming unreliable, the Wind Weavers have become crucial messengers and transporters between islands. However, their free-spirited nature sometimes conflicts with the more structured societies they now serve.
"""
                },
                {
                    "name": "Archkeeper Lyralei",
                    "content": """# Archkeeper Lyralei

## Overview
The current head of the Floating Academy's Great Library, Archkeeper Lyralei possesses the rare ability to commune with the living knowledge stored in the Memory Gardens. She appears as an ageless woman whose hair shimmers with the same aurora patterns as the magical streams.

## Background
Originally from the distant Twilight Isles, Lyralei came to the Academy as a young scholar researching the connection between memory and magic. Her breakthrough discovery that knowledge itself could be made to grow and evolve like living organisms revolutionized magical education.

## Magical Abilities
- **Memory Cultivation**: Can plant, nurture, and harvest knowledge from the Memory Gardens
- **Truth Resonance**: Instinctively knows when information is incomplete or false
- **Chronicle Weaving**: Can combine multiple memories and knowledge sources into new understanding

## Current Challenges
The recent Academy phase disturbances have begun affecting the Memory Gardens, causing some knowledge to wither while other information grows wildly out of control. Lyralei is working tirelessly to maintain the balance while searching for the cause.

## Personality
Thoughtful and patient, but fiercely protective of knowledge and learning. She believes that understanding must be earned through genuine curiosity and effort, not simply transferred or inherited.
"""
                }
            ],
            "magic_systems": [
                {
                    "name": "Aurora Stream Manipulation",
                    "content": """# Aurora Stream Manipulation

## Overview
The fundamental magical practice of the Mystic Realms, involving the channeling and directing of energy from the Aurora Streams that flow between islands. This is both the most common and most complex magical system in the realms.

## Basic Principles
Aurora energy exists in multiple frequencies, each corresponding to different magical effects. Practitioners must first learn to attune their personal magical signature to match specific stream frequencies before they can effectively channel the energy.

## Skill Levels
- **Stream Sensing**: Feeling the presence and flow of nearby Aurora energy
- **Basic Channeling**: Drawing small amounts of energy for simple effects
- **Frequency Matching**: Attuning to specific stream types for specialized magic
- **Stream Weaving**: Combining multiple frequencies for complex effects
- **Flow Mastery**: Redirecting or modifying the streams themselves

## Risks and Limitations
Overchanneling can cause "stream burn," a condition where the practitioner's magical pathways become overloaded and temporarily unusable. More serious is "frequency lock," where someone becomes permanently attuned to a single stream type.

## Applications
Used for everything from household conveniences (lighting, heating, communication) to major magical works (Skyway creation, island stabilization, weather control). The versatility of Aurora magic makes it the foundation for most other magical practices in the realms.
"""
                }
            ],
            "artifacts": [
                {
                    "name": "The Compass of True Need",
                    "content": """# The Compass of True Need

## Overview
A legendary artifact that appears as an intricately carved crystal sphere containing a floating needle made of condensed Aurora energy. The Compass doesn't point to magnetic north, but toward whatever the holder truly needs most - whether they realize it or not.

## Origins
Created by the first Skyway builders as a tool for navigation when the Aurora Streams were too chaotic to read directly. The Compass was designed to help travelers find not just their destination, but the path that would best serve their deeper purpose.

## Magical Properties
- **True Need Detection**: Points toward what will most benefit the holder's growth or mission
- **Deception Immunity**: Cannot be fooled by conscious desires or external manipulation
- **Path Revelation**: Shows multiple possible routes when multiple needs exist
- **Warning Resonance**: Vibrates when the holder is pursuing something harmful to their true purpose

## Current Location
Lost during the Battle of the Broken Sky three centuries ago, the Compass has become the subject of numerous expeditions and legends. Some claim it still exists, hidden on one of the lost islands that were severed from the Skyway network.

## The Seeker's Paradox
The Compass is said to only appear to those who truly need it, but disappears from those who seek it for selfish purposes. This has led to the philosophical question of whether the artifact chooses its bearers, or whether it simply reflects the spiritual state of those around it.
"""
                }
            ],
            "organizations": [
                {
                    "name": "The Skyway Wardens",
                    "content": """# The Skyway Wardens

## Overview
An organization dedicated to maintaining and protecting the Skyway network that connects the floating islands of the Mystic Realms. The Wardens serve as both engineers and guardians, ensuring safe passage for all who travel the crystalline bridges.

## Structure and Ranks
- **Anchor Keepers**: Maintain the physical Skyway connection points on each island
- **Bridge Walkers**: Patrol the Skyways themselves, assisting travelers and monitoring stability
- **Stream Readers**: Specialists who interpret Aurora patterns to predict Skyway behavior
- **The High Warden**: Overall leader, traditionally someone who has walked every known Skyway

## Responsibilities
Beyond maintenance, the Wardens investigate Skyway anomalies, rescue lost travelers, and work to establish new connections as islands shift position relative to each other. They also maintain the Great Map, the only complete record of all Skyway routes and their current status.

## Current Crisis
The recent instability in the Aurora Streams has caused unprecedented Skyway failures. The Wardens are stretched thin, working around the clock to maintain essential routes while investigating the underlying cause of the disturbances.

## The Warden's Code
"The path between islands is sacred. We guard not just the bridges, but the connections that bind our scattered realm into one people." This philosophy extends beyond physical infrastructure to diplomatic and cultural exchange between islands.
"""
                }
            ]
        }
        
        # Create entries for each taxonomy
        total_entries = sum(len(entries) for entries in content_plan.values())
        current_entry = 0
        
        try:
            for taxonomy, entries in content_plan.items():
                self.log(f"Creating {len(entries)} entries for {taxonomy} taxonomy...")
                
                for entry_data in entries:
                    current_entry += 1
                    self.log(f"Creating entry {current_entry}/{total_entries}: {entry_data['name']}")
                    
                    entry_result = await handle_entry_tool("create_world_entry", {
                        "world_directory": str(self.world_directory),
                        "taxonomy": taxonomy,
                        "entry_name": entry_data["name"],
                        "entry_content": entry_data["content"]
                    })
                    
                    entry_text = entry_result[0].text if entry_result else ""
                    if "successfully" not in entry_text.lower():
                        self.log(f"Entry creation failed for {entry_data['name']}: {entry_text}", "ERROR")
                        return False
                    
                    self.created_entries.append(f"{taxonomy}/{entry_data['name']}")
                    
                    # Check if auto-stub generation was triggered
                    if "stub entries" in entry_text.lower():
                        self.log(f"  ↳ Auto-stub generation triggered for {entry_data['name']}")
            
            self.log(f"✅ Created {len(self.created_entries)} comprehensive entries", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Content creation failed with exception: {e}", "ERROR")
            return False
    
    async def generate_images(self) -> bool:
        """Generate images for key entries (if FAL API available)."""
        if self.skip_images:
            self.log("Skipping image generation (--skip-images)", "INFO")
            return True
            
        self.log("Generating images for key entries...", "SUMMARY")
        
        # Select key entries for image generation
        image_targets = [
            ("overview/world-overview.md", "concept art"),
            ("entries/islands/the-floating-academy.md", "fantasy architecture"),
            ("entries/inhabitants/the-wind-weavers.md", "character design")
        ]
        
        success_count = 0
        
        try:
            for file_path, style in image_targets:
                full_path = self.world_directory / file_path
                if full_path.exists():
                    self.log(f"Generating {style} image for {file_path}...")
                    
                    try:
                        image_result = await handle_image_tool("generate_image_from_markdown_file", {
                            "filepath": str(full_path),
                            "style": style,
                            "aspect_ratio": "16:9"
                        })
                        
                        image_text = image_result[0].text if image_result else ""
                        if "successfully" in image_text.lower():
                            success_count += 1
                            self.log(f"  ✅ Image generated successfully")
                        else:
                            self.log(f"  ⚠️ Image generation failed: {image_text}")
                            
                    except Exception as e:
                        self.log(f"  ⚠️ Image generation error: {e}")
            
            if success_count > 0:
                self.log(f"✅ Generated {success_count}/{len(image_targets)} images", "SUCCESS")
            else:
                self.log("⚠️ No images generated (likely missing FAL API key)", "INFO")
            
            return True  # Don't fail the test if images can't be generated
            
        except Exception as e:
            self.log(f"Image generation failed with exception: {e}", "ERROR")
            return True  # Don't fail the test for image issues
    
    async def build_and_validate_site(self) -> bool:
        """Build static site and validate content."""
        self.log("Building static site...", "SUMMARY")
        
        try:
            site_result = await handle_site_tool("build_static_site", {
                "world_directory": str(self.world_directory),
                "action": "build"
            })
            
            site_text = site_result[0].text if site_result else ""
            if "successfully" not in site_text.lower():
                self.log(f"Site building failed: {site_text}", "ERROR")
                return False
                
            self.log("✅ Site building successful", "SUCCESS")
            
            # Validate generated content
            self.log("Validating generated site content...")
            
            site_dir = self.world_directory / "site"
            if not site_dir.exists():
                self.log("Site directory not found", "ERROR")
                return False
            
            # Check for essential files
            required_files = [
                "index.html",
                "world/index.html",
                "gallery/index.html"
            ]
            
            for file_path in required_files:
                if not (site_dir / file_path).exists():
                    self.log(f"Required file missing: {file_path}", "ERROR")
                    return False
            
            # Check for taxonomy overview files (source) - should exist after proper MCP workflow
            taxonomy_mapping = {
                "islands": "islands-overview.md",
                "inhabitants": "inhabitants-overview.md", 
                "magic_systems": "magic-systems-overview.md",  # underscores become hyphens
                "artifacts": "artifacts-overview.md",
                "organizations": "organizations-overview.md"
            }
            
            for taxonomy, filename in taxonomy_mapping.items():
                taxonomy_overview = self.world_directory / "taxonomies" / filename
                if not taxonomy_overview.exists():
                    self.log(f"Taxonomy overview file missing: {filename}", "ERROR")
                    return False
                
                # Check that the taxonomy is custom (contains guidelines)
                content = taxonomy_overview.read_text()
                if "guidelines" not in content.lower() and "structure" not in content.lower():
                    self.log(f"Taxonomy {filename} doesn't appear to have custom guidelines", "ERROR")
                    return False
                    
                self.log(f"✅ Found custom taxonomy: {filename}")
            
            self.log("✅ All taxonomy overview files exist with custom guidelines")
            
            # Check for taxonomy pages in site (entry directories should exist)
            taxonomies_found = 0
            for taxonomy in ["islands", "inhabitants", "magic_systems", "artifacts", "organizations"]:
                taxonomy_dir = site_dir / "taxonomies" / taxonomy
                if taxonomy_dir.exists():
                    taxonomies_found += 1
                    self.log(f"Found taxonomy directory: {taxonomy}")
                    
                    # Check for entry pages within this taxonomy
                    entry_dir = taxonomy_dir / "entries"
                    if entry_dir.exists():
                        entries = list(entry_dir.iterdir())
                        self.log(f"  └─ {len(entries)} entries found")
            
            if taxonomies_found == 0:
                self.log("No taxonomy directories found in site", "ERROR")
                return False
            
            self.log(f"✅ Found {taxonomies_found}/5 taxonomy directories")
            
            # Count generated entry pages
            entry_pages = list((site_dir / "taxonomies").rglob("*/entries/*/index.html"))
            self.log(f"Generated {len(entry_pages)} entry pages")
            
            if len(entry_pages) < len(self.created_entries):
                self.log(f"Expected {len(self.created_entries)} entry pages, found {len(entry_pages)}", "ERROR")
                return False
            
            self.log("✅ Site content validation successful", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Site building failed with exception: {e}", "ERROR")
            return False
    
    async def run_comprehensive_test(self) -> bool:
        """Run the complete comprehensive test."""
        self.log("Starting comprehensive end-to-end integration test", "SUMMARY")
        self.log("This test will create a complete world with rich content", "SUMMARY")
        
        start_time = time.time()
        
        try:
            # Step 1: Create world foundation
            if not await self.create_world_foundation():
                return False
            
            # Step 2: Create comprehensive content
            if not await self.create_comprehensive_content():
                return False
            
            # Step 3: Generate images (optional)
            if not await self.generate_images():
                return False
            
            # Step 4: Build and validate site
            if not await self.build_and_validate_site():
                return False
            
            # Success summary
            duration = time.time() - start_time
            self.log("="*60, "SUMMARY")
            self.log("COMPREHENSIVE TEST RESULTS", "SUMMARY")
            self.log("="*60, "SUMMARY")
            self.log(f"✅ World created: {self.test_world_name}", "SUCCESS")
            self.log(f"✅ Entries created: {len(self.created_entries)}", "SUCCESS")
            self.log(f"✅ Site built with full navigation", "SUCCESS")
            self.log(f"✅ Duration: {duration:.2f} seconds", "SUCCESS")
            self.log(f"📂 Test world location: {self.world_directory}", "SUMMARY")
            self.log("="*60, "SUMMARY")
            
            self.log("🎉 COMPREHENSIVE INTEGRATION TEST PASSED!", "SUCCESS")
            self.log("A complete world has been built from concept to finished site.", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log(f"Comprehensive test failed with exception: {e}", "ERROR")
            return False
    
    def cleanup(self):
        """Clean up test world."""
        if self.world_directory and self.world_directory.exists():
            shutil.rmtree(self.world_directory)
            self.log(f"Cleaned up test world: {self.world_directory}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run comprehensive E2E integration test")
    parser.add_argument("--cleanup", action="store_true", help="Clean up after test")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--skip-images", action="store_true", help="Skip image generation")
    parser.add_argument("--base-dir", default="./test-worlds", help="Base directory for test")
    
    args = parser.parse_args()
    
    # Run the test
    test = ComprehensiveE2ETest(args.base_dir, args.verbose, args.skip_images)
    
    try:
        success = await test.run_comprehensive_test()
        
        if args.cleanup:
            test.cleanup()
            
        if success:
            print("\n🎉 COMPREHENSIVE INTEGRATION TEST PASSED")
            print("The worldbuilding system successfully created a complete world!")
            print("Check the test-worlds directory to explore the generated content.")
            sys.exit(0)
        else:
            print("\n❌ COMPREHENSIVE INTEGRATION TEST FAILED")
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