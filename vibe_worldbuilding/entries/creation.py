"""Entry creation module for the Vibe Worldbuilding MCP.

This module handles the creation of detailed world entries with proper formatting,
frontmatter, image generation, and integration with the world context system.
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
    MAX_DESCRIPTION_LINES,
    TAXONOMY_OVERVIEW_SUFFIX,
)
from ..utils.content_parsing import (
    add_frontmatter_to_content,
    extract_description_from_content,
    extract_frontmatter,
)
from .stub_generation import generate_stub_analysis
from .utilities import (
    clean_name,
    create_world_context_prompt,
    extract_taxonomy_context,
    get_existing_entries_with_descriptions,
    get_existing_taxonomies,
)

if FAL_AVAILABLE:
    import requests


async def create_world_entry(
    arguments: dict[str, Any] | None,
) -> list[types.TextContent]:
    """Create a detailed entry for a specific world element within a taxonomy.

    Creates an entry file with taxonomy context, generates an image if possible,
    and provides automatic stub analysis for entities mentioned in the content.

    Args:
        arguments: Tool arguments containing world_directory, taxonomy, entry_name, and entry_content

    Returns:
        List containing success message with entry details and optional stub analysis
    """
    # LOGGING: Validate that new code is being executed
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] VALIDATION LOG: create_world_entry called with new validation code")
    
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]

    world_directory = arguments.get("world_directory", "")
    taxonomy = arguments.get("taxonomy", "")
    entry_name = arguments.get("entry_name", "")
    entry_content = arguments.get("entry_content", "")
    
    print(f"[{timestamp}] VALIDATION LOG: taxonomy='{taxonomy}', entry_name='{entry_name}', has_content={bool(entry_content.strip())}")

    if not all([world_directory, taxonomy, entry_name]):
        return [
            types.TextContent(
                type="text",
                text="Error: world_directory, taxonomy, and entry_name are required",
            )
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

        # Clean names for file system use
        clean_taxonomy = clean_name(taxonomy)
        clean_entry = clean_name(entry_name)

        # Check if taxonomy exists before proceeding
        taxonomy_overview_file = world_path / "taxonomies" / f"{clean_taxonomy}{TAXONOMY_OVERVIEW_SUFFIX}.md"
        print(f"[{timestamp}] VALIDATION LOG: checking taxonomy file: {taxonomy_overview_file}")
        print(f"[{timestamp}] VALIDATION LOG: file exists: {taxonomy_overview_file.exists()}")
        
        if not taxonomy_overview_file.exists():
            existing_taxonomies = get_existing_taxonomies(world_path)
            taxonomy_list = ", ".join(existing_taxonomies) if existing_taxonomies else "None"
            print(f"[{timestamp}] VALIDATION LOG: TAXONOMY VALIDATION FAILED - returning error")
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: Taxonomy '{taxonomy}' does not exist. Available taxonomies: {taxonomy_list}\n\nUse the create_taxonomy tool to create this taxonomy first.",
                )
            ]
        
        print(f"[{timestamp}] VALIDATION LOG: taxonomy validation passed, continuing...")

        # Extract taxonomy context if available
        taxonomy_context = extract_taxonomy_context(world_path, clean_taxonomy)

        # Get world context for generating well-connected entries
        existing_taxonomies = get_existing_taxonomies(world_path)
        existing_entries = get_existing_entries_with_descriptions(world_path)

        # Get world overview if available
        world_overview = _get_world_overview(world_path)

        # Create comprehensive world context for the LLM
        world_context = create_world_context_prompt(
            existing_taxonomies,
            existing_entries,
            taxonomy_context,
            world_overview,
            taxonomy,
        )

        # Always show context first, then handle entry creation
        if entry_content.strip():
            # Create the entry file
            entry_file = _create_entry_file(
                world_path,
                clean_taxonomy,
                clean_entry,
                entry_name,
                entry_content,
                taxonomy,
                taxonomy_context,
            )

            # Generate optimized image prompt and image if FAL API is available
            image_info = await _generate_optimized_entry_image(
                world_path,
                clean_taxonomy,
                clean_entry,
                entry_name,
                entry_content,
            )

            # Generate auto-stub analysis
            stub_analysis_info = generate_stub_analysis(
                world_path, entry_name, taxonomy, entry_content
            )

            # Create response with context + creation result
            relative_path = str(entry_file.relative_to(world_path))
            context_info = (
                f"\n\nTaxonomy context included: {taxonomy_context[:100]}..."
                if taxonomy_context
                else "\n\nNo taxonomy overview found for reference."
            )

            return [
                types.TextContent(
                    type="text",
                    text=f"# World Context Used for '{entry_name}'\n\n{world_context}\n\n---\n\n## Entry Created Successfully!\n\nSaved to: {relative_path}{context_info}\n\nThe entry includes:\n1. YAML frontmatter with description\n2. Your detailed content\n3. Taxonomy classification footer{image_info}{stub_analysis_info}\n\n**Note**: Review the content above - it should include crosslinks to existing entries based on the context provided.",
                )
            ]
        else:
            # Return world context for entry generation
            return [
                types.TextContent(
                    type="text",
                    text=f"# World Context for Creating '{entry_name}' in {taxonomy}\n\n{world_context}\n\n---\n\n**Next Step**: Generate entry content that references existing entries using the linking format provided above, then call this tool again with your `entry_content`.",
                )
            ]

    except Exception as e:
        return [
            types.TextContent(type="text", text=f"Error creating world entry: {str(e)}")
        ]


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
    world_path: Path,
    clean_taxonomy: str,
    clean_entry: str,
    entry_name: str,
    entry_content: str,
    taxonomy: str,
    taxonomy_context: str,
) -> Path:
    """Create the entry file with proper formatting and frontmatter."""
    entry_path = world_path / "entries" / clean_taxonomy
    entry_path.mkdir(parents=True, exist_ok=True)

    entry_file = entry_path / f"{clean_entry}{MARKDOWN_EXTENSION}"

    # Extract description for frontmatter
    description = extract_description_from_content(entry_content)

    # Build frontmatter
    frontmatter = {"description": description, "article_type": "full"}
    if taxonomy_context:
        frontmatter["taxonomyContext"] = taxonomy_context

    # Add frontmatter to content
    final_content = add_frontmatter_to_content(entry_content, frontmatter)

    # Add taxonomy footer
    final_content += f"\n\n---\n*Entry in {taxonomy.title()} taxonomy*\n"

    with open(entry_file, "w", encoding="utf-8") as f:
        f.write(final_content)

    return entry_file


async def _generate_optimized_entry_image(
    world_path: Path,
    clean_taxonomy: str,
    clean_entry: str,
    entry_name: str,
    entry_content: str,
) -> str:
    """Generate an optimized image using the new prompt system."""
    if not (FAL_AVAILABLE and FAL_API_KEY):
        return ""

    try:
        # Create the entry file path for our new image tools
        entry_file_path = world_path / "entries" / clean_taxonomy / f"{clean_entry}{MARKDOWN_EXTENSION}"
        
        # Use the existing generate_image_from_markdown_file function which now checks for
        # image_prompt in frontmatter and uses optimized prompts
        from ..tools.images import generate_image_from_markdown_file
        
        result = await generate_image_from_markdown_file({
            "filepath": str(entry_file_path),
            "style": "fantasy illustration",
            "aspect_ratio": "1:1"
        })
        
        if result and result[0].text.startswith("Successfully generated"):
            return f"\n4. Generated optimized image: images/{clean_taxonomy}/{clean_entry}{IMAGE_EXTENSION}"
        
    except Exception:
        pass  # Silently continue if image generation fails

    return ""


# Old _extract_visual_elements function removed - now using optimized image prompt system
