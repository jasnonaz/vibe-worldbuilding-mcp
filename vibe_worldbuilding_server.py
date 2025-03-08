#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Vibe Worldbuilding MCP Server
This MCP server provides prompts for creating and managing a fictional world through worldbuilding.
"""

from mcp.server.fastmcp import FastMCP
from pathlib import Path
import os
import datetime
import shutil

# Initialize the MCP server
mcp = FastMCP("Vibe Worldbuilding", dependencies=["markdown"])

# Base directory for our MCP
BASE_DIR = Path(__file__).parent.absolute()

@mcp.prompt(name="start-worldbuilding")
def start_worldbuilding() -> str:
    """Start the worldbuilding process for your fictional world."""
    with open(BASE_DIR / "prompts" / "start_worldbuilding.md", "r", encoding="utf-8") as f:
        return f.read()

@mcp.prompt(name="continue-worldbuilding")
def continue_worldbuilding() -> str:
    """Continue developing your fictional world from where you left off."""
    with open(BASE_DIR / "prompts" / "continue_worldbuilding.md", "r", encoding="utf-8") as f:
        return f.read()

@mcp.prompt(name="world-foundation")
def world_foundation() -> str:
    """Create the foundational concept for your fictional world."""
    with open(BASE_DIR / "prompts" / "world_foundation.md", "r", encoding="utf-8") as f:
        return f.read()

@mcp.prompt(name="taxonomy")
def taxonomy() -> str:
    """Create a taxonomy category for your fictional world."""
    with open(BASE_DIR / "prompts" / "taxonomy.md", "r", encoding="utf-8") as f:
        return f.read()

@mcp.prompt(name="world-entry")
def world_entry(entry_type: str = "") -> str:
    """
    Create a new world entry.
    
    Args:
        entry_type: Optional type of entry (person, place, event, artifact, concept)
    """
    with open(BASE_DIR / "prompts" / "world_entry.md", "r", encoding="utf-8") as f:
        content = f.read()
        
    if entry_type:
        # Highlight the selected entry type in the prompt
        content += f"\n\nFocus on creating a {entry_type} entry using the template above."
        
    return content

@mcp.prompt(name="consistency-review")
def consistency_review() -> str:
    """Review world entries for logical consistency."""
    with open(BASE_DIR / "prompts" / "consistency_review.md", "r", encoding="utf-8") as f:
        return f.read()

@mcp.prompt(name="entry-revision")
def entry_revision() -> str:
    """Revise an existing world entry."""
    with open(BASE_DIR / "prompts" / "entry_revision.md", "r", encoding="utf-8") as f:
        return f.read()

@mcp.prompt(name="workflow")
def workflow() -> str:
    """Learn about the recommended workflow for building your world."""
    with open(BASE_DIR / "prompts" / "workflow.md", "r", encoding="utf-8") as f:
        return f.read()

@mcp.tool()
def start_worldbuilding() -> str:
    """
    Initialize the worldbuilding process.
    """
    # Create a timestamp-based world directory name that will be used until renamed
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    world_dir_name = f"World_{timestamp}"
    
    # Get user's desktop path (this is an estimation - in a real implementation,
    # you would use a more robust method or make this configurable)
    desktop_path = Path.home() / "Desktop"
    
    # Create the base world directory
    world_dir = desktop_path / world_dir_name
    os.makedirs(world_dir, exist_ok=True)
    
    # Create standard subdirectories
    subdirs = [
        "World_Foundation",
        "Taxonomies",
        "Elements"
    ]
    
    for subdir in subdirs:
        os.makedirs(world_dir / subdir, exist_ok=True)
    
    # Create placeholder README files with instructions
    with open(world_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(f"# {world_dir_name}\n\nThis directory contains your worldbuilding project. The structure will be filled as you develop your world concept.\n\n"
                f"## Directory Structure\n\n"
                f"- **World_Foundation/**: Core concepts and foundational elements of your world\n"
                f"- **Taxonomies/**: Classification systems for the major elements of your world\n"
                f"- **Elements/**: Detailed entries for specific items, people, places, etc. in your world")
    
    with open(world_dir / "World_Foundation" / "README.md", "w", encoding="utf-8") as f:
        f.write("# World Foundation\n\nThis directory will contain the core concepts and foundational elements of your world.\n\n"
                "After you provide your world concept, we'll create:\n\n"
                "- `core_concept.md`: The central idea of your world\n"
                "- `world_overview.md`: A comprehensive overview of your world's setting\n"
                "- Other foundational documents as needed")
    
    # Return a message to the user
    return f"Worldbuilding initialized! I've created the basic file structure at: {world_dir}\n\n" \
           f"I'll now ask you for details about your world concept, and then help you populate the following:\n\n" \
           f"1. A world foundation document with your core world concept\n" \
           f"2. Taxonomy documents that classify the major elements\n" \
           f"3. Individual entries for specific elements of your world\n\n" \
           f"What kind of world would you like to create? Please describe the theme, concept, or key features."

# Run the server if executed directly
if __name__ == "__main__":
    mcp.run()
