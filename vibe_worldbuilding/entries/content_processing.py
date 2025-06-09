"""Content processing module for the Vibe Worldbuilding MCP.

This module handles batch operations on entry content including description generation,
frontmatter management, and content analysis. It focuses on LLM-driven content
enhancement following the system's design principles.
"""

import mcp.types as types
from pathlib import Path
from typing import Any, Dict, List

from ..config import MARKDOWN_EXTENSION
from ..utils.content_parsing import (
    extract_frontmatter, add_frontmatter_to_content, extract_description_from_content
)


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


# add_frontmatter_to_entries function REMOVED
# This conflicted with LLM-first design principles.
# Use generate_entry_descriptions + add_entry_frontmatter workflow instead.

async def add_entry_frontmatter(arguments: dict[str, Any] | None) -> list[types.TextContent]:
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
        return [types.TextContent(type="text", text=f"Error adding entry frontmatter: {str(e)}")]


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