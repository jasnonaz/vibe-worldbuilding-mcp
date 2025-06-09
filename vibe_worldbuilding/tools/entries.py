"""Entry creation and management tools for the Vibe Worldbuilding MCP.

This module handles the creation of detailed world entries, stub generation,
and content analysis for auto-stub identification. This is the most complex
module as it includes the intelligent stub generation workflow.
"""

import mcp.types as types
from pathlib import Path
from typing import Any, Dict, List

from ..config import (
    FAL_AVAILABLE, FAL_API_KEY, FAL_API_URL, MARKDOWN_EXTENSION, 
    IMAGE_EXTENSION, TAXONOMY_OVERVIEW_SUFFIX, MAX_DESCRIPTION_LINES
)
from ..utils.content_parsing import (
    extract_frontmatter, 
    add_frontmatter_to_content,
    extract_description_from_content
)

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
        clean_taxonomy = _clean_name(taxonomy)
        clean_entry = _clean_name(entry_name)
        
        # Extract taxonomy context if available
        taxonomy_context = _extract_taxonomy_context(world_path, clean_taxonomy)
        
        # Get world context for generating well-connected entries
        existing_taxonomies = _get_existing_taxonomies(world_path)
        existing_entries = _get_existing_entries_with_descriptions(world_path)
        
        # Get world overview if available
        world_overview = ""
        overview_path = world_path / "overview" / "world-overview.md"
        if overview_path.exists():
            try:
                with open(overview_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    world_overview = content[:500] + ("..." if len(content) > 500 else "")
            except Exception:
                pass
        
        # Create comprehensive world context for the LLM
        world_context = _create_world_context_prompt(
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
            stub_analysis_info = _generate_stub_analysis(
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


async def identify_stub_candidates(arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Analyze entry content and present it to client LLM for stub candidate identification.
    
    Creates a comprehensive analysis prompt that includes world context,
    existing taxonomies, and existing entries to help the LLM identify
    entities that should become stub entries.
    
    Args:
        arguments: Tool arguments containing world_directory, entry_content, entry_name, and taxonomy
        
    Returns:
        List containing analysis prompt for the client LLM
    """
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]
    
    world_directory = arguments.get("world_directory", "")
    entry_content = arguments.get("entry_content", "")
    entry_name = arguments.get("entry_name", "")
    taxonomy = arguments.get("taxonomy", "")
    
    if not all([world_directory, entry_content, entry_name, taxonomy]):
        return [types.TextContent(type="text", text="Error: All parameters (world_directory, entry_content, entry_name, taxonomy) are required")]
    
    try:
        world_path = Path(world_directory)
        if not world_path.exists():
            return [types.TextContent(type="text", text=f"Error: World directory {world_directory} does not exist")]
        
        # Get world context
        existing_taxonomies = _get_existing_taxonomies(world_path)
        existing_entries = _get_existing_entries_with_descriptions(world_path)
        
        # Create analysis prompt
        analysis_prompt = _create_analysis_prompt(
            entry_name, taxonomy, entry_content, existing_taxonomies, existing_entries
        )
        
        return [types.TextContent(type="text", text=analysis_prompt)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error analyzing entry for stub candidates: {str(e)}")]


async def generate_entry_descriptions(arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Present entry content to client LLM for description generation.
    
    This tool presents entries without descriptions to the client LLM
    for intelligent description generation, following the LLM-first design principle.
    
    Args:
        arguments: Tool arguments containing world_directory
        
    Returns:
        List containing analysis prompt for the client LLM
    """
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]
    
    world_directory = arguments.get("world_directory", "")
    
    if not world_directory:
        return [types.TextContent(type="text", text="Error: world_directory is required")]
    
    try:
        world_path = Path(world_directory)
        if not world_path.exists():
            return [types.TextContent(type="text", text=f"Error: World directory {world_directory} does not exist")]
        
        entries_path = world_path / "entries"
        if not entries_path.exists():
            return [types.TextContent(type="text", text="No entries directory found")]
        
        entries_needing_descriptions = []
        
        # Find entries without descriptions
        for taxonomy_dir in entries_path.iterdir():
            if taxonomy_dir.is_dir():
                for entry_file in taxonomy_dir.glob(f"*{MARKDOWN_EXTENSION}"):
                    try:
                        with open(entry_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        # Check if already has frontmatter with description
                        existing_frontmatter, main_content = extract_frontmatter(content)
                        if "description" not in existing_frontmatter:
                            entry_name = entry_file.stem.replace("-", " ").title()
                            taxonomy_name = taxonomy_dir.name.replace("-", " ").title()
                            
                            entries_needing_descriptions.append({
                                "name": entry_name,
                                "taxonomy": taxonomy_name,
                                "content": main_content[:500] + ("..." if len(main_content) > 500 else ""),
                                "file_path": str(entry_file.relative_to(world_path))
                            })
                    except Exception:
                        continue
        
        if not entries_needing_descriptions:
            return [types.TextContent(type="text", text="All entries already have descriptions in their frontmatter.")]
        
        # Create analysis prompt for LLM
        prompt = _create_description_generation_prompt(entries_needing_descriptions)
        return [types.TextContent(type="text", text=prompt)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error analyzing entries for descriptions: {str(e)}")]


async def add_frontmatter_to_entries(arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Add YAML frontmatter with descriptions to existing entries.
    
    Processes all entry files in a world directory, extracting descriptions
    from their content and adding them as YAML frontmatter. Useful for
    retrofitting existing entries with metadata.
    
    Args:
        arguments: Tool arguments containing world_directory
        
    Returns:
        List containing summary of updated entries
    """
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]
    
    world_directory = arguments.get("world_directory", "")
    
    if not world_directory:
        return [types.TextContent(type="text", text="Error: world_directory is required")]
    
    try:
        world_path = Path(world_directory)
        if not world_path.exists():
            return [types.TextContent(type="text", text=f"Error: World directory {world_directory} does not exist")]
        
        entries_path = world_path / "entries"
        if not entries_path.exists():
            return [types.TextContent(type="text", text="No entries directory found")]
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        # Process all entry files
        for taxonomy_dir in entries_path.iterdir():
            if taxonomy_dir.is_dir():
                for entry_file in taxonomy_dir.glob(f"*{MARKDOWN_EXTENSION}"):
                    try:
                        # Read existing content
                        with open(entry_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        # Check if already has frontmatter with description
                        existing_frontmatter, _ = extract_frontmatter(content)
                        if "description" in existing_frontmatter:
                            skipped_count += 1
                            continue
                        
                        # Extract description and add frontmatter
                        description = extract_description_from_content(content)
                        if description:
                            updated_content = add_frontmatter_to_content(content, {
                                "description": description
                            })
                            
                            # Write updated content
                            with open(entry_file, "w", encoding="utf-8") as f:
                                f.write(updated_content)
                            
                            updated_count += 1
                        else:
                            skipped_count += 1
                            
                    except Exception as e:
                        error_count += 1
                        print(f"Error processing {entry_file}: {e}")
        
        # Create summary
        summary = f"Frontmatter update completed:\n"
        summary += f"- Updated: {updated_count} entries\n"
        summary += f"- Skipped: {skipped_count} entries (already had description or no content)\n"
        if error_count > 0:
            summary += f"- Errors: {error_count} entries\n"
        
        return [types.TextContent(type="text", text=summary)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error adding frontmatter to entries: {str(e)}")]


async def apply_entry_descriptions(arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Apply generated descriptions to entry frontmatter.
    
    Takes a list of entry names and descriptions from the client LLM
    and applies them as YAML frontmatter to the corresponding entry files.
    
    Args:
        arguments: Tool arguments containing world_directory and entry_descriptions list
        
    Returns:
        List containing summary of updated entries
    """
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]
    
    world_directory = arguments.get("world_directory", "")
    entry_descriptions = arguments.get("entry_descriptions", [])
    
    if not world_directory or not entry_descriptions:
        return [types.TextContent(type="text", text="Error: world_directory and entry_descriptions are required")]
    
    try:
        world_path = Path(world_directory)
        if not world_path.exists():
            return [types.TextContent(type="text", text=f"Error: World directory {world_directory} does not exist")]
        
        entries_path = world_path / "entries"
        if not entries_path.exists():
            return [types.TextContent(type="text", text="No entries directory found")]
        
        updated_count = 0
        not_found_count = 0
        error_count = 0
        
        # Create a mapping of entry names to find files
        entry_file_map = {}
        for taxonomy_dir in entries_path.iterdir():
            if taxonomy_dir.is_dir():
                for entry_file in taxonomy_dir.glob(f"*{MARKDOWN_EXTENSION}"):
                    entry_name = entry_file.stem.replace("-", " ").title()
                    entry_file_map[entry_name] = entry_file
        
        # Apply descriptions
        for desc_entry in entry_descriptions:
            entry_name = desc_entry.get("name", "")
            description = desc_entry.get("description", "")
            
            if not entry_name or not description:
                error_count += 1
                continue
            
            if entry_name not in entry_file_map:
                not_found_count += 1
                continue
            
            try:
                entry_file = entry_file_map[entry_name]
                
                # Read existing content
                with open(entry_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Add frontmatter with description
                updated_content = add_frontmatter_to_content(content, {
                    "description": description
                })
                
                # Write updated content
                with open(entry_file, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                
                updated_count += 1
                
            except Exception as e:
                error_count += 1
        
        # Create summary
        summary = f"Applied descriptions to entries:\n"
        summary += f"- Updated: {updated_count} entries\n"
        if not_found_count > 0:
            summary += f"- Not found: {not_found_count} entries\n"
        if error_count > 0:
            summary += f"- Errors: {error_count} entries\n"
        
        return [types.TextContent(type="text", text=summary)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error applying entry descriptions: {str(e)}")]



async def create_stub_entries(arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Create multiple stub entries based on LLM analysis.
    
    Processes a list of stub entries, creating files and optionally
    new taxonomies as needed. Skips existing entries and provides
    comprehensive reporting.
    
    Args:
        arguments: Tool arguments containing world_directory and stub_entries list
        
    Returns:
        List containing summary of created stubs and taxonomies
    """
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]
    
    world_directory = arguments.get("world_directory", "")
    stub_entries = arguments.get("stub_entries", [])
    
    if not world_directory or not stub_entries:
        return [types.TextContent(type="text", text="Error: world_directory and stub_entries are required")]
    
    try:
        world_path = Path(world_directory)
        if not world_path.exists():
            return [types.TextContent(type="text", text=f"Error: World directory {world_directory} does not exist")]
        
        created_stubs = []
        created_taxonomies = []
        
        for stub in stub_entries:
            stub_result = _process_single_stub(world_path, stub)
            if stub_result["created_stub"]:
                created_stubs.append(stub_result["stub_info"])
            if stub_result["created_taxonomy"]:
                created_taxonomies.append(stub_result["taxonomy_name"])
        
        # Generate summary response
        return _create_stub_summary_response(created_stubs, created_taxonomies)
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error creating stub entries: {str(e)}")]


def _clean_name(name: str) -> str:
    """Clean a name for use in file/folder names."""
    return name.lower().replace(" ", "-").replace("_", "-")


def _extract_taxonomy_context(world_path: Path, clean_taxonomy: str) -> str:
    """Extract the description from a taxonomy overview file."""
    taxonomy_overview_path = world_path / "taxonomies" / f"{clean_taxonomy}{TAXONOMY_OVERVIEW_SUFFIX}{MARKDOWN_EXTENSION}"
    
    if not taxonomy_overview_path.exists():
        return ""
    
    try:
        with open(taxonomy_overview_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract the description section
        lines = content.split('\n')
        in_description = False
        description_lines = []
        
        for line in lines:
            if line.strip() == "## Description":
                in_description = True
                continue
            elif line.startswith("## ") and in_description:
                break
            elif in_description and line.strip():
                description_lines.append(line.strip())
        
        return " ".join(description_lines) if description_lines else ""
    except Exception:
        return ""


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


def _generate_stub_analysis(
    world_path: Path, entry_name: str, taxonomy: str, entry_content: str
) -> str:
    """Generate the auto-stub analysis section."""
    try:
        existing_taxonomies = _get_existing_taxonomies(world_path)
        existing_entries = _get_existing_entries_with_descriptions(world_path)
        
        taxonomies_list = "\n".join([f"- {tax}" for tax in existing_taxonomies]) if existing_taxonomies else "- No existing taxonomies found"
        
        # Include descriptions for better context
        if existing_entries:
            entries_list = "\n".join([
                f"- **{entry['name']}** ({entry['taxonomy']}): {entry['description'][:100]}{'...' if len(entry['description']) > 100 else ''}"
                for entry in existing_entries
            ])
        else:
            entries_list = "- No existing entries found"
        
        stub_analysis_prompt = f"""# Auto-Stub Generation Analysis

The entry '{entry_name}' has been successfully created. Now analyzing for potential stub candidates...

## Entry Created
**Name**: {entry_name}
**Taxonomy**: {taxonomy}

**Content**:
{entry_content}

## Available Taxonomies
{taxonomies_list}

## Existing Entries (Don't create stubs for these)
{entries_list}

## Analysis Request
Please identify entities mentioned in this entry that should become new stub entries. For each candidate, provide:

1. **Entity Name**: The name of the entity
2. **Suggested Taxonomy**: Which taxonomy it should belong to (prefer existing taxonomies)
3. **Brief Description**: 1-2 sentences describing what this entity is
4. **Create New Taxonomy**: If suggesting a new taxonomy, set this to true

## Guidelines
- Only suggest entities substantial enough to warrant their own page
- Avoid minor details or passing references
- Focus on proper nouns, significant places, important people, unique items, etc.
- Don't suggest entities that already exist

If you identify stub candidates, use the `create_stub_entries` tool with this format:
```
[{{"name": "Entity Name", "taxonomy": "Suggested Taxonomy", "description": "Brief description", "create_taxonomy": false}}]
```

If no stub candidates are found, simply respond with "No stub candidates identified for this entry."
"""
        
        return f"\n\n## Auto-Stub Analysis\n{stub_analysis_prompt}"
        
    except Exception:
        return ""


def _get_existing_taxonomies(world_path: Path) -> List[str]:
    """Get list of existing taxonomy names."""
    taxonomies_path = world_path / "taxonomies"
    existing_taxonomies = []
    
    if taxonomies_path.exists():
        for taxonomy_file in taxonomies_path.glob(f"*{TAXONOMY_OVERVIEW_SUFFIX}{MARKDOWN_EXTENSION}"):
            taxonomy_name = taxonomy_file.stem.replace(TAXONOMY_OVERVIEW_SUFFIX, "").replace("-", " ").title()
            existing_taxonomies.append(taxonomy_name)
    
    return existing_taxonomies


def _get_existing_entries(world_path: Path) -> List[Dict[str, str]]:
    """Get list of existing entries across all taxonomies."""
    entries_path = world_path / "entries"
    existing_entries = []
    
    if entries_path.exists():
        for taxonomy_dir in entries_path.iterdir():
            if taxonomy_dir.is_dir():
                for entry_file in taxonomy_dir.glob(f"*{MARKDOWN_EXTENSION}"):
                    entry_stem = entry_file.stem.replace("-", " ").title()
                    existing_entries.append({
                        "name": entry_stem,
                        "taxonomy": taxonomy_dir.name.replace("-", " ").title(),
                        "filename": entry_file.stem
                    })
    
    return existing_entries


def _get_existing_entries_with_descriptions(world_path: Path) -> List[Dict[str, str]]:
    """Get list of existing entries with their descriptions for context."""
    entries_path = world_path / "entries"
    existing_entries = []
    
    if entries_path.exists():
        for taxonomy_dir in entries_path.iterdir():
            if taxonomy_dir.is_dir():
                for entry_file in taxonomy_dir.glob(f"*{MARKDOWN_EXTENSION}"):
                    try:
                        with open(entry_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        # Extract frontmatter description or generate one
                        frontmatter, _ = extract_frontmatter(content)
                        description = frontmatter.get("description", "")
                        
                        if not description:
                            description = extract_description_from_content(content, max_words=50)
                        
                        entry_stem = entry_file.stem.replace("-", " ").title()
                        existing_entries.append({
                            "name": entry_stem,
                            "taxonomy": taxonomy_dir.name.replace("-", " ").title(),
                            "description": description,
                            "filename": entry_file.stem
                        })
                    except Exception:
                        # Skip entries we can't read
                        continue
    
    return existing_entries


def _create_analysis_prompt(
    entry_name: str, taxonomy: str, entry_content: str,
    existing_taxonomies: List[str], existing_entries: List[Dict[str, str]]
) -> str:
    """Create the stub candidate analysis prompt."""
    taxonomies_list = "\n".join([f"- {tax}" for tax in existing_taxonomies]) if existing_taxonomies else "- No existing taxonomies found"
    
    # Include descriptions for better context
    if existing_entries:
        entries_list = "\n".join([
            f"- **{entry['name']}** ({entry['taxonomy']}): {entry.get('description', 'No description')[:100]}{'...' if len(entry.get('description', '')) > 100 else ''}"
            for entry in existing_entries
        ])
    else:
        entries_list = "- No existing entries found"
    
    return f"""# Stub Candidate Analysis

## Task
Analyze the following worldbuilding entry and identify entities that should become new stub entries in this world.

## Entry Being Analyzed
**Name**: {entry_name}
**Taxonomy**: {taxonomy}

**Content**:
{entry_content}

## Available Taxonomies
{taxonomies_list}

## Existing Entries (Don't create stubs for these)
{entries_list}

## Your Task
Please identify entities mentioned in this entry that should become new stub entries. For each candidate, specify:

1. **Entity Name**: The name of the entity
2. **Suggested Taxonomy**: Which taxonomy it should belong to (choose from existing taxonomies above, or suggest a new one)
3. **Brief Description**: 1-2 sentences describing what this entity is
4. **Why It Needs a Stub**: Brief explanation of why this deserves its own entry

## Guidelines
- Only suggest entities that are substantial enough to warrant their own page
- Avoid creating stubs for minor details or passing references
- Consider whether each entity could have meaningful content developed about it
- Don't suggest entities that already exist in the world
- Focus on proper nouns, significant places, important people, unique items, etc.
- Prefer existing taxonomies, but suggest new ones if needed

## Response Format
For each stub candidate, use this format:

**Entity Name**: [Name]
**Taxonomy**: [Suggested taxonomy]
**Description**: [1-2 sentence description]
**Justification**: [Why this needs a stub]

If no stub candidates are found, simply respond with "No stub candidates identified."

## Analysis
Please analyze the content above and identify stub candidates:"""


def _process_single_stub(world_path: Path, stub: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single stub entry creation."""
    name = stub.get("name", "")
    taxonomy = stub.get("taxonomy", "")
    description = stub.get("description", "")
    create_taxonomy = stub.get("create_taxonomy", False)
    
    result = {
        "created_stub": False,
        "created_taxonomy": False,
        "stub_info": None,
        "taxonomy_name": None
    }
    
    if not all([name, taxonomy, description]):
        return result
    
    clean_taxonomy = _clean_name(taxonomy)
    clean_name = _clean_name(name)
    
    # Create taxonomy if needed
    if create_taxonomy and not _taxonomy_exists(world_path, clean_taxonomy):
        _create_basic_taxonomy(world_path, taxonomy, clean_taxonomy)
        result["created_taxonomy"] = True
        result["taxonomy_name"] = taxonomy
    
    # Skip if taxonomy doesn't exist and we're not creating it
    if not _taxonomy_exists(world_path, clean_taxonomy):
        return result
    
    # Create stub entry
    entry_path = world_path / "entries" / clean_taxonomy
    entry_path.mkdir(parents=True, exist_ok=True)
    
    entry_file = entry_path / f"{clean_name}{MARKDOWN_EXTENSION}"
    
    # Skip if entry already exists
    if entry_file.exists():
        return result
    
    # Create stub content with frontmatter
    stub_content = f"""# {name}

{description}

---
*This is a stub entry. This {taxonomy.lower()} deserves more detailed development.*

---
*Entry in {taxonomy.title()} taxonomy*
"""
    
    # Add frontmatter with description and article type
    final_stub_content = add_frontmatter_to_content(stub_content, {
        "description": description,
        "article_type": "stub"
    })
    
    with open(entry_file, "w", encoding="utf-8") as f:
        f.write(final_stub_content)
    
    result["created_stub"] = True
    result["stub_info"] = {
        "name": name,
        "taxonomy": taxonomy,
        "file": f"entries/{clean_taxonomy}/{clean_name}{MARKDOWN_EXTENSION}"
    }
    
    return result


def _taxonomy_exists(world_path: Path, clean_taxonomy: str) -> bool:
    """Check if a taxonomy exists."""
    taxonomy_overview_path = world_path / "taxonomies" / f"{clean_taxonomy}{TAXONOMY_OVERVIEW_SUFFIX}{MARKDOWN_EXTENSION}"
    return taxonomy_overview_path.exists()


def _create_basic_taxonomy(world_path: Path, taxonomy: str, clean_taxonomy: str) -> None:
    """Create a basic taxonomy structure."""
    taxonomies_path = world_path / "taxonomies"
    taxonomies_path.mkdir(exist_ok=True)
    
    basic_taxonomy_content = f"""# {taxonomy.title()} - Taxonomy Overview

## Description
{taxonomy.title()} entries in this world.

## Entry Structure for {taxonomy.title()}
Each {taxonomy.lower()} entry should include:

### Required Sections
- **Overview** - Brief description and significance
- **Description** - Detailed explanation of key aspects
- **Relationships** - Connections to other world elements

### Optional Sections
- **History** - Background and development
- **Impact** - Effects on the broader world

## Writing Guidelines
- **Length**: 200-500 words for full entries, 1-2 sentences for stubs
- **Focus**: Emphasize unique characteristics and world connections
- **Relationships**: Connect to other taxonomies where relevant

## Tone and Style
Descriptive and immersive, maintaining consistency with the world's established tone.
"""
    
    taxonomy_file = taxonomies_path / f"{clean_taxonomy}{TAXONOMY_OVERVIEW_SUFFIX}{MARKDOWN_EXTENSION}"
    with open(taxonomy_file, "w", encoding="utf-8") as f:
        f.write(basic_taxonomy_content)
    
    # Create entries folder for taxonomy
    entries_path = world_path / "entries"
    entries_path.mkdir(exist_ok=True)
    taxonomy_entries_path = entries_path / clean_taxonomy
    taxonomy_entries_path.mkdir(exist_ok=True)


def _create_world_context_prompt(
    existing_taxonomies: List[str], existing_entries: List[Dict[str, str]], 
    taxonomy_context: str, world_overview: str, target_taxonomy: str = ""
) -> str:
    """Create a comprehensive world context prompt for entry generation."""
    prompt = """# World Context for Entry Generation

## World Overview
"""
    
    if world_overview:
        prompt += f"{world_overview}\n\n"
    else:
        prompt += "No world overview available.\n\n"
    
    prompt += "## Available Taxonomies\n"
    if existing_taxonomies:
        prompt += "\n".join([f"- **{tax}**" for tax in existing_taxonomies])
        prompt += "\n\n"
    else:
        prompt += "No existing taxonomies found.\n\n"
    
    if target_taxonomy and taxonomy_context:
        prompt += f"## {target_taxonomy} Taxonomy Context\n{taxonomy_context}\n\n"
    
    prompt += "## Existing Entries\n"
    if existing_entries:
        prompt += "Here are the existing entries in this world to help you create consistent, well-connected content:\n\n"
        
        # Group by taxonomy
        by_taxonomy = {}
        for entry in existing_entries:
            tax = entry['taxonomy']
            if tax not in by_taxonomy:
                by_taxonomy[tax] = []
            by_taxonomy[tax].append(entry)
        
        for taxonomy, entries in by_taxonomy.items():
            prompt += f"### {taxonomy}\n"
            for entry in entries:
                # Include file path for static site linking
                clean_taxonomy = taxonomy.lower().replace(" ", "-")
                clean_name = entry['name'].lower().replace(" ", "-")
                site_path = f"/taxonomies/{clean_taxonomy}/entries/{clean_name}"
                prompt += f"- **{entry['name']}**: {entry['description']}\n  *Link as: `[{entry['name']}]({site_path})`*\n"
            prompt += "\n"
    else:
        prompt += "No existing entries found.\n\n"
    
    prompt += """## Guidelines for New Entries
When creating new entries, consider:

1. **Consistency**: How does this entry fit with existing world elements?
2. **Connections**: What relationships exist with other entries?
3. **Uniqueness**: What makes this entry distinctive in this world?
4. **Integration**: How does this connect to the broader world themes?
5. **Linking**: When you mention existing entries, create markdown links using the paths provided above

## Linking Instructions
**IMPORTANT**: When you reference any of the existing entries listed above in your content:
- Use the exact link format provided: `[Entry Name](/taxonomies/taxonomy/entries/entry-name)`
- This creates proper navigation in the static site between related world elements
- **Link sparingly**: Only link when the reference is central to understanding this entry
- Focus on key relationships and major connections, not every mention
- Don't over-link - aim for 2-4 meaningful links per entry at most
- Don't link common words that happen to match entry names
- Skip linking if the reference is just a passing mention or minor detail

## Next Steps
Use this context when generating your new entry content. Reference and link to existing entries where appropriate to create an interconnected world."""
    
    return prompt


def _create_description_generation_prompt(entries: List[Dict[str, str]]) -> str:
    """Create a prompt for the client LLM to generate entry descriptions."""
    prompt = """# Entry Description Generation

## Task
Generate concise descriptions (100 words or less) for the following worldbuilding entries. These descriptions will be used as YAML frontmatter to help provide context when generating new entries.

## Guidelines
- Keep descriptions to 100 words maximum
- Focus on the most essential and distinctive aspects
- Write in a clear, engaging style that captures the essence
- Avoid redundant information already obvious from the title
- Make descriptions useful for someone who needs quick context

## Entries Needing Descriptions

"""
    
    for entry in entries:
        prompt += f"""### {entry['name']} ({entry['taxonomy']})
**File**: {entry['file_path']}

**Content Preview**:
{entry['content']}

**Suggested Description**: [Your 100-word description here]

---

"""
    
    prompt += """## Response Format
For each entry, provide a description in this format:

**{Entry Name}**: [Your concise description]

## Instructions
Please analyze the content previews above and generate appropriate descriptions for each entry."""
    
    return prompt


def _create_stub_summary_response(created_stubs: List[Dict[str, str]], created_taxonomies: List[str]) -> list[types.TextContent]:
    """Create the summary response for stub creation."""
    summary_parts = []
    
    if created_stubs:
        summary_parts.append(f"Created {len(created_stubs)} stub entries:")
        for stub in created_stubs:
            summary_parts.append(f"- {stub['name']} ({stub['taxonomy']})")
    
    if created_taxonomies:
        summary_parts.append(f"\nCreated {len(created_taxonomies)} new taxonomies:")
        for tax in created_taxonomies:
            summary_parts.append(f"- {tax}")
    
    if not summary_parts:
        summary_parts.append("No stub entries were created (all may already exist or have invalid data)")
    
    return [types.TextContent(type="text", text="\n".join(summary_parts))]


# Tool router for entry operations
ENTRY_HANDLERS = {
    "create_world_entry": create_world_entry,
    "identify_stub_candidates": identify_stub_candidates,
    "create_stub_entries": create_stub_entries,
    "add_frontmatter_to_entries": add_frontmatter_to_entries,
    "generate_entry_descriptions": generate_entry_descriptions,
    "apply_entry_descriptions": apply_entry_descriptions,
}


async def handle_entry_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Route entry tool calls to appropriate handlers.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        Tool execution result
        
    Raises:
        ValueError: If tool name is not recognized
    """
    if name not in ENTRY_HANDLERS:
        raise ValueError(f"Unknown entry tool: {name}")
    
    return await ENTRY_HANDLERS[name](arguments)