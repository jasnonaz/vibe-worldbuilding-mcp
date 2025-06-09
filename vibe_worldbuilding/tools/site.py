"""Static site generation tools for the Vibe Worldbuilding MCP.

This module handles building static websites from worldbuilding content using Astro.
It manages the complex symlink operations needed to bridge world project structure
with Astro's expected content layout.
"""

import mcp.types as types
import subprocess
import shutil
from pathlib import Path
from typing import Any, List

from ..config import (
    DEFAULT_SITE_DIR, BUILD_TIMEOUT_SECONDS, CONTENT_SYMLINK_DIRS
)


async def build_static_site(arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Build a static website for a specific world using Astro.
    
    Supports three actions:
    - 'build': Generate static files in the world's site directory
    - 'dev': Set up development environment with symlinks
    - 'preview': Provide instructions for serving built site
    
    Args:
        arguments: Tool arguments containing world_directory, action, and site_dir
        
    Returns:
        List containing success/error message and instructions
    """
    if not arguments:
        return [types.TextContent(type="text", text="Error: world_directory is required")]
    
    world_directory = arguments.get("world_directory", "")
    action = arguments.get("action", "build")
    site_dir = arguments.get("site_dir", DEFAULT_SITE_DIR)
    
    if not world_directory:
        return [types.TextContent(type="text", text="Error: world_directory is required")]
    
    try:
        # Validate environment and world directory
        world_path, script_dir = _validate_build_environment(world_directory)
        
        if action == "build":
            return await _handle_build_action(world_path, script_dir, site_dir)
        elif action == "dev":
            return _handle_dev_action(world_path, script_dir)
        elif action == "preview":
            return _handle_preview_action(world_path, site_dir)
        else:
            return [types.TextContent(type="text", text=f"Unknown action: {action}. Use 'build', 'dev', or 'preview'.")]
            
    except subprocess.TimeoutExpired:
        return [types.TextContent(type="text", text="Build timed out after 5 minutes. Your project might be too large or there may be an issue with the build process.")]
    except FileNotFoundError:
        return [types.TextContent(type="text", text="Error: npm not found. Make sure Node.js and npm are installed on your system.")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error building static site: {str(e)}")]


def _validate_build_environment(world_directory: str) -> tuple[Path, Path]:
    """Validate the build environment and world directory.
    
    Args:
        world_directory: Path to the world directory
        
    Returns:
        Tuple of (world_path, script_dir)
        
    Raises:
        Exception: If validation fails
    """
    # Validate world directory exists
    world_path = Path(world_directory)
    if not world_path.exists():
        raise Exception(f"Error: World directory {world_directory} does not exist")
    
    # Check if it's a valid world directory (has overview folder)
    overview_path = world_path / "overview"
    if not overview_path.exists():
        raise Exception(f"Error: {world_directory} is not a valid world directory (no overview folder found)")
    
    # Get the directory where this script is located (should be the project root)
    script_dir = Path(__file__).parent.parent.parent.absolute()
    
    # Check if we're in the right directory (should have astro.config.mjs)
    astro_config_path = script_dir / "astro.config.mjs"
    if not astro_config_path.exists():
        raise Exception(f"Error: astro.config.mjs not found in {script_dir}. Make sure Astro is configured in the project directory.")
    
    # Check if node_modules exists
    node_modules_path = script_dir / "node_modules"
    if not node_modules_path.exists():
        raise Exception(f"Error: node_modules not found in {script_dir}. Run 'npm install' first.")
    
    return world_path, script_dir


async def _handle_build_action(world_path: Path, script_dir: Path, site_dir: str) -> list[types.TextContent]:
    """Handle the build action for static site generation.
    
    Args:
        world_path: Path to the world directory
        script_dir: Path to the project root directory
        site_dir: Name of the site directory
        
    Returns:
        List containing build result message
    """
    world_name = world_path.name
    
    # Set up symlinks for build
    temp_world_link = _setup_world_symlink(script_dir, world_path, world_name)
    _setup_content_symlinks(script_dir, world_path)
    _setup_public_images(script_dir, world_path, world_name)
    
    try:
        # Build the static site
        result = subprocess.run(
            ["npm", "run", "build"],
            capture_output=True,
            text=True,
            timeout=BUILD_TIMEOUT_SECONDS,
            cwd=script_dir
        )
        
        if result.returncode == 0:
            return _handle_successful_build(script_dir, world_path, world_name, site_dir)
        else:
            return [types.TextContent(
                type="text",
                text=f"Build failed with exit code {result.returncode}\n\nErrors:\n{result.stderr}\n\nOutput:\n{result.stdout}"
            )]
    finally:
        # Clean up all temporary files and symlinks
        _cleanup_build_artifacts(script_dir, world_name, temp_world_link)


def _handle_dev_action(world_path: Path, script_dir: Path) -> list[types.TextContent]:
    """Handle the dev action for development environment setup.
    
    Args:
        world_path: Path to the world directory
        script_dir: Path to the project root directory
        
    Returns:
        List containing development setup instructions
    """
    world_name = world_path.name
    
    # Set up symlinks for development
    _setup_world_symlink(script_dir, world_path, world_name)
    _setup_content_symlinks(script_dir, world_path)
    
    return [types.TextContent(
        type="text",
        text=f"✅ Development setup ready for {world_name}!\n\nTo start the development server:\n1. Open a terminal in {script_dir}\n2. Run: npm run dev\n3. Open http://localhost:4321\n\nNote: The world has been temporarily linked for development. The symlink will be cleaned up when you build the site."
    )]


def _handle_preview_action(world_path: Path, site_dir: str) -> list[types.TextContent]:
    """Handle the preview action for serving built sites.
    
    Args:
        world_path: Path to the world directory
        site_dir: Name of the site directory
        
    Returns:
        List containing preview instructions
    """
    site_path = world_path / site_dir
    if not site_path.exists():
        return [types.TextContent(
            type="text",
            text=f"No built site found in {site_path}. Run the build action first."
        )]
    
    return [types.TextContent(
        type="text",
        text=f"To preview the built site for {world_path.name}:\n\n1. Navigate to: {site_path}\n2. Run: python -m http.server 8000\n3. Open: http://localhost:8000\n\nOr use any other static file server of your choice."
    )]


def _setup_world_symlink(script_dir: Path, world_path: Path, world_name: str) -> Path:
    """Set up a temporary symlink to the world directory.
    
    Args:
        script_dir: Path to the project root directory
        world_path: Path to the world directory
        world_name: Name of the world
        
    Returns:
        Path to the created symlink
    """
    temp_world_link = script_dir / world_name
    
    # Remove existing symlink if it exists
    if temp_world_link.exists() or temp_world_link.is_symlink():
        if temp_world_link.is_symlink():
            temp_world_link.unlink()
        else:
            shutil.rmtree(temp_world_link)
    
    # Create symlink to the world directory
    temp_world_link.symlink_to(world_path.absolute())
    
    return temp_world_link


def _setup_content_symlinks(script_dir: Path, world_path: Path) -> None:
    """Set up symlinks for content directories that Astro expects.
    
    Args:
        script_dir: Path to the project root directory
        world_path: Path to the world directory
    """
    content_dir = script_dir / "src" / "content"
    content_dir.mkdir(parents=True, exist_ok=True)
    
    # Create symlinks for the content directories
    for link_name in CONTENT_SYMLINK_DIRS:
        link_path = content_dir / link_name
        source_path = world_path / link_name
        
        # Remove existing symlink if it exists
        if link_path.exists() or link_path.is_symlink():
            if link_path.is_symlink():
                link_path.unlink()
            else:
                shutil.rmtree(link_path)
        
        # Create symlink if source exists
        if source_path.exists():
            link_path.symlink_to(source_path.absolute())


def _setup_public_images(script_dir: Path, world_path: Path, world_name: str) -> None:
    """Copy images and favicon to the public directory for the build.
    
    Args:
        script_dir: Path to the project root directory
        world_path: Path to the world directory
        world_name: Name of the world
    """
    world_images_path = world_path / "images"
    public_images_path = script_dir / "public" / "images" / world_name
    
    if world_images_path.exists():
        # Remove existing public images for this world
        if public_images_path.exists():
            shutil.rmtree(public_images_path)
        
        # Copy images to public directory
        shutil.copytree(world_images_path, public_images_path)
        
        # Copy favicon to public root if it exists
        favicon_source = world_images_path / "favicon.png"
        if favicon_source.exists():
            favicon_dest = script_dir / "public" / "favicon.png"
            shutil.copy2(favicon_source, favicon_dest)


def _handle_successful_build(script_dir: Path, world_path: Path, world_name: str, site_dir: str) -> list[types.TextContent]:
    """Handle a successful build by moving files and counting assets.
    
    Args:
        script_dir: Path to the project root directory
        world_path: Path to the world directory
        world_name: Name of the world
        site_dir: Name of the site directory
        
    Returns:
        List containing success message with build details
    """
    # Move the built site from dist to the world's site directory
    source_dist = script_dir / "dist"
    target_site = world_path / site_dir
    
    # Remove existing site directory if it exists
    if target_site.exists():
        shutil.rmtree(target_site)
    
    # Move the built site
    if source_dist.exists():
        shutil.move(str(source_dist), str(target_site))
        
        # Count generated files
        html_files = list(target_site.rglob("*.html"))
        asset_files = list(target_site.rglob("*.css")) + list(target_site.rglob("*.js"))
        
        return [types.TextContent(
            type="text",
            text=f"✅ Static site built successfully for {world_name}!\n\nSite location: {target_site.absolute()}\nGenerated {len(html_files)} HTML pages and {len(asset_files)} asset files.\n\nTo serve the site locally:\n- Navigate to {target_site}\n- Run 'python -m http.server 8000' or any static file server\n- Open http://localhost:8000"
        )]
    else:
        return [types.TextContent(
            type="text",
            text="Build completed but dist directory not found. This may indicate a build configuration issue."
        )]


def _cleanup_build_artifacts(script_dir: Path, world_name: str, temp_world_link: Path) -> None:
    """Clean up all temporary files and symlinks created during build.
    
    Args:
        script_dir: Path to the project root directory
        world_name: Name of the world
        temp_world_link: Path to the temporary world symlink
    """
    # Clean up the temporary symlink
    if temp_world_link.exists() or temp_world_link.is_symlink():
        temp_world_link.unlink()
    
    # Clean up public images
    public_images_path = script_dir / "public" / "images" / world_name
    if public_images_path.exists():
        shutil.rmtree(public_images_path)
    
    # Clean up content symlinks
    content_dir = script_dir / "src" / "content"
    for link_name in CONTENT_SYMLINK_DIRS:
        link_path = content_dir / link_name
        if link_path.exists() or link_path.is_symlink():
            if link_path.is_symlink():
                link_path.unlink()
            else:
                shutil.rmtree(link_path)


# Tool router for site operations
SITE_HANDLERS = {
    "build_static_site": build_static_site,
}


async def handle_site_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Route site tool calls to appropriate handlers.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        Tool execution result
        
    Raises:
        ValueError: If tool name is not recognized
    """
    if name not in SITE_HANDLERS:
        raise ValueError(f"Unknown site tool: {name}")
    
    return await SITE_HANDLERS[name](arguments)