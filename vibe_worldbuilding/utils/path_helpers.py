"""Path manipulation and validation utilities.

This module provides utilities for cleaning, validating, and manipulating
file paths used throughout the worldbuilding system.
"""

import re
from pathlib import Path
from typing import List, Optional


def clean_name_for_filesystem(name: str) -> str:
    """Clean a name to be safe for use in file and directory names.

    Args:
        name: Raw name to clean

    Returns:
        Cleaned name suitable for filesystem use
    """
    # Convert to lowercase and replace spaces/underscores with hyphens
    cleaned = name.lower().replace(" ", "-").replace("_", "-")

    # Remove or replace problematic characters
    cleaned = re.sub(r"[^\w\-.]", "", cleaned)

    # Remove multiple consecutive hyphens
    cleaned = re.sub(r"-+", "-", cleaned)

    # Remove leading/trailing hyphens
    cleaned = cleaned.strip("-")

    return cleaned


def extract_name_from_filename(file_path: Path) -> str:
    """Extract a display name from a filename.

    Args:
        file_path: Path to extract name from

    Returns:
        Display name with proper capitalization
    """
    # Get stem (filename without extension)
    stem = file_path.stem

    # Remove common suffixes
    stem = stem.replace("-overview", "")

    # Replace hyphens with spaces and title case
    return stem.replace("-", " ").title()


def find_world_root_directory(start_path: Path) -> Optional[Path]:
    """Find the world root directory by looking for identifying markers.

    Args:
        start_path: Path to start searching from

    Returns:
        Path to world root directory, or None if not found
    """
    current = start_path if start_path.is_dir() else start_path.parent

    while current != current.parent:
        # Look for world directory markers
        if (current / "README.md").exists() and (current / "overview").exists():
            return current
        current = current.parent

    return None


def extract_category_from_entry_path(file_path: Path) -> Optional[str]:
    """Extract taxonomy category from an entry file path.

    Args:
        file_path: Path to an entry file

    Returns:
        Category name, or None if not found
    """
    path_str = str(file_path)

    if "/entries/" in path_str:
        parts = path_str.split("/entries/")
        if len(parts) > 1:
            category_part = parts[1].split("/")[0]
            return category_part

    return None


def build_relative_path(base_path: Path, target_path: Path) -> str:
    """Build a relative path string from base to target.

    Args:
        base_path: Base directory path
        target_path: Target file/directory path

    Returns:
        Relative path as string
    """
    try:
        return str(target_path.relative_to(base_path))
    except ValueError:
        # If paths are not related, return absolute path
        return str(target_path)


def ensure_file_extension(file_path: Path, extension: str) -> Path:
    """Ensure a file path has the specified extension.

    Args:
        file_path: Original file path
        extension: Extension to ensure (with or without leading dot)

    Returns:
        Path with the correct extension
    """
    if not extension.startswith("."):
        extension = "." + extension

    if not str(file_path).endswith(extension):
        return file_path.with_suffix(extension)

    return file_path


def validate_world_directory(directory_path: Path) -> bool:
    """Validate that a directory is a proper world directory.

    Args:
        directory_path: Path to validate

    Returns:
        True if valid world directory, False otherwise
    """
    if not directory_path.exists() or not directory_path.is_dir():
        return False

    # Check for required subdirectories
    required_dirs = ["overview", "taxonomies", "entries"]
    for required_dir in required_dirs:
        if not (directory_path / required_dir).exists():
            return False

    return True


def get_taxonomy_name_from_overview_file(file_path: Path) -> Optional[str]:
    """Extract taxonomy name from an overview file path.

    Args:
        file_path: Path to taxonomy overview file

    Returns:
        Taxonomy name, or None if not a valid overview file
    """
    stem = file_path.stem
    if stem.endswith("-overview"):
        taxonomy_name = stem.replace("-overview", "")
        return extract_name_from_filename(Path(taxonomy_name))

    return None


def build_entry_file_path(
    world_path: Path, taxonomy: str, entry_name: str, extension: str = ".md"
) -> Path:
    """Build the full file path for an entry.

    Args:
        world_path: Path to the world directory
        taxonomy: Taxonomy name
        entry_name: Entry name
        extension: File extension

    Returns:
        Complete path to the entry file
    """
    clean_taxonomy = clean_name_for_filesystem(taxonomy)
    clean_entry = clean_name_for_filesystem(entry_name)

    return world_path / "entries" / clean_taxonomy / f"{clean_entry}{extension}"


def build_taxonomy_overview_path(
    world_path: Path, taxonomy: str, extension: str = ".md"
) -> Path:
    """Build the full file path for a taxonomy overview.

    Args:
        world_path: Path to the world directory
        taxonomy: Taxonomy name
        extension: File extension

    Returns:
        Complete path to the taxonomy overview file
    """
    clean_taxonomy = clean_name_for_filesystem(taxonomy)

    return world_path / "taxonomies" / f"{clean_taxonomy}-overview{extension}"


def list_taxonomy_directories(world_path: Path) -> List[str]:
    """List all taxonomy directories in a world.

    Args:
        world_path: Path to the world directory

    Returns:
        List of taxonomy names
    """
    entries_path = world_path / "entries"
    if not entries_path.exists():
        return []

    taxonomies = []
    for item in entries_path.iterdir():
        if item.is_dir():
            taxonomy_name = extract_name_from_filename(item)
            taxonomies.append(taxonomy_name)

    return sorted(taxonomies)
