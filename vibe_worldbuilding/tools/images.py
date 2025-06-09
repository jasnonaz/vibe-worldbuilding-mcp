"""Image generation tools for the Vibe Worldbuilding MCP.

This module handles image generation from markdown content using the FAL API.
Images are automatically organized in the world's centralized images directory.
"""

import mcp.types as types
from pathlib import Path
from typing import Any, Tuple

from ..config import (
    FAL_AVAILABLE, FAL_API_KEY, FAL_API_URL, DEFAULT_IMAGE_STYLE,
    DEFAULT_IMAGE_ASPECT_RATIO, IMAGE_EXTENSION, MAX_DESCRIPTION_LINES
)

if FAL_AVAILABLE:
    import requests


async def generate_image_from_markdown_file(arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Generate an image from a markdown file using FAL Imagen4 API.
    
    Reads a markdown file, extracts title and description content,
    generates an appropriate image prompt, and saves the resulting
    image to the world's organized images directory.
    
    Args:
        arguments: Tool arguments containing filepath, style, and aspect_ratio
        
    Returns:
        List containing success message with image details or error message
    """
    # Validate dependencies and arguments
    if not FAL_AVAILABLE:
        return [types.TextContent(type="text", text="Error: requests library not available. Please install with: pip install requests")]
    
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]
    
    filepath = arguments.get("filepath", "")
    style = arguments.get("style", DEFAULT_IMAGE_STYLE)
    aspect_ratio = arguments.get("aspect_ratio", DEFAULT_IMAGE_ASPECT_RATIO)
    
    if not filepath:
        return [types.TextContent(type="text", text="Error: filepath is required")]
    
    if not FAL_API_KEY:
        return [types.TextContent(type="text", text="Error: FAL_KEY environment variable not set")]
    
    try:
        # Read and analyze the markdown file
        file_path = Path(filepath)
        content = _read_markdown_file(file_path)
        title, description = _extract_content_elements(content)
        
        # Generate image prompt
        prompt = _create_image_prompt(style, title, description)
        
        # Generate image via FAL API
        image_data = await _generate_image_via_fal(prompt, aspect_ratio)
        
        # Save image to organized directory structure
        image_path = _save_image_to_world_structure(file_path, image_data)
        
        # Create success response
        seed_info = f"Seed: {image_data.get('seed', 'unknown')}" if 'seed' in image_data else ""
        
        return [types.TextContent(
            type="text", 
            text=f"Successfully generated image for {filepath}\nSaved to: {image_path}\nPrompt used: {prompt}\nAspect ratio: {aspect_ratio}\n{seed_info}"
        )]
        
    except FileNotFoundError:
        return [types.TextContent(type="text", text=f"Error: File {filepath} not found")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error generating image: {str(e)}")]


def _read_markdown_file(file_path: Path) -> str:
    """Read the content of a markdown file.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def _extract_content_elements(content: str) -> Tuple[str, str]:
    """Extract title and description from markdown content.
    
    Args:
        content: Markdown file content
        
    Returns:
        Tuple of (title, description)
    """
    lines = content.split('\n')
    title = ""
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


def _create_image_prompt(style: str, title: str, description: str) -> str:
    """Create an image generation prompt from content elements.
    
    Args:
        style: Art style for the image
        title: Extracted title from content
        description: Extracted description from content
        
    Returns:
        Complete prompt for image generation
    """
    if title:
        return f"{style} of {title}. {description}"
    else:
        return f"{style}. {description}"


async def _generate_image_via_fal(prompt: str, aspect_ratio: str) -> dict:
    """Generate an image using the FAL API.
    
    Args:
        prompt: Image generation prompt
        aspect_ratio: Desired aspect ratio
        
    Returns:
        API response data including image URL and metadata
        
    Raises:
        Exception: If API request fails or returns no images
    """
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "num_images": 1
    }
    
    response = requests.post(FAL_API_URL, headers=headers, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"FAL API request failed with status {response.status_code}: {response.text}")
    
    result = response.json()
    
    if "images" not in result or not result["images"]:
        raise Exception("No images returned from FAL API")
    
    # Download the image data
    image_url = result["images"][0]["url"]
    image_response = requests.get(image_url)
    
    if image_response.status_code != 200:
        raise Exception(f"Failed to download image from {image_url}")
    
    # Add image data to result
    result["image_data"] = image_response.content
    
    return result


def _save_image_to_world_structure(file_path: Path, image_data: dict) -> Path:
    """Save the generated image to the world's organized directory structure.
    
    Args:
        file_path: Path to the source markdown file
        image_data: Image data and metadata from API
        
    Returns:
        Path where the image was saved
    """
    # Find the world root directory
    world_root = _find_world_root(file_path)
    
    # Create centralized images directory
    images_dir = world_root / "images"
    images_dir.mkdir(exist_ok=True)
    
    # Determine category from file path for organization
    category = _extract_category_from_path(file_path)
    
    # Create final image path
    if category:
        category_dir = images_dir / category
        category_dir.mkdir(exist_ok=True)
        image_filename = f"{file_path.stem}{IMAGE_EXTENSION}"
        image_path = category_dir / image_filename
    else:
        image_filename = f"{file_path.stem}{IMAGE_EXTENSION}"
        image_path = images_dir / image_filename
    
    # Save the image
    with open(image_path, "wb") as f:
        f.write(image_data["image_data"])
    
    return image_path


def _find_world_root(file_path: Path) -> Path:
    """Find the world root directory by looking for README.md and overview folder.
    
    Args:
        file_path: Path to a file within the world
        
    Returns:
        Path to the world root directory
    """
    current = file_path if file_path.is_dir() else file_path.parent
    
    while current != current.parent:
        if (current / "README.md").exists() and (current / "overview").exists():
            return current
        current = current.parent
    
    # Fallback to file's parent directory if world root not found
    return file_path.parent


def _extract_category_from_path(file_path: Path) -> str:
    """Extract category from file path for image organization.
    
    Args:
        file_path: Path to the source file
        
    Returns:
        Category name or empty string if no category found
    """
    file_path_str = str(file_path)
    
    if "/entries/" in file_path_str:
        path_parts = file_path_str.split("/entries/")
        if len(path_parts) > 1:
            category_part = path_parts[1].split("/")[0]
            return category_part
    
    return ""


# Tool router for image operations
IMAGE_HANDLERS = {
    "generate_image_from_markdown_file": generate_image_from_markdown_file,
}


async def handle_image_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Route image tool calls to appropriate handlers.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        Tool execution result
        
    Raises:
        ValueError: If tool name is not recognized
    """
    if name not in IMAGE_HANDLERS:
        raise ValueError(f"Unknown image tool: {name}")
    
    return await IMAGE_HANDLERS[name](arguments)