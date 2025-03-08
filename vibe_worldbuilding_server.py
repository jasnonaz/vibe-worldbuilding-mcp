#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Vibe Worldbuilding MCP Server
This MCP server provides prompts for creating and managing a fictional world through worldbuilding.
"""

from mcp.server.fastmcp import FastMCP
from pathlib import Path
import os

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
    return "Worldbuilding initialized! Let's begin your worldbuilding journey.\n\nI'll now ask you for details about your world concept, and then help you create the following:\n\n1. A world foundation document with your core world concept\n2. Taxonomy documents that classify the major elements\n3. Individual entries for specific elements of your world\n\nWhat kind of world would you like to create? Please describe the theme, concept, or key features."

# Run the server if executed directly
if __name__ == "__main__":
    mcp.run()
