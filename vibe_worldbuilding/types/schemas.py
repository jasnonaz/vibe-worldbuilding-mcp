"""MCP tool schemas for the Vibe Worldbuilding server.

This module contains all the type definitions and input schemas for MCP tools,
organized by functional category for easy maintenance and testing.
"""

import mcp.types as types


# Content Management Tools
SAVE_WORLD_CONTENT_SCHEMA = types.Tool(
    name="save_world_content",
    description="Save worldbuilding content to a markdown file",
    inputSchema={
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Name of the file to save (without .md extension)"
            },
            "content": {
                "type": "string",
                "description": "Markdown content to save"
            },
            "directory": {
                "type": "string",
                "description": "Directory to save in (default: current directory)",
                "default": "."
            }
        },
        "required": ["filename", "content"]
    }
)

READ_WORLD_CONTENT_SCHEMA = types.Tool(
    name="read_world_content",
    description="Read existing worldbuilding content from a markdown file",
    inputSchema={
        "type": "object",
        "properties": {
            "filepath": {
                "type": "string",
                "description": "Path to the markdown file to read"
            }
        },
        "required": ["filepath"]
    }
)

LIST_WORLD_FILES_SCHEMA = types.Tool(
    name="list_world_files",
    description="List all worldbuilding files in a directory",
    inputSchema={
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Directory to list files from (default: current directory)",
                "default": "."
            }
        }
    }
)


# World Creation Tools
INSTANTIATE_WORLD_SCHEMA = types.Tool(
    name="instantiate_world",
    description="Create basic folder structure for a new world project",
    inputSchema={
        "type": "object",
        "properties": {
            "world_name": {
                "type": "string",
                "description": "Name of the world (used for base directory naming)"
            },
            "world_content": {
                "type": "string",
                "description": "The world overview/foundation content to save"
            },
            "taxonomies": {
                "type": "array",
                "description": "List of initial taxonomy objects with name and description",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name of the taxonomy"},
                        "description": {"type": "string", "description": "Description of how this taxonomy applies to the world"}
                    },
                    "required": ["name", "description"]
                },
                "default": []
            },
            "base_directory": {
                "type": "string",
                "description": "Base directory to create the world structure in (default: current directory)",
                "default": "."
            },
            "unique_suffix": {
                "type": "string",
                "description": "Type of unique suffix to add to world folder name",
                "enum": ["timestamp", "uuid", "short-uuid"],
                "default": "timestamp"
            }
        },
        "required": ["world_name", "world_content"]
    }
)


# Taxonomy Tools
GENERATE_TAXONOMY_GUIDELINES_SCHEMA = types.Tool(
    name="generate_taxonomy_guidelines",
    description="Generate structured entry guidelines for a specific taxonomy type",
    inputSchema={
        "type": "object",
        "properties": {
            "taxonomy_name": {
                "type": "string",
                "description": "Name of the taxonomy to create guidelines for"
            },
            "taxonomy_description": {
                "type": "string",
                "description": "Description of how this taxonomy applies to the world"
            }
        },
        "required": ["taxonomy_name", "taxonomy_description"]
    }
)

CREATE_TAXONOMY_FOLDERS_SCHEMA = types.Tool(
    name="create_taxonomy_folders",
    description="Create a single taxonomy with custom guidelines for a world project",
    inputSchema={
        "type": "object",
        "properties": {
            "world_directory": {
                "type": "string",
                "description": "Path to the world directory"
            },
            "taxonomy_name": {
                "type": "string",
                "description": "Name of the taxonomy to create"
            },
            "taxonomy_description": {
                "type": "string",
                "description": "Description of how this taxonomy applies to the world"
            },
            "custom_guidelines": {
                "type": "string",
                "description": "Custom entry structure guidelines for this taxonomy"
            }
        },
        "required": ["world_directory", "taxonomy_name", "taxonomy_description", "custom_guidelines"]
    }
)


# Entry Tools
CREATE_WORLD_ENTRY_SCHEMA = types.Tool(
    name="create_world_entry",
    description="Create a detailed entry for a specific world element within a taxonomy. Call without entry_content to get world context, then call again with content to create the entry.",
    inputSchema={
        "type": "object",
        "properties": {
            "world_directory": {
                "type": "string",
                "description": "Path to the world directory"
            },
            "taxonomy": {
                "type": "string",
                "description": "Name of the taxonomy this entry belongs to"
            },
            "entry_name": {
                "type": "string",
                "description": "Name of the entry to create"
            },
            "entry_content": {
                "type": "string",
                "description": "Markdown content for the entry (optional - omit to get world context first)",
                "default": ""
            }
        },
        "required": ["world_directory", "taxonomy", "entry_name"]
    }
)

IDENTIFY_STUB_CANDIDATES_SCHEMA = types.Tool(
    name="identify_stub_candidates",
    description="Analyze entry content and present it to client LLM for stub candidate identification",
    inputSchema={
        "type": "object",
        "properties": {
            "world_directory": {
                "type": "string",
                "description": "Path to the world directory"
            },
            "entry_content": {
                "type": "string",
                "description": "The markdown content of the entry to analyze for stub candidates"
            },
            "entry_name": {
                "type": "string",
                "description": "Name of the entry being analyzed"
            },
            "taxonomy": {
                "type": "string",
                "description": "Taxonomy the entry belongs to"
            }
        },
        "required": ["world_directory", "entry_content", "entry_name", "taxonomy"]
    }
)

CREATE_STUB_ENTRIES_SCHEMA = types.Tool(
    name="create_stub_entries",
    description="Create multiple stub entries based on LLM analysis",
    inputSchema={
        "type": "object",
        "properties": {
            "world_directory": {
                "type": "string",
                "description": "Path to the world directory"
            },
            "stub_entries": {
                "type": "array",
                "description": "List of stub entries to create",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name of the entity"},
                        "taxonomy": {"type": "string", "description": "Taxonomy to place the entry in"},
                        "description": {"type": "string", "description": "1-2 sentence description"},
                        "create_taxonomy": {"type": "boolean", "description": "Whether to create the taxonomy if it doesn't exist", "default": False}
                    },
                    "required": ["name", "taxonomy", "description"]
                }
            }
        },
        "required": ["world_directory", "stub_entries"]
    }
)

ADD_FRONTMATTER_TO_ENTRIES_SCHEMA = types.Tool(
    name="add_frontmatter_to_entries",
    description="Add YAML frontmatter with descriptions to existing entries",
    inputSchema={
        "type": "object",
        "properties": {
            "world_directory": {
                "type": "string",
                "description": "Path to the world directory"
            }
        },
        "required": ["world_directory"]
    }
)

GENERATE_ENTRY_DESCRIPTIONS_SCHEMA = types.Tool(
    name="generate_entry_descriptions",
    description="Present entry content to client LLM for intelligent description generation",
    inputSchema={
        "type": "object",
        "properties": {
            "world_directory": {
                "type": "string",
                "description": "Path to the world directory"
            }
        },
        "required": ["world_directory"]
    }
)

APPLY_ENTRY_DESCRIPTIONS_SCHEMA = types.Tool(
    name="apply_entry_descriptions",
    description="Apply generated descriptions to entry frontmatter",
    inputSchema={
        "type": "object",
        "properties": {
            "world_directory": {
                "type": "string",
                "description": "Path to the world directory"
            },
            "entry_descriptions": {
                "type": "array",
                "description": "List of entry descriptions to apply",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name of the entry"},
                        "description": {"type": "string", "description": "Generated description for the entry"}
                    },
                    "required": ["name", "description"]
                }
            }
        },
        "required": ["world_directory", "entry_descriptions"]
    }
)




# Image Generation Tools
GENERATE_IMAGE_FROM_MARKDOWN_FILE_SCHEMA = types.Tool(
    name="generate_image_from_markdown_file",
    description="Generate an image from a markdown file using FAL Imagen4 API",
    inputSchema={
        "type": "object",
        "properties": {
            "filepath": {
                "type": "string",
                "description": "Path to the markdown file to generate an image for"
            },
            "style": {
                "type": "string",
                "description": "Art style for the image (default: fantasy illustration)",
                "default": "fantasy illustration"
            },
            "aspect_ratio": {
                "type": "string",
                "description": "Aspect ratio for the generated image",
                "enum": ["1:1", "16:9", "9:16", "3:4", "4:3"],
                "default": "1:1"
            }
        },
        "required": ["filepath"]
    }
)


# Site Generation Tools
BUILD_STATIC_SITE_SCHEMA = types.Tool(
    name="build_static_site",
    description="Build a static website for a specific world, outputting the site within the world directory",
    inputSchema={
        "type": "object",
        "properties": {
            "world_directory": {
                "type": "string",
                "description": "Path to the world directory to build a site for"
            },
            "action": {
                "type": "string",
                "description": "Action to perform: 'build' to generate static files, 'dev' to start development server, or 'preview' to preview built site",
                "enum": ["build", "dev", "preview"],
                "default": "build"
            },
            "site_dir": {
                "type": "string",
                "description": "Directory name within the world folder to output built files (default: site)",
                "default": "site"
            }
        },
        "required": ["world_directory"]
    }
)


# Organized tool collections for easy access
CONTENT_TOOLS = [
    SAVE_WORLD_CONTENT_SCHEMA,
    READ_WORLD_CONTENT_SCHEMA,
    LIST_WORLD_FILES_SCHEMA,
]

WORLD_TOOLS = [
    INSTANTIATE_WORLD_SCHEMA,
]

TAXONOMY_TOOLS = [
    GENERATE_TAXONOMY_GUIDELINES_SCHEMA,
    CREATE_TAXONOMY_FOLDERS_SCHEMA,
]

ENTRY_TOOLS = [
    CREATE_WORLD_ENTRY_SCHEMA,
    IDENTIFY_STUB_CANDIDATES_SCHEMA,
    CREATE_STUB_ENTRIES_SCHEMA,
    ADD_FRONTMATTER_TO_ENTRIES_SCHEMA,
    GENERATE_ENTRY_DESCRIPTIONS_SCHEMA,
    APPLY_ENTRY_DESCRIPTIONS_SCHEMA,
]

IMAGE_TOOLS = [
    GENERATE_IMAGE_FROM_MARKDOWN_FILE_SCHEMA,
]

SITE_TOOLS = [
    BUILD_STATIC_SITE_SCHEMA,
]

# Complete tool list
ALL_TOOLS = CONTENT_TOOLS + WORLD_TOOLS + TAXONOMY_TOOLS + ENTRY_TOOLS + SITE_TOOLS


def get_all_tools(include_fal_tools: bool = False) -> list[types.Tool]:
    """Get all tool schemas, optionally including FAL-dependent tools.
    
    Args:
        include_fal_tools: Whether to include tools that require FAL API
        
    Returns:
        List of all tool schemas
    """
    tools = ALL_TOOLS.copy()
    if include_fal_tools:
        tools.extend(IMAGE_TOOLS)
    return tools


def get_tools_by_category(category: str) -> list[types.Tool]:
    """Get tool schemas by category.
    
    Args:
        category: Tool category ("content", "world", "taxonomy", "entry", "image", "site")
        
    Returns:
        List of tool schemas for the specified category
        
    Raises:
        ValueError: If category is not recognized
    """
    category_map = {
        "content": CONTENT_TOOLS,
        "world": WORLD_TOOLS,
        "taxonomy": TAXONOMY_TOOLS,
        "entry": ENTRY_TOOLS,
        "image": IMAGE_TOOLS,
        "site": SITE_TOOLS,
    }
    
    if category not in category_map:
        raise ValueError(f"Unknown category: {category}. Valid categories: {list(category_map.keys())}")
    
    return category_map[category]