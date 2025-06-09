"""World creation tools for the Vibe Worldbuilding MCP.

This module handles the creation of new world projects with proper directory
structure, content initialization, and optional image generation.
"""

import mcp.types as types
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config import (
    FAL_AVAILABLE, FAL_API_KEY, FAL_API_URL, WORLD_DIRECTORIES,
    DEFAULT_UNIQUE_SUFFIX, MARKDOWN_EXTENSION, IMAGE_EXTENSION
)

if FAL_AVAILABLE:
    import requests


async def instantiate_world(arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Create basic folder structure for a new world project.
    
    Creates a uniquely named world directory with standard structure,
    saves the world overview content, generates a README, and optionally
    creates initial images.
    
    Args:
        arguments: Tool arguments containing world_name, world_content, and options
        
    Returns:
        List containing success message with project details
    """
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]
    
    world_name = arguments.get("world_name", "")
    world_content = arguments.get("world_content", "")
    taxonomies = arguments.get("taxonomies", [])
    base_directory = arguments.get("base_directory", ".")
    unique_suffix = arguments.get("unique_suffix", DEFAULT_UNIQUE_SUFFIX)
    
    if not world_name or not world_content:
        return [types.TextContent(type="text", text="Error: Both world_name and world_content are required")]
    
    try:
        # Generate unique suffix for world folder
        suffix = _generate_unique_suffix(unique_suffix)
        
        # Create world directory structure
        world_path, created_folders = _create_world_structure(
            world_name, base_directory, suffix
        )
        
        # Save world overview content
        overview_file = world_path / "overview" / f"world-overview{MARKDOWN_EXTENSION}"
        with open(overview_file, "w", encoding="utf-8") as f:
            f.write(world_content)
        created_folders.append(str(overview_file.relative_to(Path(base_directory))))
        
        # Create project README
        readme_file = _create_world_readme(world_path, world_name, taxonomies)
        created_folders.append(str(readme_file.relative_to(Path(base_directory))))
        
        # Generate overview images and favicon if FAL API is available
        image_generation_info = ""
        favicon_info = ""
        if FAL_API_KEY and FAL_AVAILABLE:
            image_generation_info = await _generate_overview_images(world_path, world_name, world_content)
            favicon_info = await _generate_world_favicon(world_path, world_name, world_content)
        
        # Create success response
        return _create_success_response(
            world_name, world_path.name, world_path, created_folders, 
            taxonomies, image_generation_info + favicon_info
        )
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error creating world structure: {str(e)}")]


def _generate_unique_suffix(suffix_type: str) -> str:
    """Generate a unique suffix for the world folder name.
    
    Args:
        suffix_type: Type of suffix ("timestamp", "uuid", "short-uuid")
        
    Returns:
        Generated suffix string
    """
    if suffix_type == "timestamp":
        return datetime.now().strftime("%Y%m%d-%H%M%S")
    elif suffix_type == "uuid":
        return str(uuid.uuid4())
    elif suffix_type == "short-uuid":
        return str(uuid.uuid4())[:8]
    else:
        # Fallback to timestamp
        return datetime.now().strftime("%Y%m%d-%H%M%S")


def _create_world_structure(world_name: str, base_directory: str, suffix: str) -> tuple[Path, list[str]]:
    """Create the basic world directory structure.
    
    Args:
        world_name: Name of the world
        base_directory: Base directory to create world in
        suffix: Unique suffix for folder name
        
    Returns:
        Tuple of (world_path, list_of_created_folders)
    """
    base_path = Path(base_directory)
    clean_world_name = world_name.lower().replace(" ", "-")
    unique_folder_name = f"{clean_world_name}-{suffix}"
    world_path = base_path / unique_folder_name
    world_path.mkdir(parents=True, exist_ok=True)
    
    created_folders = []
    
    # Create main world folders
    for folder in WORLD_DIRECTORIES:
        folder_path = world_path / folder
        folder_path.mkdir(exist_ok=True)
        created_folders.append(str(folder_path.relative_to(base_path)))
    
    return world_path, created_folders


def _create_world_readme(world_path: Path, world_name: str, taxonomies: list) -> Path:
    """Create a comprehensive README for the world project.
    
    Args:
        world_path: Path to the world directory
        world_name: Name of the world
        taxonomies: List of initial taxonomies
        
    Returns:
        Path to the created README file
    """
    taxonomies_text = ""
    if taxonomies:
        taxonomy_names = [t.get("name", "") if isinstance(t, dict) else t for t in taxonomies]
        taxonomies_text = f"\n\n## Initial Taxonomies\n\n{chr(10).join(f'- **{name}**: Ready for development' for name in taxonomy_names)}\n"
    
    readme_content = f"""# {world_name}

This directory contains all the worldbuilding content for **{world_name}**.

## Directory Structure

- **overview/**: Core world documents and foundation
- **taxonomies/**: Classification systems and category definitions  
- **entries/**: Detailed entries for specific world elements
- **images/**: Generated and reference images
- **notes/**: Development notes and work-in-progress content{taxonomies_text}

## Getting Started

1. Review your world overview in `overview/world-overview.md`
2. Use the `create_taxonomy_folders` tool to add new taxonomies as needed
3. Define your taxonomies and create detailed entries
4. Generate images to visualize key concepts

## Taxonomy Development

As you develop your world, you'll identify key categories that need systematic development. Use the worldbuilding MCP to:
- Create folders for new taxonomies as they emerge
- Maintain consistency across related elements
- Build comprehensive classification systems

---
*World structure created by Vibe Worldbuilding MCP*
"""
    
    readme_file = world_path / f"README{MARKDOWN_EXTENSION}"
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    return readme_file


async def _generate_overview_images(world_path: Path, world_name: str, world_content: str) -> str:
    """Generate overview images for the world using FAL API.
    
    Args:
        world_path: Path to the world directory
        world_name: Name of the world
        world_content: Content of the world overview
        
    Returns:
        Information string about generated images
    """
    if not FAL_AVAILABLE:
        return ""
    
    image_generation_info = ""
    
    try:
        headers = {
            "Authorization": f"Key {FAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Generate three different types of images
        image_configs = [
            {
                "name": "header",
                "prompt": _create_header_prompt(world_name, world_content),
                "image_size": "landscape_16_9",
                "filename": f"world-overview-header{IMAGE_EXTENSION}"
            },
            {
                "name": "atmosphere",
                "prompt": f"Atmospheric detail from {world_name}, focusing on mood and environment, detailed fantasy illustration",
                "image_size": "square_hd",
                "filename": f"world-overview-atmosphere{IMAGE_EXTENSION}"
            },
            {
                "name": "concept",
                "prompt": f"Key concept visualization from {world_name}, detailed fantasy illustration",
                "image_size": "square_hd",
                "filename": f"world-overview-concept{IMAGE_EXTENSION}"
            }
        ]
        
        for config in image_configs:
            success = await _generate_single_image(
                headers, config["prompt"], config["image_size"],
                world_path / "images" / config["filename"]
            )
            if success:
                image_generation_info += f"\n- Generated {config['name']} image: {config['filename']}"
                
    except Exception as e:
        image_generation_info = f"\n\nNote: Image generation attempted but failed: {str(e)}"
    
    return image_generation_info


def _create_header_prompt(world_name: str, world_content: str) -> str:
    """Create an appropriate header image prompt based on world content.
    
    Args:
        world_name: Name of the world
        world_content: Content to analyze for themes
        
    Returns:
        Generated prompt for header image
    """
    base_prompt = f"Epic wide landscape of {world_name}, fantasy digital art, cinematic composition"
    content_lower = world_content.lower()
    
    if "desert" in content_lower:
        return f"Epic desert landscape with futuristic elements, {world_name}, vast dunes and hidden technology, cinematic sci-fi art"
    elif "forest" in content_lower:
        return f"Mystical forest landscape, {world_name}, ancient trees and magical atmosphere, fantasy digital art"
    elif "city" in content_lower or "urban" in content_lower:
        return f"Futuristic cityscape, {world_name}, towering structures and advanced technology, cyberpunk digital art"
    else:
        return f"{base_prompt}, cinematic digital art"


async def _generate_single_image(headers: dict, prompt: str, image_size: str, output_path: Path) -> bool:
    """Generate a single image using the FAL API.
    
    Args:
        headers: HTTP headers for the API request
        prompt: Image generation prompt
        image_size: FAL API image size parameter
        output_path: Where to save the generated image
        
    Returns:
        True if successful, False otherwise
    """
    try:
        payload = {
            "prompt": prompt,
            "image_size": image_size,
            "num_images": 1,
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "enable_safety_checker": True
        }
        
        response = requests.post(FAL_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if "images" in result and result["images"]:
                image_url = result["images"][0]["url"]
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(image_response.content)
                    return True
    except Exception:
        pass  # Silently fail for individual images
    
    return False


async def _generate_world_favicon(world_path: Path, world_name: str, world_content: str) -> str:
    """Generate a custom favicon for the world using FAL API.
    
    Args:
        world_path: Path to the world directory
        world_name: Name of the world
        world_content: Content of the world overview
        
    Returns:
        Information string about favicon generation
    """
    if not FAL_AVAILABLE:
        return ""
    
    try:
        headers = {
            "Authorization": f"Key {FAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Create favicon-specific prompt
        favicon_prompt = _create_favicon_prompt(world_name, world_content)
        
        # Generate favicon with proper size constraints
        payload = {
            "prompt": favicon_prompt,
            "image_size": "square_hd",  # 1024x1024 square format
            "num_images": 1,
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "enable_safety_checker": True
        }
        
        response = requests.post(FAL_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if "images" in result and result["images"]:
                image_url = result["images"][0]["url"]
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    # Save favicon in the images directory
                    favicon_path = world_path / "images" / "favicon.png"
                    with open(favicon_path, 'wb') as f:
                        f.write(image_response.content)
                    
                    return "\n- Generated custom favicon: favicon.png"
                else:
                    return f"\n\nNote: Favicon image download failed: HTTP {image_response.status_code}"
            else:
                return f"\n\nNote: Favicon generation failed: No images in API response"
        else:
            return f"\n\nNote: Favicon generation failed: API returned HTTP {response.status_code} - {response.text[:200]}"
                    
    except Exception as e:
        return f"\n\nNote: Favicon generation attempted but failed: {str(e)}"
    
    return "\n\nNote: Favicon generation failed: Unknown error"


def _create_favicon_prompt(world_name: str, world_content: str) -> str:
    """Create a favicon prompt based on world content.
    
    Args:
        world_name: Name of the world
        world_content: Content to analyze for themes
        
    Returns:
        Generated prompt for favicon image
    """
    # Get first 200 characters of world content for context
    world_summary = world_content[:200].strip()
    
    return (
        f"Simple geometric icon symbol for '{world_name}' world. "
        f"Context: {world_summary}. "
        f"REQUIREMENTS: NO TEXT, pure symbol only, minimalist geometric design, "
        f"single central icon, high contrast silhouette, simple shapes, "
        f"recognizable at tiny sizes, solid colors only, favicon style, "
        f"professional web icon, vector-like flat design"
    )


def _create_success_response(
    world_name: str, folder_name: str, world_path: Path, 
    created_folders: list[str], taxonomies: list, image_info: str
) -> list[types.TextContent]:
    """Create the success response message.
    
    Args:
        world_name: Name of the world
        folder_name: Generated folder name
        world_path: Full path to world directory
        created_folders: List of created folders/files
        taxonomies: List of initial taxonomies
        image_info: Information about generated images
        
    Returns:
        Success response as TextContent list
    """
    folder_list = "\n".join([f"- {folder}" for folder in sorted(created_folders)])
    
    if taxonomies:
        taxonomy_names = [t.get("name", "") if isinstance(t, dict) else t for t in taxonomies]
        taxonomy_info = f"\n\nInitial taxonomies created: {', '.join(taxonomy_names)}"
    else:
        taxonomy_info = "\n\nNo initial taxonomies created. Use 'create_taxonomy_folders' to add them as needed."
    
    message = (
        f"Successfully instantiated '{world_name}' world project!\n\n"
        f"Project folder: {folder_name}\n"
        f"Full path: {world_path}\n\n"
        f"Created structure:\n{folder_list}{taxonomy_info}{image_info}\n\n"
        f"Next steps:\n"
        f"1. Review your world overview\n"
        f"2. Create additional taxonomy folders as needed\n"
        f"3. Begin creating detailed entries\n"
        f"4. Generate images for key concepts"
    )
    
    return [types.TextContent(type="text", text=message)]


# Tool router for world operations
WORLD_HANDLERS = {
    "instantiate_world": instantiate_world,
}


async def handle_world_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Route world tool calls to appropriate handlers.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        Tool execution result
        
    Raises:
        ValueError: If tool name is not recognized
    """
    if name not in WORLD_HANDLERS:
        raise ValueError(f"Unknown world tool: {name}")
    
    return await WORLD_HANDLERS[name](arguments)