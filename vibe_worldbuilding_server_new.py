#!/usr/bin/env python3
"""
New modular Vibe Worldbuilding MCP Server entry point.

This is a simple wrapper that imports and runs the modular server.
"""

from vibe_worldbuilding.server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())