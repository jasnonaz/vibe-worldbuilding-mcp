"""Utility functions for entry management.

This module contains helper functions used across the entries package
for name cleaning, context extraction, and world analysis.
"""

from pathlib import Path
from typing import Dict, List

from ..config import MARKDOWN_EXTENSION, TAXONOMY_OVERVIEW_SUFFIX


def clean_name(name: str) -> str:
    """Clean a name for use in file/folder names."""
    return name.lower().replace(" ", "-").replace("_", "-")


def extract_taxonomy_context(world_path: Path, clean_taxonomy: str) -> str:
    """Extract the description from a taxonomy overview file."""
    taxonomy_overview_path = (
        world_path
        / "taxonomies"
        / f"{clean_taxonomy}{TAXONOMY_OVERVIEW_SUFFIX}{MARKDOWN_EXTENSION}"
    )

    if not taxonomy_overview_path.exists():
        return ""

    try:
        with open(taxonomy_overview_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract the description section
        lines = content.split("\n")
        in_description = False
        description_lines = []

        for line in lines:
            if line.strip() == "## Description":
                in_description = True
                continue
            elif line.startswith("## ") and in_description:
                break
            elif in_description and line.strip():
                description_lines.append(line.strip())

        return " ".join(description_lines) if description_lines else ""
    except Exception:
        return ""


def get_existing_taxonomies(world_path: Path) -> List[str]:
    """Get a list of existing taxonomies in the world."""
    taxonomies = []
    taxonomies_path = world_path / "taxonomies"

    if taxonomies_path.exists():
        for file_path in taxonomies_path.glob(
            f"*{TAXONOMY_OVERVIEW_SUFFIX}{MARKDOWN_EXTENSION}"
        ):
            taxonomy_name = file_path.stem.replace(TAXONOMY_OVERVIEW_SUFFIX, "")
            taxonomies.append(taxonomy_name)

    return sorted(taxonomies)


def get_existing_entries(world_path: Path) -> List[Dict[str, str]]:
    """Get a list of existing entries in the world."""
    entries = []
    entries_path = world_path / "entries"

    if entries_path.exists():
        for taxonomy_dir in entries_path.iterdir():
            if taxonomy_dir.is_dir():
                for entry_file in taxonomy_dir.glob(f"*{MARKDOWN_EXTENSION}"):
                    entry_name = entry_file.stem.replace("-", " ").title()
                    entries.append(
                        {
                            "name": entry_name,
                            "taxonomy": taxonomy_dir.name,
                            "file": str(entry_file.relative_to(world_path)),
                        }
                    )

    return entries


def get_existing_entries_with_descriptions(world_path: Path) -> List[Dict[str, str]]:
    """Get a list of existing entries with their descriptions."""
    entries = []
    entries_path = world_path / "entries"

    if entries_path.exists():
        for taxonomy_dir in entries_path.iterdir():
            if taxonomy_dir.is_dir():
                for entry_file in taxonomy_dir.glob(f"*{MARKDOWN_EXTENSION}"):
                    try:
                        with open(entry_file, "r", encoding="utf-8") as f:
                            content = f.read()

                        # Extract frontmatter to get description
                        from ..utils.content_parsing import extract_frontmatter

                        frontmatter, _ = extract_frontmatter(content)
                        description = frontmatter.get("description", "")

                        entry_name = entry_file.stem.replace("-", " ").title()
                        entries.append(
                            {
                                "name": entry_name,
                                "taxonomy": taxonomy_dir.name,
                                "description": description,
                                "file": str(entry_file.relative_to(world_path)),
                            }
                        )
                    except Exception:
                        # Skip entries that can't be read
                        continue

    return entries


def create_world_context_prompt(
    existing_taxonomies: List[str],
    existing_entries: List[Dict[str, str]],
    taxonomy_context: str,
    world_overview: str,
    taxonomy: str,
) -> str:
    """Create a comprehensive world context prompt for the LLM."""
    context_lines = []

    # World overview
    if world_overview:
        context_lines.append(f"**World Overview:**\n{world_overview}")

    # Taxonomy context
    if taxonomy_context:
        context_lines.append(f"**Current Taxonomy ({taxonomy}):**\n{taxonomy_context}")

    # Existing taxonomies
    if existing_taxonomies:
        taxonomy_list = ", ".join(existing_taxonomies)
        context_lines.append(f"**Available Taxonomies:** {taxonomy_list}")

    # Existing entries (show first 15 for context)
    if existing_entries:
        entries_by_taxonomy = {}
        for entry in existing_entries:
            tax = entry["taxonomy"]
            if tax not in entries_by_taxonomy:
                entries_by_taxonomy[tax] = []
            entries_by_taxonomy[tax].append(entry)

        context_lines.append("**Existing Entries to Reference:**")
        for tax, entries in sorted(entries_by_taxonomy.items()):
            entry_names = [
                entry["name"] for entry in entries[:5]
            ]  # Limit to 5 per taxonomy
            more_count = len(entries) - 5
            if more_count > 0:
                entry_names.append(f"(+{more_count} more)")
            context_lines.append(f"- **{tax}**: {', '.join(entry_names)}")

    # Writing instructions
    context_lines.append(
        "\n**Writing Guidelines:**\n"
        "• Target 300-400 words unless the story demands more\n"
        "• Use the taxonomy structure as a flexible guide, not a rigid template\n"
        "• Write with personality - mix documentary precision with narrative flair\n"
        "• Include quotes, in-world documents, or interesting perspectives when relevant\n"
        "• Reference existing entries naturally (use exact names for auto-linking)\n"
        "• Focus on vivid details that bring the element to life\n"
        "• Consider unique storytelling angles - scholar's notes, traveler's accounts, conflicting reports"
    )

    return "\n\n".join(context_lines)


def taxonomy_exists(world_path: Path, clean_taxonomy: str) -> bool:
    """Check if a taxonomy exists in the world."""
    entries_dir = world_path / "entries" / clean_taxonomy
    taxonomies_file = (
        world_path
        / "taxonomies"
        / f"{clean_taxonomy}{TAXONOMY_OVERVIEW_SUFFIX}{MARKDOWN_EXTENSION}"
    )
    return entries_dir.exists() or taxonomies_file.exists()


def create_basic_taxonomy(world_path: Path, taxonomy: str, clean_taxonomy: str) -> None:
    """Create a basic taxonomy structure if it doesn't exist."""
    # Create entries directory
    entries_dir = world_path / "entries" / clean_taxonomy
    entries_dir.mkdir(parents=True, exist_ok=True)

    # Create taxonomy overview file
    taxonomies_dir = world_path / "taxonomies"
    taxonomies_dir.mkdir(exist_ok=True)

    taxonomy_file = (
        taxonomies_dir
        / f"{clean_taxonomy}{TAXONOMY_OVERVIEW_SUFFIX}{MARKDOWN_EXTENSION}"
    )
    if not taxonomy_file.exists():
        basic_overview = f"""# {taxonomy.title()} Overview

## Description

This taxonomy contains {taxonomy.lower()} entries for this world.

## Entry Guidelines
These serve as flexible frameworks - adapt to each entry's unique story.

### Core Elements (Include Most)
- **Overview** - Introduction and key characteristics
- **Details** - Expanded information and distinctive features
- **Connections** - Relationships to other world elements

### Additional Elements (Use When Relevant)
- **History** - Background and development over time
- **Perspectives** - Different viewpoints, quotes, or documents
- **Impact** - Influence on the broader world

## Writing Guidelines
- **Length**: Target 300-400 words for initial entries
- **Style**: Mix documentary precision with narrative flair
- **Voice**: Write with personality - include quotes, documents, unique angles
- **Connections**: Reference existing entries naturally for auto-linking
- **Flexibility**: Adapt structure to serve each entry's story

## Writing Philosophy
Prioritize engaging, immersive writing that brings each element to life through vivid details and interesting perspectives.
"""
        with open(taxonomy_file, "w", encoding="utf-8") as f:
            f.write(basic_overview)
