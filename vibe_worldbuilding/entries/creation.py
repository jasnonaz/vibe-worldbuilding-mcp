"""Entry creation module for the Vibe Worldbuilding MCP.

This module handles the creation of detailed world entries with proper formatting,
frontmatter, image generation, and integration with the world context system.
"""

import mcp.types as types
from pathlib import Path
from typing import Any

from ..config import (
    FAL_AVAILABLE, FAL_API_KEY, FAL_API_URL, MARKDOWN_EXTENSION, 
    IMAGE_EXTENSION, TAXONOMY_OVERVIEW_SUFFIX, MAX_DESCRIPTION_LINES
)
from ..utils.content_parsing import (
    extract_frontmatter, 
    add_frontmatter_to_content,
    extract_description_from_content
)
from .utilities import (
    clean_name, extract_taxonomy_context, get_existing_taxonomies,
    get_existing_entries_with_descriptions, create_world_context_prompt
)
from .stub_generation import generate_stub_analysis

if FAL_AVAILABLE:
    import requests


async def create_world_entry(arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Create a detailed entry for a specific world element within a taxonomy.
    
    Creates an entry file with taxonomy context, generates an image if possible,
    and provides automatic stub analysis for entities mentioned in the content.
    
    Args:
        arguments: Tool arguments containing world_directory, taxonomy, entry_name, and entry_content
        
    Returns:
        List containing success message with entry details and optional stub analysis
    """
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]
    
    world_directory = arguments.get("world_directory", "")
    taxonomy = arguments.get("taxonomy", "")
    entry_name = arguments.get("entry_name", "")
    entry_content = arguments.get("entry_content", "")
    
    if not all([world_directory, taxonomy, entry_name]):
        return [types.TextContent(type="text", text="Error: world_directory, taxonomy, and entry_name are required")]
    
    try:
        world_path = Path(world_directory)
        if not world_path.exists():
            return [types.TextContent(type="text", text=f"Error: World directory {world_directory} does not exist")]
        
        # Clean names for file system use
        clean_taxonomy = clean_name(taxonomy)
        clean_entry = clean_name(entry_name)
        
        # Extract taxonomy context if available
        taxonomy_context = extract_taxonomy_context(world_path, clean_taxonomy)
        
        # Get world context for generating well-connected entries
        existing_taxonomies = get_existing_taxonomies(world_path)
        existing_entries = get_existing_entries_with_descriptions(world_path)
        
        # Get world overview if available
        world_overview = _get_world_overview(world_path)
        
        # Create comprehensive world context for the LLM
        world_context = create_world_context_prompt(
            existing_taxonomies, existing_entries, taxonomy_context, 
            world_overview, taxonomy
        )
        
        # Always show context first, then handle entry creation
        if entry_content.strip():
            # Create the entry file
            entry_file = _create_entry_file(
                world_path, clean_taxonomy, clean_entry, entry_name, 
                entry_content, taxonomy, taxonomy_context
            )
            
            # Generate entry image if FAL API is available
            image_info = await _generate_entry_image(
                world_path, clean_taxonomy, clean_entry, entry_name, 
                entry_content, taxonomy_context
            )
            
            # Generate auto-stub analysis
            stub_analysis_info = generate_stub_analysis(
                world_path, entry_name, taxonomy, entry_content
            )
            
            # Create response with context + creation result
            relative_path = str(entry_file.relative_to(world_path))
            context_info = f"\n\nTaxonomy context included: {taxonomy_context[:100]}..." if taxonomy_context else "\n\nNo taxonomy overview found for reference."
            
            return [types.TextContent(
                type="text",
                text=f"# World Context Used for '{entry_name}'\n\n{world_context}\n\n---\n\n## Entry Created Successfully!\n\nSaved to: {relative_path}{context_info}\n\nThe entry includes:\n1. YAML frontmatter with description\n2. Your detailed content\n3. Taxonomy classification footer{image_info}{stub_analysis_info}\n\n**Note**: Review the content above - it should include crosslinks to existing entries based on the context provided."
            )]
        else:
            # Return world context for entry generation
            return [types.TextContent(
                type="text",
                text=f"# World Context for Creating '{entry_name}' in {taxonomy}\n\n{world_context}\n\n---\n\n**Next Step**: Generate entry content that references existing entries using the linking format provided above, then call this tool again with your `entry_content`."
            )]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error creating world entry: {str(e)}")]


def _get_world_overview(world_path: Path) -> str:
    """Get world overview content for context."""
    world_overview = ""
    overview_path = world_path / "overview" / "world-overview.md"
    if overview_path.exists():
        try:
            with open(overview_path, "r", encoding="utf-8") as f:
                content = f.read()
                world_overview = content[:500] + ("..." if len(content) > 500 else "")
        except Exception:
            pass
    return world_overview


def _create_entry_file(
    world_path: Path, clean_taxonomy: str, clean_entry: str, entry_name: str,
    entry_content: str, taxonomy: str, taxonomy_context: str
) -> Path:
    """Create the entry file with proper formatting and frontmatter."""
    entry_path = world_path / "entries" / clean_taxonomy
    entry_path.mkdir(parents=True, exist_ok=True)
    
    entry_file = entry_path / f"{clean_entry}{MARKDOWN_EXTENSION}"
    
    # Extract description for frontmatter
    description = extract_description_from_content(entry_content)
    
    # Build frontmatter
    frontmatter = {
        "description": description,
        "article_type": "full"
    }
    if taxonomy_context:
        frontmatter["taxonomyContext"] = taxonomy_context
    
    # Add frontmatter to content
    final_content = add_frontmatter_to_content(entry_content, frontmatter)
    
    # Add taxonomy footer
    final_content += f"\n\n---\n*Entry in {taxonomy.title()} taxonomy*\n"
    
    with open(entry_file, "w", encoding="utf-8") as f:
        f.write(final_content)
    
    return entry_file


async def _generate_entry_image(
    world_path: Path, clean_taxonomy: str, clean_entry: str, entry_name: str,
    entry_content: str, taxonomy_context: str
) -> str:
    """Generate an image for the entry using FAL API."""
    if not (FAL_AVAILABLE and FAL_API_KEY):
        return ""
    
    try:
        # Extract visual elements from content
        title, description = _extract_visual_elements(entry_name, entry_content)
        
        # Create entry-specific prompt
        if taxonomy_context:
            entry_prompt = f"Detailed illustration of {title}, {description}, within the context of {taxonomy_context[:100]}, fantasy art style, detailed digital art"
        else:
            entry_prompt = f"Detailed illustration of {title}, {description}, fantasy art style, detailed digital art"
        
        # Generate image
        headers = {
            "Authorization": f"Key {FAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": entry_prompt,
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
                    # Save entry image in organized structure
                    images_dir = world_path / "images"
                    images_dir.mkdir(exist_ok=True)
                    
                    category_dir = images_dir / clean_taxonomy
                    category_dir.mkdir(exist_ok=True)
                    
                    entry_image_path = category_dir / f"{clean_entry}{IMAGE_EXTENSION}"
                    with open(entry_image_path, "wb") as f:
                        f.write(image_response.content)
                    
                    return f"\n4. Generated image: images/{clean_taxonomy}/{clean_entry}{IMAGE_EXTENSION}"
    except Exception:
        pass  # Silently continue if image generation fails
    
    return ""


def _extract_visual_elements(entry_name: str, entry_content: str) -> tuple[str, str]:
    """Extract title and description for image generation."""
    lines = entry_content.split('\n')
    title = entry_name
    description_lines = []
    
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
        elif line.strip() and not line.startswith('#') and not line.startswith('---'):
            description_lines.append(line.strip())
            if len(description_lines) >= MAX_DESCRIPTION_LINES:
                break
    
    description = ' '.join(description_lines)
    return title, description