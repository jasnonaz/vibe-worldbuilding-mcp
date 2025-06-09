"""Entry creation and management package for the Vibe Worldbuilding MCP.

This package handles the creation of detailed world entries, automatic stub generation,
and content analysis. It's organized into focused modules for better maintainability.

Public API:
    - create_world_entry: Main entry creation function with integrated stub analysis
    - create_stub_entries: Stub creation from LLM analysis
    - generate_entry_descriptions: LLM-driven batch description generation
    - add_entry_frontmatter: Apply LLM-generated descriptions to entry files
"""

# Import public API functions
from .creation import create_world_entry
from .stub_generation import create_stub_entries
from .content_processing import (
    generate_entry_descriptions,
    add_entry_frontmatter
)

# Re-export for backward compatibility with existing tools/entries.py interface
__all__ = [
    "create_world_entry",
    "create_stub_entries",
    "generate_entry_descriptions",
    "add_entry_frontmatter"
]