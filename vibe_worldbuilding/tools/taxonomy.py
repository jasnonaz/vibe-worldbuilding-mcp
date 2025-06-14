"""Taxonomy management tools for the Vibe Worldbuilding MCP.

This module handles the creation and management of taxonomies, which are
classification systems for organizing world elements into categories.
"""

from pathlib import Path
from typing import Any

import mcp.types as types

from ..config import (
    FAL_API_KEY,
    FAL_API_URL,
    FAL_AVAILABLE,
    IMAGE_EXTENSION,
    MARKDOWN_EXTENSION,
    TAXONOMY_OVERVIEW_SUFFIX,
)

if FAL_AVAILABLE:
    import requests


async def create_taxonomy_with_llm_guidelines(arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Create a taxonomy with LLM-generated guidelines in a single streamlined workflow.
    
    This tool presents the guidelines generation prompt to the LLM and waits for 
    the guidelines response in the same conversation flow, then creates the taxonomy.
    
    Args:
        arguments: Tool arguments containing world_directory, taxonomy_name, taxonomy_description, and llm_generated_guidelines
        
    Returns:
        List containing either guidelines prompt OR creation confirmation
    """
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]

    world_directory = arguments.get("world_directory", "")
    taxonomy_name = arguments.get("taxonomy_name", "")
    taxonomy_description = arguments.get("taxonomy_description", "")
    llm_generated_guidelines = arguments.get("llm_generated_guidelines", "")

    if not all([world_directory, taxonomy_name, taxonomy_description]):
        return [
            types.TextContent(
                type="text",
                text="Error: world_directory, taxonomy_name, and taxonomy_description are required",
            )
        ]

    # If no LLM guidelines provided, return prompt for LLM to generate them
    if not llm_generated_guidelines.strip():
        guidelines_prompt = _create_guidelines_prompt(taxonomy_name, taxonomy_description)
        
        return [types.TextContent(type="text", text=f"""{guidelines_prompt}

**Next Step:** After you generate the guidelines above, call this tool again with the same parameters plus your generated guidelines in the `llm_generated_guidelines` parameter to create the taxonomy.""")]

    # Otherwise, create the taxonomy with the LLM-generated guidelines
    return await _create_taxonomy_structure(
        world_directory, taxonomy_name, taxonomy_description, llm_generated_guidelines
    )


async def create_taxonomy(arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Create a taxonomy with LLM-generated guidelines.

    This function either:
    1. When called without custom_guidelines: Creates a prompt for the LLM to generate guidelines
    2. When called with custom_guidelines: Creates the actual taxonomy structure with those guidelines

    Args:
        arguments: Tool arguments containing world_directory, taxonomy_name, taxonomy_description, and optional custom_guidelines

    Returns:
        List containing either guidelines prompt or creation confirmation
    """
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]

    world_directory = arguments.get("world_directory", "")
    taxonomy_name = arguments.get("taxonomy_name", "")
    taxonomy_description = arguments.get("taxonomy_description", "")
    custom_guidelines = arguments.get("custom_guidelines", "")

    if not all([world_directory, taxonomy_name, taxonomy_description]):
        return [
            types.TextContent(
                type="text",
                text="Error: world_directory, taxonomy_name, and taxonomy_description are required",
            )
        ]

    # If no guidelines provided, return prompt for LLM to generate them
    if not custom_guidelines.strip():
        guidelines_prompt = _create_guidelines_prompt(
            taxonomy_name, taxonomy_description
        )
        return [types.TextContent(type="text", text=guidelines_prompt)]

    # Otherwise, create the taxonomy with the provided guidelines
    return await _create_taxonomy_structure(
        world_directory, taxonomy_name, taxonomy_description, custom_guidelines
    )


async def _create_taxonomy_structure(
    world_directory: str,
    taxonomy_name: str,
    taxonomy_description: str,
    custom_guidelines: str,
) -> list[types.TextContent]:
    """Create the actual taxonomy structure with guidelines.

    Args:
        world_directory: Path to the world directory
        taxonomy_name: Name of the taxonomy
        taxonomy_description: Description of the taxonomy
        custom_guidelines: LLM-generated guidelines for the taxonomy

    Returns:
        List containing success message with created taxonomy details
    """
    try:
        world_path = Path(world_directory)
        if not world_path.exists():
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: World directory {world_directory} does not exist",
                )
            ]

        # Clean taxonomy name for file system use
        clean_taxonomy_name = taxonomy_name.lower().replace(" ", "-").replace("_", "-")

        # Create taxonomies directory
        taxonomies_dir = world_path / "taxonomies"
        taxonomies_dir.mkdir(exist_ok=True)

        # Create entries directory for this taxonomy
        entries_dir = world_path / "entries" / clean_taxonomy_name
        entries_dir.mkdir(parents=True, exist_ok=True)

        # Create taxonomy overview file
        taxonomy_overview_path = (
            taxonomies_dir
            / f"{clean_taxonomy_name}{TAXONOMY_OVERVIEW_SUFFIX}{MARKDOWN_EXTENSION}"
        )

        # Build the complete taxonomy overview content
        overview_content = f"""# {taxonomy_name.title()} - Taxonomy Overview

## Description
{taxonomy_description}

{custom_guidelines}

## Writing Philosophy
These guidelines serve as flexible frameworks rather than rigid templates. Each entry should be crafted to tell its unique story while maintaining consistency with the world's established tone and feel. Prioritize engaging, immersive writing that brings each element to life through vivid details, interesting perspectives, and natural connections to other world elements.
"""

        with open(taxonomy_overview_path, "w", encoding="utf-8") as f:
            f.write(overview_content)

        # Create response
        relative_overview_path = str(taxonomy_overview_path.relative_to(world_path))
        relative_entries_path = str(entries_dir.relative_to(world_path))

        return [
            types.TextContent(
                type="text",
                text=f"Successfully created taxonomy '{taxonomy_name}'!\n\nCreated files:\n- Overview: {relative_overview_path}\n- Entries directory: {relative_entries_path}\n\nThe taxonomy is now ready for creating entries. Use the create_world_entry tool to add specific {taxonomy_name.lower()} entries.",
            )
        ]

    except Exception as e:
        return [
            types.TextContent(type="text", text=f"Error creating taxonomy: {str(e)}")
        ]


def _create_guidelines_prompt(taxonomy_name: str, taxonomy_description: str) -> str:
    """Create a comprehensive prompt for LLM to generate flexible taxonomy guidelines."""
    return f"""# Taxonomy Guidelines Generation

## Task
Generate flexible entry structure guidelines for a taxonomy called "{taxonomy_name}" with this description: {taxonomy_description}

## Core Philosophy
These guidelines should serve as **flexible frameworks** rather than rigid templates. Writers should feel empowered to adapt the structure to best serve each individual entry's unique needs and story.

## Required Output Format

Please generate the complete guidelines using this exact structure:

```markdown
## Entry Guidelines for {taxonomy_name.title()}
These guidelines provide a flexible framework - adapt sections as needed for each entry's unique story.

### Core Elements (Include Most)
- **[Section Name]** - [What this typically covers, with flexibility notes]
- **[Section Name]** - [What this typically covers, with flexibility notes]
- **[Section Name]** - [What this typically covers, with flexibility notes]

### Additional Elements (Use When Relevant)
- **[Section Name]** - [When this adds value to the entry]
- **[Section Name]** - [When this adds value to the entry]
- **[Section Name]** - [When this adds value to the entry]

## Writing Guidelines
- **Length**: Target 300-400 words for initial entries (expand if the story demands it)
- **Voice**: Favor engaging, immersive writing over bland description
- **Style**: Mix documentary precision with narrative flair - include quotes, in-world documents, interesting perspectives
- **Connections**: Weave in references to existing entries naturally
- **Personality**: Each entry should feel distinctive and memorable

## Content Approach
- Use in-world quotes, documents, or observations when they enhance the entry
- Include specific, vivid details that bring the element to life
- Show relationships and conflicts rather than just listing them
- Write from interesting angles - a scholar's notes, a traveler's account, conflicting reports
- Make each entry feel like it has personality and history
```

## Guidelines for Your Response
- Emphasize **flexibility** - these are guides, not rigid rules
- Focus on what makes compelling, engaging entries for this taxonomy type
- Consider unique storytelling approaches appropriate to this element type
- Suggest 3-4 core elements and 3-4 additional elements
- Encourage creative, immersive writing approaches
- Think about what would make entries in this taxonomy memorable and distinctive

Generate the complete guidelines now:"""


# Tool router for taxonomy operations
TAXONOMY_HANDLERS = {
    "create_taxonomy": create_taxonomy,
    "create_taxonomy_with_llm_guidelines": create_taxonomy_with_llm_guidelines,
}


async def handle_taxonomy_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent]:
    """Route taxonomy tool calls to appropriate handlers.

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        Tool execution result

    Raises:
        ValueError: If tool name is not recognized
    """
    if name not in TAXONOMY_HANDLERS:
        raise ValueError(f"Unknown taxonomy tool: {name}")

    return await TAXONOMY_HANDLERS[name](arguments)
