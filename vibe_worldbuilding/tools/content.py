"""Content management tools for the Vibe Worldbuilding MCP.

This module handles basic file operations like saving, reading, and listing
worldbuilding content files.
"""

import mcp.types as types
from pathlib import Path
from typing import Any


async def save_world_content(arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Save worldbuilding content to a markdown file.
    
    Args:
        arguments: Tool arguments containing filename, content, and optional directory
        
    Returns:
        List containing success/error message
    """
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]
    
    filename = arguments.get("filename", "")
    content = arguments.get("content", "")
    directory = arguments.get("directory", ".")
    
    if not filename or not content:
        return [types.TextContent(type="text", text="Error: Both filename and content are required")]
    
    # Ensure filename has .md extension
    if not filename.endswith(".md"):
        filename += ".md"
    
    # Create directory if it doesn't exist
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    
    # Save the file
    file_path = dir_path / filename
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return [types.TextContent(type="text", text=f"Successfully saved content to {file_path}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error saving file: {str(e)}")]


async def read_world_content(arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Read existing worldbuilding content from a markdown file.
    
    Args:
        arguments: Tool arguments containing filepath
        
    Returns:
        List containing file content or error message
    """
    if not arguments:
        return [types.TextContent(type="text", text="Error: No arguments provided")]
    
    filepath = arguments.get("filepath", "")
    if not filepath:
        return [types.TextContent(type="text", text="Error: filepath is required")]
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return [types.TextContent(type="text", text=f"Content of {filepath}:\n\n{content}")]
    except FileNotFoundError:
        return [types.TextContent(type="text", text=f"Error: File {filepath} not found")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error reading file: {str(e)}")]


async def list_world_files(arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """List all worldbuilding files in a directory.
    
    Args:
        arguments: Tool arguments containing optional directory
        
    Returns:
        List containing file listing or error message
    """
    directory = arguments.get("directory", ".") if arguments else "."
    
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return [types.TextContent(type="text", text=f"Error: Directory {directory} does not exist")]
        
        md_files = list(dir_path.glob("*.md"))
        if not md_files:
            return [types.TextContent(type="text", text=f"No markdown files found in {directory}")]
        
        file_list = "\n".join([f"- {f.name}" for f in sorted(md_files)])
        return [types.TextContent(type="text", text=f"Markdown files in {directory}:\n{file_list}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error listing files: {str(e)}")]


# Tool router for content operations
CONTENT_HANDLERS = {
    "save_world_content": save_world_content,
    "read_world_content": read_world_content,
    "list_world_files": list_world_files,
}


async def handle_content_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Route content tool calls to appropriate handlers.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        Tool execution result
        
    Raises:
        ValueError: If tool name is not recognized
    """
    if name not in CONTENT_HANDLERS:
        raise ValueError(f"Unknown content tool: {name}")
    
    return await CONTENT_HANDLERS[name](arguments)