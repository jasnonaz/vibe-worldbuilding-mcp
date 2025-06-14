"""Image generation tools for the Vibe Worldbuilding MCP.

This module handles image generation from markdown content using the FAL API.
Images are automatically organized in the world's centralized images directory.
"""

from pathlib import Path
from typing import Any, Tuple

import mcp.types as types

from ..config import (
    DEFAULT_IMAGE_ASPECT_RATIO,
    DEFAULT_IMAGE_STYLE,
    FAL_API_KEY,
    FAL_API_URL,
    FAL_AVAILABLE,
    IMAGE_EXTENSION,
    MAX_DESCRIPTION_LINES,
)
from ..utils.content_parsing import (
    extract_frontmatter,
    add_frontmatter_to_content,
)

if FAL_AVAILABLE:
    import requests


async def generate_image_prompt_for_entry(
    arguments: dict[str, Any] | None,
) -> list[types.TextContent]:
    """Generate or update an optimized image prompt for a world entry.

    This tool reads an entry file and helps generate a 2-sentence image prompt
    optimized for AI image generation. If called without image_prompt, it provides
    guidance for the LLM. If called with image_prompt, it saves it to frontmatter.

    Args:
        arguments: Tool arguments containing filepath and optional image_prompt

    Returns:
        List containing prompt guidance or success message
    """
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]

    filepath = arguments.get("filepath", "")
    if not filepath:
        return [types.TextContent(type="text", text="Error: filepath is required")]

    try:
        # Read the markdown file
        file_path = Path(filepath)
        content = _read_markdown_file(file_path)
        
        # Check if we're saving a prompt
        image_prompt = arguments.get("image_prompt", "")
        if image_prompt:
            # Save mode - add image_prompt to frontmatter
            updated_content = add_frontmatter_to_content(content, {"image_prompt": image_prompt})
            
            # Write back to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Successfully saved image prompt to {filepath} frontmatter"
                )
            ]
        
        # Generate mode - provide guidance for LLM
        # Extract title and key content elements
        title, description = _extract_content_elements(content)
        
        # Extract existing frontmatter to check for image_prompt
        frontmatter, _ = extract_frontmatter(content)
        
        if "image_prompt" in frontmatter:
            return [
                types.TextContent(
                    type="text",
                    text=f"This entry already has an image prompt in frontmatter:\n\n{frontmatter['image_prompt']}"
                )
            ]
        
        # Create prompt for LLM to generate image prompt
        prompt = f"""I need you to create a visually-rich image generation prompt for this world entry.

Entry Title: {title}
Entry Content Preview: {description}

Please create a 2-3 sentence image prompt that:
1. Captures the visual essence and atmosphere of this entry
2. Uses concrete, descriptive language with specific visual details
3. Includes style cues (lighting, mood, artistic approach, color palette)
4. Is optimized for AI image generation with clear composition
5. Is approximately 30-40 words total

IMPORTANT: 
- Focus on what can be SEEN in the image
- Include atmospheric details (lighting, weather, time of day)
- Specify artistic style (e.g., cinematic, painterly, photorealistic)
- Add composition details (close-up, wide shot, dramatic angle)
- Avoid any text/writing in the image
- Make it evocative and richly detailed

Examples of style elements to include:

Lighting & Atmosphere:
- "Golden hour lighting", "Dramatic shadows", "Soft diffused light"
- "Misty atmosphere", "Volumetric fog", "Ethereal glow"

Artistic Styles:
- "Epic fantasy book cover art", "Impressionist painting style"
- "Detailed concept art", "Oil painting technique", "Watercolor style"
- "Photorealistic rendering", "Gothic atmosphere", "Anime art style"

Composition & Details:
- "Dynamic action pose", "Sweeping vista", "Intimate close-up"
- "Ornate details", "Weathered textures", "Intricate patterns"
- "Cinematic composition", "Low angle shot", "Dramatic framing"

Respond with ONLY the image prompt, nothing else."""
        
        return [
            types.TextContent(
                type="text",
                text=prompt
            )
        ]
        
    except FileNotFoundError:
        return [
            types.TextContent(type="text", text=f"Error: File {filepath} not found")
        ]
    except Exception as e:
        return [
            types.TextContent(type="text", text=f"Error: {str(e)}")
        ]


async def generate_image_from_markdown_file(
    arguments: dict[str, Any] | None,
) -> list[types.TextContent]:
    """Generate an image from a markdown file using FAL Imagen4 API.

    Reads a markdown file, uses the image_prompt from frontmatter if available,
    or extracts content to create a prompt, then generates and saves the image.

    Args:
        arguments: Tool arguments containing filepath, style, and aspect_ratio

    Returns:
        List containing success message with image details or error message
    """
    # Validate dependencies and arguments
    if not FAL_AVAILABLE:
        return [
            types.TextContent(
                type="text",
                text="Error: requests library not available. Please install with: pip install requests",
            )
        ]

    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]

    filepath = arguments.get("filepath", "")
    style = arguments.get("style", DEFAULT_IMAGE_STYLE)
    aspect_ratio = arguments.get("aspect_ratio", DEFAULT_IMAGE_ASPECT_RATIO)
    skip_optimization = arguments.get("skip_optimization", False)

    if not filepath:
        return [types.TextContent(type="text", text="Error: filepath is required")]

    if not FAL_API_KEY:
        return [
            types.TextContent(
                type="text", text="Error: FAL_KEY environment variable not set"
            )
        ]

    try:
        # Read and analyze the markdown file
        file_path = Path(filepath)
        content = _read_markdown_file(file_path)
        
        # Get world-level visual style if available - this always takes priority
        world_style = _get_world_visual_style(file_path)
        if world_style:
            # Use world-level style instead of parameter
            style = world_style
        
        # Check for image_prompt in frontmatter first
        frontmatter, _ = extract_frontmatter(content)
        
        if "image_prompt" in frontmatter and frontmatter["image_prompt"]:
            # Use the LLM-generated prompt from frontmatter
            base_prompt = frontmatter["image_prompt"]
            # Use world style if available, otherwise use provided style
            if world_style:
                prompt = f"{world_style}, {base_prompt}"
            else:
                prompt = f"{style}, {base_prompt}" if style != DEFAULT_IMAGE_STYLE else base_prompt
        else:
            # No image_prompt in frontmatter
            if not skip_optimization:
                # Return guidance for creating an optimized prompt
                return [
                    types.TextContent(
                        type="text",
                        text=f"""No optimized image prompt found for {filepath}. 

To generate a better image, first create an optimized prompt:

1. Use the 'generate_image_prompt_for_entry' tool on this file
2. Follow the LLM guidance to create a visually-rich 2-sentence prompt
3. Save the prompt back to the file
4. Then run 'generate_image_from_markdown_file' again

This two-step process ensures higher quality, more evocative images that capture the essence of your world entry.

Alternatively, to proceed with a basic prompt now, add the parameter 'skip_optimization': true"""
                    )
                ]
            else:
                # Fall back to extracting from content
                title, description = _extract_content_elements(content)
                # Use world style if available, otherwise use provided style
                effective_style = world_style if world_style else style
                prompt = _create_image_prompt(effective_style, title, description)

        # Generate image via FAL API
        image_data = await _generate_image_via_fal(prompt, aspect_ratio)

        # Save image to organized directory structure
        image_path = _save_image_to_world_structure(file_path, image_data)

        # Create success response
        seed_info = (
            f"Seed: {image_data.get('seed', 'unknown')}" if "seed" in image_data else ""
        )

        return [
            types.TextContent(
                type="text",
                text=f"Successfully generated image for {filepath}\nSaved to: {image_path}\nPrompt used: {prompt}\nAspect ratio: {aspect_ratio}\n{seed_info}",
            )
        ]

    except FileNotFoundError:
        return [
            types.TextContent(type="text", text=f"Error: File {filepath} not found")
        ]
    except Exception as e:
        return [
            types.TextContent(type="text", text=f"Error generating image: {str(e)}")
        ]


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
    """Extract title and key descriptive text from markdown content.

    Args:
        content: Markdown file content

    Returns:
        Tuple of (title, description) - optimized for image generation
    """
    # Extract content without frontmatter
    frontmatter, content_without_frontmatter = extract_frontmatter(content)
    
    lines = content_without_frontmatter.split("\n")
    title = ""
    description_lines = []

    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.strip() and not line.startswith("#") and not line.startswith("---"):
            description_lines.append(line.strip())
            if len(description_lines) >= 3:  # Allow up to 3 lines for richer context
                break

    # Create description with ~30-35 words for better detail
    description = " ".join(description_lines)
    words = description.split()
    if len(words) > 35:
        description = " ".join(words[:35])
    
    return title, description


def _create_image_prompt(style: str, title: str, description: str) -> str:
    """Create a simple fallback image generation prompt.

    This is only used when no image_prompt exists in frontmatter.
    The preferred approach is to use LLM-generated prompts stored in frontmatter.

    Args:
        style: Art style for the image
        title: Extracted title from content
        description: Extracted description from content

    Returns:
        Simple prompt for image generation
    """
    if title and description:
        prompt = f"{style} of {title}. {description}."
    elif title:
        prompt = f"{style} of {title}."
    elif description:
        prompt = f"{style}. {description}."
    else:
        prompt = f"{style}."
    
    # Clean up any double periods
    return prompt.replace("..", ".")


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
        "Content-Type": "application/json",
    }

    payload = {"prompt": prompt, "aspect_ratio": aspect_ratio, "num_images": 1}

    response = requests.post(FAL_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(
            f"FAL API request failed with status {response.status_code}: {response.text}"
        )

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


def _get_world_visual_style(file_path: Path) -> str:
    """Get the stored visual style for this world.

    Args:
        file_path: Path to a file within the world

    Returns:
        Visual style string, or empty string if not found
    """
    try:
        # Find the world root directory
        world_root = _find_world_root(file_path)
        
        # Look for the stored visual style
        style_file = world_root / "metadata" / "visual_style.txt"
        
        if style_file.exists():
            with open(style_file, "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception:
        pass  # Silently fail and use default style
    
    return ""


# Tool router for image operations
IMAGE_HANDLERS = {
    "generate_image_from_markdown_file": generate_image_from_markdown_file,
    "generate_image_prompt_for_entry": generate_image_prompt_for_entry,
}


async def handle_image_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent]:
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
