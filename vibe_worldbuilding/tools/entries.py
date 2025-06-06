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
    
    if not all([world_directory, taxonomy, entry_name, entry_content]):
        return [types.TextContent(type="text", text="Error: All parameters (world_directory, taxonomy, entry_name, entry_content) are required")]
    
    try:
        world_path = Path(world_directory)
        if not world_path.exists():
            return [types.TextContent(type="text", text=f"Error: World directory {world_directory} does not exist")]
        
        # Clean names for file system use
        clean_taxonomy = _clean_name(taxonomy)
        clean_entry = _clean_name(entry_name)
        
        # Extract taxonomy context if available
        taxonomy_context = _extract_taxonomy_context(world_path, clean_taxonomy)
        
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
        
        # Create response
        relative_path = str(entry_file.relative_to(world_path))
        context_info = f"\n\nTaxonomy context included: {taxonomy_context[:100]}..." if taxonomy_context else "\n\nNo taxonomy overview found for reference."
        
        return [types.TextContent(
            type="text",
            text=f"Successfully created entry '{entry_name}' in {taxonomy} taxonomy!\n\nSaved to: {relative_path}{context_info}\n\nThe entry includes:\n1. Automatic reference to the taxonomy overview\n2. Your detailed content\n3. Taxonomy classification footer{image_info}{stub_analysis_info}"
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
        existing_entries = _get_existing_entries(world_path)
        
        # Create analysis prompt
        analysis_prompt = _create_analysis_prompt(
            entry_name, taxonomy, entry_content, existing_taxonomies, existing_entries
        )
        
        return [types.TextContent(type="text", text=analysis_prompt)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error analyzing entry for stub candidates: {str(e)}")]


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
    """Create the entry file with proper formatting."""
    entry_path = world_path / "entries" / clean_taxonomy
    entry_path.mkdir(parents=True, exist_ok=True)
    
    entry_file = entry_path / f"{clean_entry}{MARKDOWN_EXTENSION}"
    
    # Add taxonomy context header if available
    header = ""
    if taxonomy_context:
        header = f"""---
taxonomyContext: "{taxonomy_context}"
---

"""
    
    final_content = f"""{header}{entry_content}

---
*Entry in {taxonomy.title()} taxonomy*
"""
    
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
        existing_entries = _get_existing_entries(world_path)
        
        taxonomies_list = "\n".join([f"- {tax}" for tax in existing_taxonomies]) if existing_taxonomies else "- No existing taxonomies found"
        entries_list = "\n".join([f"- {entry['name']} ({entry['taxonomy']})" for entry in existing_entries]) if existing_entries else "- No existing entries found"
        
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


def _create_analysis_prompt(
    entry_name: str, taxonomy: str, entry_content: str,
    existing_taxonomies: List[str], existing_entries: List[Dict[str, str]]
) -> str:
    """Create the stub candidate analysis prompt."""
    taxonomies_list = "\n".join([f"- {tax}" for tax in existing_taxonomies]) if existing_taxonomies else "- No existing taxonomies found"
    entries_list = "\n".join([f"- {entry['name']} ({entry['taxonomy']})" for entry in existing_entries]) if existing_entries else "- No existing entries found"
    
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
    
    # Create stub content
    stub_content = f"""# {name}

{description}

---
*This is a stub entry. This {taxonomy.lower()} deserves more detailed development.*

---
*Entry in {taxonomy.title()} taxonomy*
"""
    
    with open(entry_file, "w", encoding="utf-8") as f:
        f.write(stub_content)
    
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