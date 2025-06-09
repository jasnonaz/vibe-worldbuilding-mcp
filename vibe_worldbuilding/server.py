"""Main MCP server for the Vibe Worldbuilding system.

This is the entry point that coordinates all the modular components:
prompts, tools, and utilities.
"""

import os
import asyncio
from typing import Any, Sequence

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from .config import SERVER_NAME, VERSION, FAL_AVAILABLE
from .types.schemas import get_all_tools

# Import prompt handlers
from .prompts.core import handle_core_prompt, CORE_PROMPT_HANDLERS
from .prompts.taxonomy import handle_taxonomy_prompt, TAXONOMY_PROMPT_HANDLERS
from .prompts.entries import handle_entry_prompt, ENTRY_PROMPT_HANDLERS
from .prompts.workflow import handle_workflow_prompt, WORKFLOW_PROMPT_HANDLERS

# Import tool handlers
from .tools.world import handle_world_tool, WORLD_HANDLERS
from .tools.taxonomy import handle_taxonomy_tool, TAXONOMY_HANDLERS
from .tools.entries import handle_entry_tool, ENTRY_HANDLERS
from .tools.images import handle_image_tool, IMAGE_HANDLERS
from .tools.site import handle_site_tool, SITE_HANDLERS


# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file if it exists."""
    from pathlib import Path
    
    env_path = Path(__file__).parent.parent / ".env"
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Only set if not already in environment
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = value.strip()


# Load .env file at startup
load_env_file()

# Initialize the MCP server
app = Server(SERVER_NAME)

# All prompt handlers combined
ALL_PROMPT_HANDLERS = {
    **CORE_PROMPT_HANDLERS,
    **TAXONOMY_PROMPT_HANDLERS,
    **ENTRY_PROMPT_HANDLERS,
    **WORKFLOW_PROMPT_HANDLERS,
}

# All tool handlers combined
ALL_TOOL_HANDLERS = {
    **WORLD_HANDLERS,
    **TAXONOMY_HANDLERS,
    **ENTRY_HANDLERS,
    **IMAGE_HANDLERS,
    **SITE_HANDLERS,
}


@app.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """List available worldbuilding prompts."""
    return [
        types.Prompt(
            name="start-worldbuilding",
            description="Begin a new world project with structured guidance",
        ),
        types.Prompt(
            name="continue-worldbuilding",
            description="Resume work on an existing world project",
        ),
        types.Prompt(
            name="world-foundation",
            description="Develop the core concepts and foundation of your world",
        ),
        types.Prompt(
            name="taxonomy",
            description="Create classification systems for world elements",
        ),
        types.Prompt(
            name="world-entry",
            description="Create detailed entries for specific world elements",
        ),
        types.Prompt(
            name="consistency-review",
            description="Check your world for logical consistency and coherence",
        ),
        types.Prompt(
            name="entry-revision",
            description="Revise and improve existing world entries",
        ),
        types.Prompt(
            name="workflow",
            description="Get guidance on the overall worldbuilding process",
        ),
    ]


@app.get_prompt()
async def handle_get_prompt(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
    """Get a specific worldbuilding prompt."""
    if name in CORE_PROMPT_HANDLERS:
        return handle_core_prompt(name)
    elif name in TAXONOMY_PROMPT_HANDLERS:
        return handle_taxonomy_prompt(name)
    elif name in ENTRY_PROMPT_HANDLERS:
        return handle_entry_prompt(name)
    elif name in WORKFLOW_PROMPT_HANDLERS:
        return handle_workflow_prompt(name)
    else:
        raise ValueError(f"Unknown prompt: {name}")


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available worldbuilding tools."""
    return get_all_tools(include_fal_tools=FAL_AVAILABLE)


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Handle tool calls for worldbuilding operations."""
    try:
        # Route to appropriate tool handler based on tool name
        if name in WORLD_HANDLERS:
            return await handle_world_tool(name, arguments)
        elif name in TAXONOMY_HANDLERS:
            return await handle_taxonomy_tool(name, arguments)
        elif name in ENTRY_HANDLERS:
            return await handle_entry_tool(name, arguments)
        elif name in IMAGE_HANDLERS:
            return await handle_image_tool(name, arguments)
        elif name in SITE_HANDLERS:
            return await handle_site_tool(name, arguments)
        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error executing tool '{name}': {str(e)}")]


async def main():
    """Main entry point for the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=SERVER_NAME,
                server_version=VERSION,
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())