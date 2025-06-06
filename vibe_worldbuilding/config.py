"""Configuration and constants for the Vibe Worldbuilding MCP."""

import os

# Version information
VERSION = "1.0.0"
SERVER_NAME = "vibe-worldbuilding"

# External API configuration
FAL_API_URL = "https://fal.run/fal-ai/imagen4/preview"
FAL_API_KEY = os.environ.get("FAL_KEY")

# Check for optional dependencies
try:
    import requests
    FAL_AVAILABLE = True
except ImportError:
    FAL_AVAILABLE = False

# Default values
DEFAULT_IMAGE_STYLE = "fantasy illustration"
DEFAULT_IMAGE_ASPECT_RATIO = "1:1"
DEFAULT_SITE_DIR = "site"
DEFAULT_UNIQUE_SUFFIX = "timestamp"

# File extensions and patterns
MARKDOWN_EXTENSION = ".md"
IMAGE_EXTENSION = ".png"

# Directory structure
WORLD_DIRECTORIES = ["overview", "taxonomies", "entries", "images", "notes"]
CONTENT_SYMLINK_DIRS = ["overview", "taxonomies", "entries"]

# Taxonomy naming patterns
TAXONOMY_OVERVIEW_SUFFIX = "-overview"

# Build timeouts and limits
BUILD_TIMEOUT_SECONDS = 300  # 5 minutes
MAX_DESCRIPTION_LINES = 3