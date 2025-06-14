"""Stub generation module for the Vibe Worldbuilding MCP.

This module handles automatic stub entry creation through LLM analysis.
It identifies entities mentioned in content that deserve their own entries
and creates minimal stub entries for future development.
"""

from pathlib import Path
from typing import Any, Dict, List

import mcp.types as types

from ..config import MARKDOWN_EXTENSION
from ..utils.content_parsing import add_frontmatter_to_content
from .utilities import (
    clean_name,
    create_basic_taxonomy,
    get_existing_entries_with_descriptions,
    get_existing_taxonomies,
    taxonomy_exists,
)

# identify_stub_candidates function REMOVED
# This functionality is already built into create_world_entry.
# Stub analysis is automatically provided when creating entries.


async def create_stub_entries(
    arguments: dict[str, Any] | None,
) -> list[types.TextContent]:
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
        return [
            types.TextContent(
                type="text", text="Error: world_directory and stub_entries are required"
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
        return [
            types.TextContent(
                type="text", text=f"Error creating stub entries: {str(e)}"
            )
        ]


def generate_stub_analysis(
    world_path: Path, entry_name: str, taxonomy: str, entry_content: str
) -> str:
    """Generate the auto-stub analysis section for entry creation response."""
    try:
        existing_taxonomies = get_existing_taxonomies(world_path)
        existing_entries = get_existing_entries_with_descriptions(world_path)

        # Create a concise analysis prompt
        analysis_info = f"""

## 🔗 Auto-Stub Analysis Available

The system has analyzed "{entry_name}" and can identify entities that might deserve their own entries.

**Available for Reference:**
- Taxonomies: {', '.join(existing_taxonomies) if existing_taxonomies else 'None'}
- Existing Entries: {len(existing_entries)} entries across {len(set(entry['taxonomy'] for entry in existing_entries))} taxonomies

**To generate stubs:** Use the `identify_stub_candidates` tool with this entry's content to get LLM analysis of potential stub candidates, then use `create_stub_entries` to create them."""

        return analysis_info

    except Exception:
        return ""


def _create_analysis_prompt(
    entry_name: str,
    taxonomy: str,
    entry_content: str,
    existing_taxonomies: List[str],
    existing_entries: List[Dict[str, str]],
) -> str:
    """Create the stub candidate analysis prompt."""
    taxonomies_list = (
        "\n".join([f"- {tax}" for tax in existing_taxonomies])
        if existing_taxonomies
        else "- No existing taxonomies found"
    )

    # Include descriptions for better context
    if existing_entries:
        entries_list = "\n".join(
            [
                f"- **{entry['name']}** ({entry['taxonomy']}): {entry.get('description', 'No description')[:100]}{'...' if len(entry.get('description', '')) > 100 else ''}"
                for entry in existing_entries
            ]
        )
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
        "taxonomy_name": None,
    }

    if not all([name, taxonomy, description]):
        return result

    clean_taxonomy = clean_name(taxonomy)
    clean_entry_name = clean_name(name)

    # Create taxonomy if needed
    if create_taxonomy and not taxonomy_exists(world_path, clean_taxonomy):
        create_basic_taxonomy(world_path, taxonomy, clean_taxonomy)
        result["created_taxonomy"] = True
        result["taxonomy_name"] = taxonomy

    # Skip if taxonomy doesn't exist and we're not creating it
    if not taxonomy_exists(world_path, clean_taxonomy):
        return result

    # Create stub entry
    entry_path = world_path / "entries" / clean_taxonomy
    entry_path.mkdir(parents=True, exist_ok=True)

    entry_file = entry_path / f"{clean_entry_name}{MARKDOWN_EXTENSION}"

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
    final_stub_content = add_frontmatter_to_content(
        stub_content, {"description": description, "article_type": "stub"}
    )

    with open(entry_file, "w", encoding="utf-8") as f:
        f.write(final_stub_content)

    result["created_stub"] = True
    result["stub_info"] = {
        "name": name,
        "taxonomy": taxonomy,
        "file": f"entries/{clean_taxonomy}/{clean_entry_name}{MARKDOWN_EXTENSION}",
    }

    return result


def _create_stub_summary_response(
    created_stubs: List[Dict[str, str]], created_taxonomies: List[str]
) -> list[types.TextContent]:
    """Create summary response for stub creation."""
    if not created_stubs and not created_taxonomies:
        return [
            types.TextContent(
                type="text",
                text="No new stub entries or taxonomies were created. All suggested entities may already exist.",
            )
        ]

    response_parts = []

    if created_taxonomies:
        taxonomies_list = ", ".join(created_taxonomies)
        response_parts.append(f"**New Taxonomies Created:** {taxonomies_list}")

    if created_stubs:
        response_parts.append(f"**Stub Entries Created:** {len(created_stubs)}")
        for stub in created_stubs:
            response_parts.append(
                f"- **{stub['name']}** ({stub['taxonomy']}): {stub['file']}"
            )

    response_text = "# Stub Creation Summary\n\n" + "\n\n".join(response_parts)
    response_text += "\n\n*These stub entries provide a foundation for future content development. Each can be expanded with more detailed information as the world grows.*"

    return [types.TextContent(type="text", text=response_text)]
