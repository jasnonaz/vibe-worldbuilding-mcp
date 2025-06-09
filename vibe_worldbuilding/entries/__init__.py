"""Entry creation and management package for the Vibe Worldbuilding MCP.

This package handles the creation of detailed world entries, automatic stub generation,
and content analysis. It's organized into focused modules for better maintainability.

Public API:
    - create_world_entry: Main entry creation function
    - identify_stub_candidates: Auto-stub analysis  
    - create_stub_entries: Stub creation
    - generate_entry_descriptions: Batch description generation
    - add_frontmatter_to_entries: Add metadata to entries
    - apply_entry_descriptions: Apply generated descriptions
"""

# Import public API functions
from .creation import create_world_entry
from .stub_generation import identify_stub_candidates, create_stub_entries
from .content_processing import (
    generate_entry_descriptions,
    add_frontmatter_to_entries, 
    apply_entry_descriptions
)

# Re-export for backward compatibility with existing tools/entries.py interface
__all__ = [
    "create_world_entry",
    "identify_stub_candidates", 
    "create_stub_entries",
    "generate_entry_descriptions",
    "add_frontmatter_to_entries",
    "apply_entry_descriptions"
]