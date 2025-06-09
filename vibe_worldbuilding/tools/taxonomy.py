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


async def generate_taxonomy_guidelines(arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Generate structured entry guidelines for a specific taxonomy type.
    
    This function creates a detailed prompt that helps users generate custom
    guidelines for their taxonomy entries using an LLM.
    
    Args:
        arguments: Tool arguments containing taxonomy_name and taxonomy_description
        
    Returns:
        List containing the generated prompt for creating taxonomy guidelines
    """
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]
    
    taxonomy_name = arguments.get("taxonomy_name", "")
    taxonomy_description = arguments.get("taxonomy_description", "")
    
    if not taxonomy_name or not taxonomy_description:
        return [types.TextContent(type="text", text="Error: taxonomy_name and taxonomy_description are required")]
    
    guidelines_prompt = f"""Please generate structured entry guidelines for a taxonomy called "{taxonomy_name}" with this description: {taxonomy_description}

Create specific entry structure guidelines. Generate the complete guidelines including:

## Entry Structure for {taxonomy_name.title()}
Each {taxonomy_name.lower()} entry should include:

### Required Sections
[List exactly 3-5 core sections that every entry should have - be very specific to this taxonomy type]

### Optional Sections (choose 2-3 most relevant)
[List 2-3 additional sections that might be relevant for some entries]

## Writing Guidelines
- **Length**: [Specify appropriate word count for this taxonomy type]
- **Complexity Control**: [How many references to make, what to avoid]
- **Focus**: [What should entries emphasize for this specific taxonomy]
- **Relationships**: [How entries should connect to others]

## Tone and Style
[Describe the appropriate writing tone and style for this taxonomy type]

Make everything specific to this taxonomy concept. The guidelines you create will be used directly to create individual entries, so be detailed and practical.

Provide the complete formatted guidelines - I'll use them exactly as you write them."""

    return [types.TextContent(type="text", text=guidelines_prompt)]


async def create_taxonomy_folders(arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Create a single taxonomy with custom guidelines for a world project.
    
    Creates the taxonomy overview file, entry directory, and optionally
    generates a conceptual image for the taxonomy.
    
    Args:
        arguments: Tool arguments containing world_directory, taxonomy details, and guidelines
        
    Returns:
        List containing success message with created files/folders
    """
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]
    
    world_directory = arguments.get("world_directory", "")
    taxonomy_name = arguments.get("taxonomy_name", "")
    taxonomy_description = arguments.get("taxonomy_description", "")
    custom_guidelines = arguments.get("custom_guidelines", "")
    
    if not world_directory or not taxonomy_name or not taxonomy_description:
        return [types.TextContent(type="text", text="Error: world_directory, taxonomy_name, and taxonomy_description are required")]
    
    if not custom_guidelines:
        return [types.TextContent(type="text", text="Error: custom_guidelines is required. Please run 'generate_taxonomy_guidelines' first to create guidelines for this taxonomy, then use those guidelines here.")]
    
    try:
        world_path = Path(world_directory)
        if not world_path.exists():
            return [types.TextContent(type="text", text=f"Error: World directory {world_directory} does not exist")]
        
        created_folders = []
        clean_name = _clean_taxonomy_name(taxonomy_name)
        
        # Create taxonomy overview file
        taxonomy_file = _create_taxonomy_overview(
            world_path, clean_name, taxonomy_name, taxonomy_description, custom_guidelines
        )
        created_folders.append(f"taxonomies/{clean_name}{TAXONOMY_OVERVIEW_SUFFIX}{MARKDOWN_EXTENSION}")
        
        # Create entry directory for the taxonomy
        entry_path = _create_entry_directory(world_path, clean_name)
        created_folders.append(f"entries/{clean_name}")
        
        # Generate taxonomy image if FAL API is available
        image_created = await _generate_taxonomy_image(
            world_path, clean_name, taxonomy_name, taxonomy_description
        )
        if image_created:
            created_folders.append(f"images/{clean_name}-taxonomy{IMAGE_EXTENSION}")

        return [types.TextContent(
            type="text", 
            text=f"Successfully created taxonomy '{taxonomy_name}'!\n\nCreated:\n" + 
                 "\n".join(f"- {folder}" for folder in created_folders)
        )]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error creating taxonomy folders: {str(e)}")]


def _clean_taxonomy_name(taxonomy_name: str) -> str:
    """Clean taxonomy name for use in file/folder names.
    
    Args:
        taxonomy_name: Raw taxonomy name
        
    Returns:
        Cleaned name suitable for filenames
    """
    return taxonomy_name.lower().replace(" ", "-").replace("_", "-")


def _create_taxonomy_overview(
    world_path: Path, clean_name: str, taxonomy_name: str, 
    taxonomy_description: str, custom_guidelines: str
) -> Path:
    """Create the taxonomy overview file.
    
    Args:
        world_path: Path to the world directory
        clean_name: Cleaned taxonomy name for filename
        taxonomy_name: Display name of the taxonomy
        taxonomy_description: Description of the taxonomy
        custom_guidelines: Custom guidelines for entries in this taxonomy
        
    Returns:
        Path to the created taxonomy file
    """
    taxonomies_path = world_path / "taxonomies"
    taxonomies_path.mkdir(exist_ok=True)
    
    taxonomy_file = taxonomies_path / f"{clean_name}{TAXONOMY_OVERVIEW_SUFFIX}{MARKDOWN_EXTENSION}"
    
    taxonomy_content = f"""# {taxonomy_name.title()} - Taxonomy Overview

## Description
{taxonomy_description}

{custom_guidelines}
"""

    with open(taxonomy_file, "w", encoding="utf-8") as f:
        f.write(taxonomy_content)
    
    return taxonomy_file


def _create_entry_directory(world_path: Path, clean_name: str) -> Path:
    """Create the entry directory for the taxonomy.
    
    Args:
        world_path: Path to the world directory
        clean_name: Cleaned taxonomy name for directory
        
    Returns:
        Path to the created entry directory
    """
    entries_path = world_path / "entries"
    entries_path.mkdir(exist_ok=True)
    entry_path = entries_path / clean_name
    entry_path.mkdir(exist_ok=True)
    
    return entry_path


async def _generate_taxonomy_image(
    world_path: Path, clean_name: str, taxonomy_name: str, taxonomy_description: str
) -> bool:
    """Generate a conceptual image for the taxonomy.
    
    Args:
        world_path: Path to the world directory
        clean_name: Cleaned taxonomy name for filename
        taxonomy_name: Display name of the taxonomy
        taxonomy_description: Description for prompt generation
        
    Returns:
        True if image was generated successfully, False otherwise
    """
    if not (FAL_AVAILABLE and FAL_API_KEY):
        return False
    
    try:
        # Create taxonomy-specific prompt
        taxonomy_prompt = f"Conceptual illustration of {taxonomy_name}, {taxonomy_description}, fantasy art style, detailed digital illustration"
        
        headers = {
            "Authorization": f"Key {FAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": taxonomy_prompt,
            "aspect_ratio": "1:1",
            "num_images": 1
        }
        
        response = requests.post(FAL_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if "images" in result and result["images"]:
                image_url = result["images"][0]["url"]
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    # Save taxonomy image
                    images_dir = world_path / "images"
                    images_dir.mkdir(exist_ok=True)
                    taxonomy_image_path = images_dir / f"{clean_name}-taxonomy{IMAGE_EXTENSION}"
                    with open(taxonomy_image_path, "wb") as f:
                        f.write(image_response.content)
                    return True
    except Exception:
        # Silently continue if image generation fails
        pass
    
    return False


# Tool router for taxonomy operations
TAXONOMY_HANDLERS = {
    "generate_taxonomy_guidelines": generate_taxonomy_guidelines,
    "create_taxonomy_folders": create_taxonomy_folders,
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