"""Consistency analysis and improvement module for the Vibe Worldbuilding MCP.

This module provides tools for analyzing multiple world entries to identify
consistency issues and apply improvements. It follows the LLM-first design
principle by outsourcing the actual consistency analysis to the client LLM.
"""

import random
from pathlib import Path
from typing import Any, Dict, List

import mcp.types as types

from ..config import MARKDOWN_EXTENSION


async def analyze_world_consistency(
    arguments: dict[str, Any] | None,
) -> list[types.TextContent]:
    """Analyze multiple entries for consistency issues.

    This tool loads multiple world entries and presents them to the client LLM
    for consistency analysis. The LLM identifies inconsistencies, missing
    connections, and opportunities for improvement.

    Args:
        arguments: Tool arguments containing:
            - world_directory: Path to the world directory
            - entry_count: Number of entries to analyze (default: 15)

    Returns:
        List containing analysis prompt for the client LLM with entry content
        and instructions for consistency analysis
    """
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]

    world_directory = arguments.get("world_directory", "")
    entry_count = arguments.get("entry_count", 15)

    if not world_directory:
        return [
            types.TextContent(type="text", text="Error: world_directory is required")
        ]

    try:
        world_path = Path(world_directory)
        if not world_path.exists():
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: World directory {world_directory} does not exist",
                )
            ]

        entries_path = world_path / "entries"
        if not entries_path.exists():
            return [types.TextContent(type="text", text="No entries directory found")]

        # Collect all available entries
        all_entries = []
        for taxonomy_dir in entries_path.iterdir():
            if taxonomy_dir.is_dir():
                for entry_file in taxonomy_dir.glob(f"*{MARKDOWN_EXTENSION}"):
                    all_entries.append(
                        {
                            "taxonomy": taxonomy_dir.name,
                            "file": entry_file,
                            "name": entry_file.stem.replace("-", " ").title(),
                        }
                    )

        if not all_entries:
            return [types.TextContent(type="text", text="No entries found to analyze")]

        # Select random entries for analysis
        selected_entries = random.sample(
            all_entries, min(entry_count, len(all_entries))
        )

        # Load entry content
        entries_content = []
        for entry in selected_entries:
            try:
                with open(entry["file"], "r", encoding="utf-8") as f:
                    content = f.read()
                entries_content.append(
                    {
                        "taxonomy": entry["taxonomy"],
                        "name": entry["name"],
                        "path": str(entry["file"]),
                        "content": content,
                    }
                )
            except Exception as e:
                continue

        if not entries_content:
            return [
                types.TextContent(
                    type="text", text="Error: Could not load any entry content"
                )
            ]

        # Create analysis prompt
        prompt = _create_consistency_analysis_prompt(entries_content)

        return [types.TextContent(type="text", text=prompt)]

    except Exception as e:
        return [
            types.TextContent(
                type="text", text=f"Error analyzing world consistency: {str(e)}"
            )
        ]


def _create_consistency_analysis_prompt(entries: List[Dict]) -> str:
    """Create a comprehensive prompt for LLM consistency analysis."""
    prompt = f"""# World Consistency Analysis

## Task
Analyze the following {len(entries)} world entries for consistency issues and opportunities to improve connections between entries.

## Entries to Analyze

"""

    for entry in entries:
        prompt += f"""### {entry['name']} ({entry['taxonomy']})
**File**: {entry['path']}

{entry['content']}

---

"""

    prompt += """## Analysis Instructions

Please analyze these entries and identify:

1. **Inconsistencies**
   - Names mentioned differently across entries
   - Contradictory facts or descriptions
   - Timeline conflicts

2. **Missing Connections**
   - Characters/places/things mentioned but not linked
   - Obvious relationships that aren't stated
   - Events that should connect multiple entries

3. **Enhancement Opportunities**
   - Places to add cross-references
   - Details that would strengthen the world
   - Consistency improvements

## Output Format

For each issue or opportunity found, please provide:
- **File to edit**: Full path to the file
- **Current text**: The exact text that needs changing
- **New text**: What to replace it with
- **Reason**: Brief explanation of why this improves consistency

Please use the Edit or MultiEdit tools to apply these changes."""

    return prompt
