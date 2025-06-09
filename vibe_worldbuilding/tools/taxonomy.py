"""Taxonomy management tools for the Vibe Worldbuilding MCP.

This module handles the creation and management of taxonomies, which are
classification systems for organizing world elements into categories.
"""

import mcp.types as types
from pathlib import Path
from typing import Any

from ..config import (
    FAL_AVAILABLE, FAL_API_KEY, FAL_API_URL, MARKDOWN_EXTENSION, 
    IMAGE_EXTENSION, TAXONOMY_OVERVIEW_SUFFIX
)

if FAL_AVAILABLE:
    import requests


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
        return [types.TextContent(type="text", text="Error: world_directory, taxonomy_name, and taxonomy_description are required")]
    
    # If no guidelines provided, return prompt for LLM to generate them
    if not custom_guidelines.strip():
        guidelines_prompt = _create_guidelines_prompt(taxonomy_name, taxonomy_description)
        return [types.TextContent(type="text", text=guidelines_prompt)]
    
    # Otherwise, create the taxonomy with the provided guidelines
    return await _create_taxonomy_structure(world_directory, taxonomy_name, taxonomy_description, custom_guidelines)


async def _create_taxonomy_structure(world_directory: str, taxonomy_name: str, taxonomy_description: str, custom_guidelines: str) -> list[types.TextContent]:
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
            return [types.TextContent(type="text", text=f"Error: World directory {world_directory} does not exist")]
        
        # Clean taxonomy name for file system use
        clean_taxonomy_name = taxonomy_name.lower().replace(" ", "-").replace("_", "-")
        
        # Create taxonomies directory
        taxonomies_dir = world_path / "taxonomies"
        taxonomies_dir.mkdir(exist_ok=True)
        
        # Create entries directory for this taxonomy
        entries_dir = world_path / "entries" / clean_taxonomy_name
        entries_dir.mkdir(parents=True, exist_ok=True)
        
        # Create taxonomy overview file
        taxonomy_overview_path = taxonomies_dir / f"{clean_taxonomy_name}{TAXONOMY_OVERVIEW_SUFFIX}{MARKDOWN_EXTENSION}"
        
        # Build the complete taxonomy overview content
        overview_content = f"""# {taxonomy_name.title()} - Taxonomy Overview

## Description
{taxonomy_description}

{custom_guidelines}

## Tone and Style
Descriptive and immersive, maintaining consistency with the world's established tone.
"""
        
        with open(taxonomy_overview_path, "w", encoding="utf-8") as f:
            f.write(overview_content)
        
        # Create response
        relative_overview_path = str(taxonomy_overview_path.relative_to(world_path))
        relative_entries_path = str(entries_dir.relative_to(world_path))
        
        return [types.TextContent(
            type="text",
            text=f"Successfully created taxonomy '{taxonomy_name}'!\n\nCreated files:\n- Overview: {relative_overview_path}\n- Entries directory: {relative_entries_path}\n\nThe taxonomy is now ready for creating entries. Use the create_world_entry tool to add specific {taxonomy_name.lower()} entries."
        )]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error creating taxonomy: {str(e)}")]


def _create_guidelines_prompt(taxonomy_name: str, taxonomy_description: str) -> str:
    """Create a comprehensive prompt for LLM to generate taxonomy guidelines."""
    return f"""# Taxonomy Guidelines Generation

## Task
Generate comprehensive entry structure guidelines for a taxonomy called "{taxonomy_name}" with this description: {taxonomy_description}

## Instructions
Create specific, detailed guidelines that will help writers create consistent, high-quality entries for this taxonomy. Your guidelines should be practical and actionable.

## Required Output Format

Please generate the complete guidelines using this exact structure:

```markdown
## Entry Structure for {taxonomy_name.title()}
Each {taxonomy_name.lower()} entry should include:

### Required Sections
- **[Section Name]** - [Specific description of what this section should contain]
- **[Section Name]** - [Specific description of what this section should contain]
- **[Section Name]** - [Specific description of what this section should contain]

### Optional Sections
- **[Section Name]** - [When and why to include this section]
- **[Section Name]** - [When and why to include this section]

## Writing Guidelines
- **Length**: [Specific word count or paragraph guidelines]
- **Focus**: [What aspects should be emphasized]
- **Relationships**: [How entries should connect to other taxonomies]
- **Details**: [Level of detail appropriate for this taxonomy]

## Content Requirements
- [Specific requirement 1]
- [Specific requirement 2]
- [Specific requirement 3]
```

## Guidelines for Your Response
- Be specific to the {taxonomy_name} taxonomy type
- Consider what makes this taxonomy unique in a worldbuilding context
- Provide practical structure that writers can follow
- Include 3-5 required sections and 2-3 optional sections
- Make guidelines that will create rich, interconnected world content
- Focus on what would be most useful for this specific type of world element

Generate the complete guidelines now:"""


# Tool router for taxonomy operations
TAXONOMY_HANDLERS = {
    "create_taxonomy": create_taxonomy,
}


async def handle_taxonomy_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
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