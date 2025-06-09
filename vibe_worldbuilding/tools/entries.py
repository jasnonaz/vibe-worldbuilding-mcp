"""Entry tools router for the Vibe Worldbuilding MCP.

This module provides the main tool handler interface for entry operations,
delegating to the appropriate specialized modules in the entries package.
"""

import mcp.types as types
from typing import Any

from ..entries.creation import create_world_entry
from ..entries.stub_generation import create_stub_entries
from ..entries.content_processing import (
    generate_entry_descriptions, add_entry_frontmatter
)



# Tool router for entry operations
ENTRY_HANDLERS = {
    "create_world_entry": create_world_entry,
    "create_stub_entries": create_stub_entries,
    "generate_entry_descriptions": generate_entry_descriptions,
    "add_entry_frontmatter": add_entry_frontmatter,
}


async def handle_entry_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Route entry tool calls to appropriate handlers.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        Tool execution result
        
    Raises:
        ValueError: If tool name is not recognized
    """
    if name not in ENTRY_HANDLERS:
        raise ValueError(f"Unknown entry tool: {name}")
    
    return await ENTRY_HANDLERS[name](arguments)


# Tool router for entry operations
ENTRY_HANDLERS = {
    "create_world_entry": create_world_entry,
    "identify_stub_candidates": identify_stub_candidates,
    "create_stub_entries": create_stub_entries,
    "add_frontmatter_to_entries": add_frontmatter_to_entries,
    "generate_entry_descriptions": generate_entry_descriptions,
    "apply_entry_descriptions": apply_entry_descriptions,
}


async def handle_entry_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Route entry tool calls to appropriate handlers.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        Tool execution result
        
    Raises:
        ValueError: If tool name is not recognized
    """
    if name not in ENTRY_HANDLERS:
        raise ValueError(f"Unknown entry tool: {name}")
    
    return await ENTRY_HANDLERS[name](arguments)