#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Vibe Worldbuilding MCP Server
This MCP server provides prompts for creating and managing a fictional world through worldbuilding.
"""

from mcp.server.fastmcp import FastMCP
from pathlib import Path
import os
import re
from google import genai
from google.genai import types

# Initialize the MCP server
mcp = FastMCP("Vibe Worldbuilding", dependencies=["markdown", "google-generativeai"])

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
    # Create images directory
    images_dir = BASE_DIR / "images"
    if not images_dir.exists():
        os.makedirs(images_dir)
        
    # Create simplified directory structure
    # Create Taxonomies directory
    taxonomies_dir = BASE_DIR / "Taxonomies"
    if not taxonomies_dir.exists():
        os.makedirs(taxonomies_dir)
        
    # Create Entries directory
    entries_dir = BASE_DIR / "Entries"
    if not entries_dir.exists():
        os.makedirs(entries_dir)
    
    # Check if world-overview.md already exists
    world_overview_path = BASE_DIR / "world-overview.md"
    if world_overview_path.exists():
        return "Worldbuilding already started! Your world structure is ready to use.\n\n⭐ IMPORTANT: Begin your message with 'Use the continue-worldbuilding prompt' to load worldbuilding context."
    
    # Create an empty world-overview file as a placeholder
    with open(world_overview_path, "w", encoding="utf-8") as f:
        f.write("# World Overview\n\nThis document will contain the core overview of your world, including:\n\n- Concept (what makes your world unique)\n- Physical characteristics (geography, climate)\n- Major features (regions, distinctive landmarks)\n- Intelligent life (species, races, civilizations)\n- Technology or magic (core systems)\n- Historical epochs (major time periods)")
    
    return "Worldbuilding initialized! Your world structure is now ready.\n\n⭐ IMPORTANT: Begin your next message with 'Use the continue-worldbuilding prompt' to properly continue this project."

@mcp.tool()
def generate_image_from_markdown_file(file_path: str) -> str:
    """
    Generate an image based on the content of a markdown file and save it to disk.
    
    Args:
        file_path: Path to the markdown file to generate an image for
    
    Returns:
        Path to the saved image file
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' not found."
        
        # Create images directory if it doesn't exist
        images_dir = os.path.join(os.path.dirname(file_path), "images")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        
        # Read the markdown file
        with open(file_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
        
        # Extract title (first heading)
        title_match = re.search(r"^# (.+)$", markdown_content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
        else:
            title = os.path.basename(file_path).replace(".md", "")
        
        # Extract the first few paragraphs for context
        paragraphs = re.findall(r"(?:^|\n\n)([^\n#].+?)(?:\n\n|$)", markdown_content)
        description = " ".join(paragraphs[:3]) if paragraphs else title
        
        # Create a prompt for image generation
        image_prompt = f"Create a highly detailed, fantasy-style illustration for '{title}'. {description}"
        
        # Truncate prompt if it's too long
        if len(image_prompt) > 500:
            image_prompt = image_prompt[:497] + "..."
        
        # Retrieve the API key from the environment
        api_key = os.getenv("IMAGEN_API_KEY")
        if not api_key:
            return "Error: Please set the IMAGEN_API_KEY environment variable."
        
        # Initialize the Imagen client
        client = genai.Client(api_key=api_key)
        
        # Call the Imagen API to generate the image
        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=image_prompt,
            config=types.GenerateImagesConfig(number_of_images=1)
        )
        
        # Extract the generated image
        image_bytes = response.generated_images[0].image.image_bytes
        
        # Save the image
        image_file_name = title.replace(" ", "_").lower() + ".png"
        image_path = os.path.join(images_dir, image_file_name)
        
        with open(image_path, "wb") as f:
            f.write(image_bytes)
        
        return f"Successfully generated and saved image for '{title}' to {image_path}. To view the image, you can upload it or open it with a file viewer."
        
    except Exception as e:
        return f"Error generating image: {str(e)}"

# Run the server if executed directly
if __name__ == "__main__":
    mcp.run()
