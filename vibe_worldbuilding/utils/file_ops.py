"""File system operation utilities for the Vibe Worldbuilding MCP.

This module provides common file system operations used across
the worldbuilding tools, with consistent error handling and validation.
"""

from pathlib import Path
from typing import Optional, List


def ensure_directory_exists(directory_path: Path) -> None:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Raises:
        OSError: If directory cannot be created
    """
    directory_path.mkdir(parents=True, exist_ok=True)


def safe_read_file(file_path: Path, encoding: str = "utf-8") -> str:
    """Safely read a file with proper error handling.
    
    Args:
        file_path: Path to the file to read
        encoding: Text encoding to use
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file cannot be decoded with specified encoding
        OSError: If file cannot be read due to permissions or other issues
    """
    with open(file_path, "r", encoding=encoding) as f:
        return f.read()


def safe_write_file(file_path: Path, content: str, encoding: str = "utf-8") -> None:
    """Safely write content to a file with proper error handling.
    
    Args:
        file_path: Path to the file to write
        content: Content to write
        encoding: Text encoding to use
        
    Raises:
        OSError: If file cannot be written due to permissions or other issues
    """
    # Ensure parent directory exists
    ensure_directory_exists(file_path.parent)
    
    with open(file_path, "w", encoding=encoding) as f:
        f.write(content)


def find_files_by_pattern(directory: Path, pattern: str) -> List[Path]:
    """Find files matching a glob pattern in a directory.
    
    Args:
        directory: Directory to search in
        pattern: Glob pattern to match
        
    Returns:
        List of matching file paths, sorted by name
        
    Raises:
        OSError: If directory cannot be accessed
    """
    if not directory.exists():
        return []
    
    return sorted(directory.glob(pattern))


def find_directories_by_pattern(directory: Path, pattern: str) -> List[Path]:
    """Find directories matching a glob pattern in a directory.
    
    Args:
        directory: Directory to search in
        pattern: Glob pattern to match
        
    Returns:
        List of matching directory paths, sorted by name
        
    Raises:
        OSError: If directory cannot be accessed
    """
    if not directory.exists():
        return []
    
    return sorted([p for p in directory.glob(pattern) if p.is_dir()])


def file_exists_and_readable(file_path: Path) -> bool:
    """Check if a file exists and is readable.
    
    Args:
        file_path: Path to check
        
    Returns:
        True if file exists and is readable, False otherwise
    """
    try:
        return file_path.exists() and file_path.is_file() and file_path.stat().st_size >= 0
    except OSError:
        return False


def copy_file_contents(source: Path, destination: Path) -> None:
    """Copy contents from source file to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Raises:
        FileNotFoundError: If source file doesn't exist
        OSError: If files cannot be read/written
    """
    content = safe_read_file(source)
    safe_write_file(destination, content)


def get_file_size(file_path: Path) -> Optional[int]:
    """Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes, or None if file doesn't exist or can't be accessed
    """
    try:
        return file_path.stat().st_size
    except OSError:
        return None


def remove_file_safely(file_path: Path) -> bool:
    """Safely remove a file if it exists.
    
    Args:
        file_path: Path to the file to remove
        
    Returns:
        True if file was removed or didn't exist, False if removal failed
    """
    try:
        if file_path.exists():
            file_path.unlink()
        return True
    except OSError:
        return False


def create_symlink_safely(source: Path, link_path: Path) -> bool:
    """Safely create a symbolic link.
    
    Args:
        source: Path to the source file/directory
        link_path: Path where the symlink should be created
        
    Returns:
        True if symlink was created successfully, False otherwise
    """
    try:
        # Remove existing link if it exists
        if link_path.exists() or link_path.is_symlink():
            if link_path.is_symlink():
                link_path.unlink()
            else:
                # If it's a regular file/directory, don't remove it
                return False
        
        # Create the symlink
        link_path.symlink_to(source.absolute())
        return True
    except OSError:
        return False