"""Entry tools router for the Vibe Worldbuilding MCP.

This module provides the main tool handler interface for entry operations,
delegating to the appropriate specialized modules in the entries package.
"""

from typing import Any

import mcp.types as types

from ..entries.consistency import analyze_world_consistency
from ..entries.content_processing import (
    add_entry_frontmatter,
    generate_entry_descriptions,
)
from ..entries.creation import create_world_entry
from ..entries.stub_generation import create_stub_entries

# Tool router for entry operations
ENTRY_HANDLERS = {
    "create_world_entry": create_world_entry,
    "create_stub_entries": create_stub_entries,
    "generate_entry_descriptions": generate_entry_descriptions,
    "add_entry_frontmatter": add_entry_frontmatter,
    "analyze_world_consistency": analyze_world_consistency,
}


async def handle_entry_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent]:
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
