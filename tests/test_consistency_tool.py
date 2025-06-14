#!/usr/bin/env python3
"""
Test script for the World Consistency Analysis Tool

This test creates a small world with intentional inconsistencies
and then uses the analyze_world_consistency tool to detect them.
"""

import asyncio
import shutil
import sys
import time
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vibe_worldbuilding.tools.entries import handle_entry_tool
from vibe_worldbuilding.tools.taxonomy import handle_taxonomy_tool

# Import the tool handlers directly
from vibe_worldbuilding.tools.world import handle_world_tool


async def test_consistency_analysis():
    """Test the consistency analysis tool with a small world."""

    test_world_name = f"consistency-test-{int(time.time())}"
    base_dir = Path(__file__).parent / "test-worlds"
    base_dir.mkdir(exist_ok=True)

    print(f"Creating test world: {test_world_name}")

    try:
        # 1. Create a world
        result = await handle_world_tool(
            "instantiate_world",
            {
                "world_name": test_world_name,
                "world_content": """# The Realm of Echoing Shadows

A mystical realm where shadow magic and elemental forces collide. The realm is ruled by the Shadow Council from their fortress in Umbral City.""",
                "base_directory": str(base_dir),
                "taxonomies": [
                    {
                        "name": "Characters",
                        "description": "Important figures in the realm",
                    },
                    {"name": "Locations", "description": "Notable places and regions"},
                ],
            },
        )

        # Extract world directory from result
        world_directory = None
        for content in result:
            if "Full path:" in content.text:
                # Extract the path from the line that contains "Full path: /path/to/world"
                lines = content.text.split("\n")
                for line in lines:
                    if line.startswith("Full path:"):
                        world_directory = line.replace("Full path:", "").strip()
                        break
                break

        if not world_directory:
            raise Exception("Could not determine world directory")

        print(f"World created at: {world_directory}")

        # 2. Create entries with intentional inconsistencies

        # Entry 1: Character with a name
        await handle_entry_tool(
            "create_world_entry",
            {
                "world_directory": world_directory,
                "taxonomy": "Characters",
                "entry_name": "Lord Shadowbane",
                "entry_content": """# Lord Shadowbane

Lord Shadowbane is the leader of the Shadow Council and the most powerful shadow mage in the realm. He rules from his throne in Umbra City, commanding the shadow guards with an iron fist.

His apprentice, Lyra Nightwhisper, serves as his right hand and enforcer of his will throughout the kingdom.""",
            },
        )

        # Entry 2: Location mentioning the character differently
        await handle_entry_tool(
            "create_world_entry",
            {
                "world_directory": world_directory,
                "taxonomy": "Locations",
                "entry_name": "Umbral City",
                "entry_content": """# Umbral City

The capital of the shadow realm, Umbral City is a metropolis of perpetual twilight. At its heart stands the Obsidian Citadel, where Lord Shadowsbane holds court.

The city is protected by the elite Shadow Guards, who report directly to Lira Nightwhisper, the Lord's trusted apprentice.""",
            },
        )

        # Entry 3: Another character with timeline conflict
        await handle_entry_tool(
            "create_world_entry",
            {
                "world_directory": world_directory,
                "taxonomy": "Characters",
                "entry_name": "Lyra Nightwhisper",
                "entry_content": """# Lyra Nightwhisper

A young shadow mage who rose to prominence after defeating the ancient dragon Pyrax in the year 1247. She became Lord Shadowbane's apprentice in 1250 and quickly proved herself invaluable.

She commands the Shadow Guards from her tower in Umbral City, which was built in 1245.""",
            },
        )

        print("\nEntries created with intentional inconsistencies:")
        print("- 'Lord Shadowsbane' vs 'Lord Shadowbane' (spelling)")
        print("- 'Lira Nightwhisper' vs 'Lyra Nightwhisper' (spelling)")
        print(
            "- Timeline conflict: Tower built in 1245, but Lyra defeated dragon in 1247"
        )

        # 3. Run consistency analysis
        print("\nRunning consistency analysis...")
        analysis_result = await handle_entry_tool(
            "analyze_world_consistency",
            {
                "world_directory": world_directory,
                "entry_count": 10,
            },
        )

        # Print the analysis prompt that would be sent to the LLM
        print("\n" + "=" * 80)
        print("CONSISTENCY ANALYSIS PROMPT:")
        print("=" * 80)
        for content in analysis_result:
            print(content.text)

        print("\n✅ Consistency analysis tool executed successfully!")
        print("\nThe tool has generated a prompt that would be sent to the client LLM")
        print(
            "for analysis. The LLM would identify the inconsistencies and suggest fixes."
        )

        return True

    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Cleanup
        if "world_directory" in locals() and world_directory:
            world_path = Path(world_directory)
            if world_path.exists():
                print(f"\nCleaning up test world: {world_path}")
                shutil.rmtree(world_path)


if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_consistency_analysis())
    sys.exit(0 if success else 1)
