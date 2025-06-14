"""World creation tools for the Vibe Worldbuilding MCP.

This module handles the creation of new world projects with proper directory
structure, content initialization, and optional image generation.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import mcp.types as types

from ..config import (
    DEFAULT_UNIQUE_SUFFIX,
    FAL_API_KEY,
    FAL_API_URL,
    FAL_AVAILABLE,
    IMAGE_EXTENSION,
    MARKDOWN_EXTENSION,
    MAX_DESCRIPTION_LINES,
    WORLD_DIRECTORIES,
)

if FAL_AVAILABLE:
    import requests


async def instantiate_world(
    arguments: dict[str, Any] | None,
) -> list[types.TextContent]:
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
        return [
            types.TextContent(
                type="text",
                text="Error: Both world_name and world_content are required",
            )
        ]

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

        # Generate world visual style as an LLM prompt (integrated workflow)
        visual_style_info = await _generate_world_visual_style(
            world_path, world_name, world_content
        )

        # Generate overview images and favicon if FAL API is available
        image_generation_info = ""
        favicon_info = ""
        if FAL_API_KEY and FAL_AVAILABLE:
            image_generation_info = await _generate_overview_images(
                world_path, world_name, world_content
            )
            favicon_info = await _generate_world_favicon(
                world_path, world_name, world_content
            )

        # Create success response
        return _create_success_response(
            world_name,
            world_path.name,
            world_path,
            created_folders,
            taxonomies,
            visual_style_info + image_generation_info + favicon_info,
        )

    except Exception as e:
        return [
            types.TextContent(
                type="text", text=f"Error creating world structure: {str(e)}"
            )
        ]


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


def _create_world_structure(
    world_name: str, base_directory: str, suffix: str
) -> tuple[Path, list[str]]:
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
        taxonomy_names = [
            t.get("name", "") if isinstance(t, dict) else t for t in taxonomies
        ]
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


async def _generate_overview_images(
    world_path: Path, world_name: str, world_content: str
) -> str:
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
            "Content-Type": "application/json",
        }

        # Extract content elements for consistent image generation
        title, description = _extract_world_content_elements(world_name, world_content)
        
        # Check for stored visual style
        style_file = world_path / "metadata" / "visual_style.txt"
        if style_file.exists():
            with open(style_file, "r", encoding="utf-8") as f:
                world_style = f.read().strip()
            # Use consistent world style for all images
            image_configs = [
                {
                    "name": "header",
                    "prompt": _create_world_image_prompt(world_style, title, description),
                    "image_size": "landscape_16_9",
                    "filename": f"world-overview-header{IMAGE_EXTENSION}",
                },
                {
                    "name": "atmosphere",
                    "prompt": _create_world_image_prompt(world_style, title, description),
                    "image_size": "square_hd",
                    "filename": f"world-overview-atmosphere{IMAGE_EXTENSION}",
                },
                {
                    "name": "concept",
                    "prompt": _create_world_image_prompt(world_style, title, description),
                    "image_size": "square_hd",
                    "filename": f"world-overview-concept{IMAGE_EXTENSION}",
                },
            ]
        else:
            # Generate three different types of images with varied artistic styles
            image_configs = [
                {
                    "name": "header",
                    "prompt": _create_world_image_prompt("epic fantasy book cover art, sweeping landscape", title, description),
                    "image_size": "landscape_16_9",
                    "filename": f"world-overview-header{IMAGE_EXTENSION}",
                },
                {
                    "name": "atmosphere",
                    "prompt": _create_world_image_prompt("atmospheric impressionist painting", title, description),
                    "image_size": "square_hd",
                    "filename": f"world-overview-atmosphere{IMAGE_EXTENSION}",
                },
                {
                    "name": "concept",
                    "prompt": _create_world_image_prompt("detailed concept art", title, description),
                    "image_size": "square_hd",
                    "filename": f"world-overview-concept{IMAGE_EXTENSION}",
                },
            ]

        for config in image_configs:
            success = await _generate_single_image(
                headers,
                config["prompt"],
                config["image_size"],
                world_path / "images" / config["filename"],
            )
            if success:
                image_generation_info += (
                    f"\n- Generated {config['name']} image: {config['filename']}"
                )

    except Exception as e:
        image_generation_info = (
            f"\n\nNote: Image generation attempted but failed: {str(e)}"
        )

    return image_generation_info


def _extract_world_content_elements(world_name: str, world_content: str) -> tuple[str, str]:
    """Extract title and rich description from world content.

    Args:
        world_name: Name of the world
        world_content: World overview content

    Returns:
        Tuple of (title, description) optimized for image prompts
    """
    lines = world_content.split("\n")
    title = world_name  # Use world name as title
    description_lines = []

    for line in lines:
        if line.startswith("# "):
            # Extract title from first header if present
            extracted_title = line[2:].strip()
            if extracted_title:
                title = extracted_title
        elif line.strip() and not line.startswith("#") and not line.startswith("---"):
            description_lines.append(line.strip())
            if len(description_lines) >= 3:  # Allow up to 3 lines for richer detail
                break

    # Join lines and limit to ~35 words for detailed but focused prompts
    description = " ".join(description_lines)
    words = description.split()
    if len(words) > 35:
        description = " ".join(words[:35])
    
    return title, description


def _create_world_image_prompt(style: str, title: str, description: str) -> str:
    """Create a detailed world image prompt.

    Args:
        style: Art style for the image
        title: World title
        description: World description

    Returns:
        Rich prompt for image generation
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


async def _generate_single_image(
    headers: dict, prompt: str, image_size: str, output_path: Path
) -> bool:
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
            "enable_safety_checker": True,
        }

        response = requests.post(FAL_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            if "images" in result and result["images"]:
                image_url = result["images"][0]["url"]
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(image_response.content)
                    return True
    except Exception:
        pass  # Silently fail for individual images

    return False


async def _generate_world_visual_style(
    world_path: Path, world_name: str, world_content: str
) -> str:
    """Generate and store a consistent visual style for the world.

    Args:
        world_path: Path to the world directory
        world_name: Name of the world
        world_content: Content of the world overview

    Returns:
        Information string about visual style generation
    """
    try:
        # Extract themes and mood from world content
        style_elements = _extract_style_elements(world_name, world_content)
        
        # Create LLM prompt for visual style generation
        style_prompt = _create_style_generation_prompt(world_name, style_elements)
        
        # Store the prompt in a metadata file for the LLM to process
        metadata_dir = world_path / "metadata"
        metadata_dir.mkdir(exist_ok=True)
        
        # Save style generation request
        style_request_file = metadata_dir / "visual_style_request.md"
        with open(style_request_file, "w", encoding="utf-8") as f:
            f.write(style_prompt)
        
        return f"\n- Created visual style generation request: metadata/visual_style_request.md\n  → Use the LLM to generate a visual style, then continue with world development"
        
    except Exception as e:
        return f"\n\nNote: Visual style generation failed: {str(e)}"


def _extract_style_elements(world_name: str, world_content: str) -> dict:
    """Extract visual and thematic elements from world content.

    Args:
        world_name: Name of the world
        world_content: World overview content

    Returns:
        Dictionary containing extracted style elements
    """
    lines = world_content.split("\n")
    
    # Extract key descriptive words and themes
    descriptive_words = []
    mood_indicators = []
    setting_elements = []
    
    for line in lines:
        if line.strip() and not line.startswith("#") and not line.startswith("---"):
            words = line.lower().split()
            
            # Look for mood and atmosphere words
            mood_words = [w for w in words if any(mood in w for mood in 
                         ['dark', 'bright', 'ethereal', 'mystical', 'ancient', 'modern', 
                          'vibrant', 'muted', 'dramatic', 'serene', 'chaotic', 'peaceful'])]
            mood_indicators.extend(mood_words)
            
            # Look for setting elements
            setting_words = [w for w in words if any(setting in w for setting in 
                            ['castle', 'city', 'forest', 'desert', 'mountain', 'ocean', 
                             'magical', 'technological', 'medieval', 'futuristic', 'urban', 'rural'])]
            setting_elements.extend(setting_words)
            
            # General descriptive words (adjectives)
            desc_words = [w for w in words if len(w) > 4 and 
                         any(w.endswith(suffix) for suffix in ['ing', 'ous', 'ful', 'ive', 'tic'])]
            descriptive_words.extend(desc_words[:3])  # Limit to prevent overwhelming
    
    return {
        'mood': mood_indicators[:5],  # Top 5 mood indicators
        'setting': setting_elements[:5],  # Top 5 setting elements
        'descriptive': descriptive_words[:5]  # Top 5 descriptive words
    }


def _create_style_generation_prompt(world_name: str, style_elements: dict) -> str:
    """Create a prompt for LLM to generate visual style.

    Args:
        world_name: Name of the world
        style_elements: Extracted style elements from content

    Returns:
        Prompt for visual style generation
    """
    mood_text = ", ".join(style_elements['mood']) if style_elements['mood'] else "balanced"
    setting_text = ", ".join(style_elements['setting']) if style_elements['setting'] else "varied"
    desc_text = ", ".join(style_elements['descriptive']) if style_elements['descriptive'] else "detailed"
    
    return f"""# Visual Style Generation Request for {world_name}

## Extracted Themes
- **Mood Elements**: {mood_text}
- **Setting Elements**: {setting_text}  
- **Descriptive Elements**: {desc_text}

## Task
Please generate a consistent visual style description for all images in this world. This style should be 2-3 sentences that can be prepended to any image prompt to ensure visual consistency.

## Requirements
1. **Artistic Style**: Specify a consistent artistic approach (e.g., "oil painting style", "digital concept art", "watercolor illustrations")
2. **Color Palette**: Define the dominant colors and tones
3. **Lighting & Atmosphere**: Specify consistent lighting mood
4. **Level of Detail**: Define the complexity level (minimalist, detailed, ornate, etc.)
5. **Composition Style**: Note any consistent framing or perspective preferences

## Examples of Good Visual Styles
- "Detailed fantasy oil painting style with rich earth tones and golden accents. Dramatic chiaroscuro lighting with deep shadows and warm highlights."
- "Clean vector art style with a limited palette of blues and whites. Soft, diffused lighting and minimalist composition with plenty of negative space."
- "Gritty photorealistic digital art with desaturated colors and industrial textures. Moody atmospheric lighting with volumetric fog effects."

## Output Format
Respond with ONLY the visual style description (2-3 sentences), nothing else. 

After you provide the style, I will save it to `metadata/visual_style.txt` where it will be automatically used for all image generation in this world.

**World Name**: {world_name}
**Context**: Based on the themes and mood identified above, create a visual style that captures the essence of this world.

**Next Step**: After generating the style description, save it using Claude Code's Write tool to `{world_name}/metadata/visual_style.txt`
"""


async def _generate_world_favicon(
    world_path: Path, world_name: str, world_content: str
) -> str:
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
            "Content-Type": "application/json",
        }

        # Create favicon-specific prompt using world style if available
        style_file = world_path / "metadata" / "visual_style.txt"
        if style_file.exists():
            with open(style_file, "r", encoding="utf-8") as f:
                world_style = f.read().strip()
            favicon_prompt = _create_favicon_prompt_with_style(world_name, world_content, world_style)
        else:
            favicon_prompt = _create_favicon_prompt(world_name, world_content)

        # Generate favicon with proper size constraints
        payload = {
            "prompt": favicon_prompt,
            "image_size": "square_hd",  # 1024x1024 square format
            "num_images": 1,
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "enable_safety_checker": True,
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
                    with open(favicon_path, "wb") as f:
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
    """Create a simple favicon prompt.

    Args:
        world_name: Name of the world
        world_content: Content to analyze for themes

    Returns:
        Simple prompt for favicon generation
    """
    # Extract key theme from first few lines
    lines = world_content.split("\n")
    theme_words = []
    
    for line in lines[:3]:  # Check first 3 lines
        if line.strip() and not line.startswith("#"):
            words = line.split()
            for word in words:
                if len(word) > 4 and word[0].isupper():
                    theme_words.append(word.lower())
            if len(theme_words) >= 2:
                break
    
    # Build simple prompt
    if theme_words:
        theme = theme_words[0]  # Use most prominent theme
        return f"Minimalist {theme} icon symbol. Bold simplified shapes, vector style, no text."
    else:
        return f"Abstract geometric symbol for {world_name}. Minimalist icon, bold silhouette, no text."


def _create_favicon_prompt_with_style(world_name: str, world_content: str, world_style: str) -> str:
    """Create a favicon prompt using the world's visual style.

    Args:
        world_name: Name of the world
        world_content: Content to analyze for themes
        world_style: The world's visual style

    Returns:
        Favicon prompt consistent with world style
    """
    # Extract key theme from first few lines
    lines = world_content.split("\n")
    theme_words = []
    
    for line in lines[:3]:  # Check first 3 lines
        if line.strip() and not line.startswith("#"):
            words = line.split()
            for word in words:
                if len(word) > 4 and word[0].isupper():
                    theme_words.append(word.lower())
            if len(theme_words) >= 2:
                break
    
    # Build prompt incorporating world style
    if theme_words:
        theme = theme_words[0]  # Use most prominent theme
        return f"Minimalist {theme} icon symbol in the style of: {world_style}. Simple, bold favicon design, no text."
    else:
        return f"Abstract geometric symbol for {world_name} in the style of: {world_style}. Simple, bold favicon design, no text."


def _create_success_response(
    world_name: str,
    folder_name: str,
    world_path: Path,
    created_folders: list[str],
    taxonomies: list,
    image_info: str,
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
        taxonomy_names = [
            t.get("name", "") if isinstance(t, dict) else t for t in taxonomies
        ]
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


async def handle_world_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent]:
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
