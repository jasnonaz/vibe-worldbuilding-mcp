#!/usr/bin/env python3

import os
import json
import asyncio
import uuid
from datetime import datetime
from typing import Any, Sequence
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from pathlib import Path

# Load environment variables from .env file
def load_env_file(env_path: Path = None):
    """Load environment variables from .env file"""
    if env_path is None:
        env_path = Path(__file__).parent / ".env"
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Only set if not already in environment (allows override)
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = value.strip()

# Load .env file at startup
load_env_file()

try:
    import requests
    FAL_AVAILABLE = True
except ImportError:
    FAL_AVAILABLE = False

app = Server("vibe-worldbuilding")

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
    
    if name == "start-worldbuilding":
        return types.GetPromptResult(
            description="Begin a new world project",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text="""# Starting a New World

Welcome to worldbuilding! Let's create something amazing together.

## What is your world about?

Think about the core concept that makes your world unique. This could be:
- A central magical/technological system
- A unique physical law or property
- An interesting social structure
- A fascinating historical event
- A compelling conflict or tension

Take your time to describe your initial idea. Don't worry about details yet - we'll develop those together.

What draws you to this world concept? What excites you about exploring it further?"""
                    )
                )
            ]
        )
    
    elif name == "continue-worldbuilding":
        return types.GetPromptResult(
            description="Resume work on an existing world",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text="""# Continuing Your World

Welcome back to your worldbuilding project!

## Where we left off

To help me understand where we are in your world's development, please share:

1. **What world are you working on?** (Brief reminder of the core concept)
2. **What have you developed so far?** (Overview, taxonomies, specific entries)
3. **What would you like to focus on today?** (New areas, refinements, consistency checks)

You can also paste any existing content you'd like me to review or build upon.

What aspect of your world is calling to you today?"""
                    )
                )
            ]
        )
    
    elif name == "world-foundation":
        return types.GetPromptResult(
            description="Develop core world concepts",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text="""# Building Your World's Foundation

Let's establish the fundamental aspects of your world that everything else will build upon.

## Core Questions to Explore

**The Central Concept**
- What makes your world unique and interesting?
- What is the "big idea" that drives everything else?

**Physical Reality**
- How do the basic laws of physics, magic, or technology work?
- What are the fundamental forces that shape daily life?

**Scale and Scope**
- Is this a single location, planet, galaxy, or multiverse?
- What time period(s) does your world cover?

**Tone and Themes**
- What feelings should your world evoke?
- What questions or themes do you want to explore?

## Creating Your Foundation Document

We'll work together to create a foundational document that captures:
1. Your world's elevator pitch (1-2 sentences)
2. Core mechanics/systems
3. Key themes and tone
4. Scope and boundaries

What aspect would you like to start with?"""
                    )
                )
            ]
        )
    
    elif name == "taxonomy":
        return types.GetPromptResult(
            description="Create classification systems",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text="""# Creating World Taxonomies

Taxonomies help organize and categorize the elements of your world, creating systematic frameworks that ensure consistency and inspire new ideas.

## Types of Taxonomies to Consider

**Social/Cultural Systems**
- Government types and structures
- Social classes or castes
- Cultural groups and ethnicities
- Professions and roles

**Magical/Technological Systems**
- Schools or types of magic
- Technology categories and advancement levels
- Energy sources and their applications

**Biological/Ecological**
- Species and subspecies
- Ecosystems and biomes
- Evolutionary relationships

**Geographic/Spatial**
- Region types and climates
- Settlement categories
- Architectural styles

**Temporal/Historical**
- Era classifications
- Event types and scales
- Calendar systems

## Creating Your Taxonomy

Choose a category that's important to your world and we'll create a systematic classification. This will include:
1. Clear categories and subcategories
2. Defining characteristics for each type
3. Examples of each category
4. Relationships between categories

What type of classification system interests you most for your world?"""
                    )
                )
            ]
        )
    
    elif name == "world-entry":
        return types.GetPromptResult(
            description="Create detailed world entries",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text="""# Creating Detailed World Entries

Let's dive deep into a specific element of your world and create a comprehensive entry that brings it to life.

## Types of Entries

**Places**
- Cities, regions, landmarks, or buildings
- Include geography, culture, history, and notable features

**Characters/Beings**
- Important individuals, species, or groups
- Cover appearance, personality, abilities, and relationships

**Objects/Artifacts**
- Magical items, technologies, or significant objects
- Detail function, history, appearance, and impact

**Events/Phenomena**
- Historical events, natural phenomena, or ongoing situations
- Explain causes, effects, timeline, and significance

**Systems/Concepts**
- Magic systems, governments, religions, or philosophies
- Break down mechanics, beliefs, structures, and implications

## Entry Structure

Each entry should include:
1. **Overview** - Quick summary and significance
2. **Description** - Detailed explanation of key aspects
3. **History/Context** - Background and development
4. **Relationships** - Connections to other world elements
5. **Impact** - Effects on the broader world

What specific element of your world would you like to develop into a detailed entry?"""
                    )
                )
            ]
        )
    
    elif name == "consistency-review":
        return types.GetPromptResult(
            description="Review world consistency",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text="""# World Consistency Review

Let's examine your world for logical consistency, internal coherence, and potential areas that need development or revision.

## Areas to Check

**Internal Logic**
- Do your world's rules work consistently?
- Are there contradictions in how systems operate?
- Do cause-and-effect relationships make sense?

**Cultural Coherence**
- Do societies develop logically from their circumstances?
- Are belief systems and values internally consistent?
- Do economic and political systems align with the world's reality?

**Temporal Consistency**
- Does your world's history flow logically?
- Are technological/magical advancement rates reasonable?
- Do events have appropriate consequences?

**Geographic Logic**
- Do climates, ecosystems, and geography make sense together?
- Are trade routes and settlements positioned logically?
- Do natural resources align with civilizations?

## Review Process

Share the elements of your world you'd like me to review. This could include:
- Your foundation document
- Taxonomies and classification systems
- Specific entries or detailed elements
- Any areas where you sense potential problems

I'll help identify:
1. Inconsistencies or contradictions
2. Areas that need more development
3. Opportunities to strengthen connections
4. Suggestions for resolving issues

What aspects of your world would you like to review for consistency?"""
                    )
                )
            ]
        )
    
    elif name == "entry-revision":
        return types.GetPromptResult(
            description="Revise existing entries",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text="""# Revising World Entries

Let's improve and refine existing elements of your world to make them more compelling, consistent, and detailed.

## Types of Revisions

**Expansion and Depth**
- Add missing details or context
- Develop underdeveloped aspects
- Increase complexity and nuance

**Consistency Fixes**
- Resolve contradictions with other elements
- Align with established world rules
- Ensure logical coherence

**Enhancement and Polish**
- Improve clarity and readability
- Strengthen the most interesting aspects
- Add sensory details and atmosphere

**Connection Building**
- Link to other world elements
- Develop relationships and dependencies
- Create interesting tensions or harmonies

## Revision Process

Share the entry or element you'd like to revise. I'll help you:

1. **Identify** areas for improvement
2. **Brainstorm** enhancement options
3. **Develop** specific improvements
4. **Integrate** changes with the broader world
5. **Polish** the final result

You can share:
- A specific entry you want to improve
- Multiple related elements to revise together
- An area where you feel something is missing
- Content that doesn't feel quite right

What would you like to work on improving?"""
                    )
                )
            ]
        )
    
    elif name == "workflow":
        return types.GetPromptResult(
            description="Worldbuilding process guidance",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text="""# Worldbuilding Workflow Guide

Here's a systematic approach to building rich, cohesive fictional worlds:

## Phase 1: Foundation (Start Here)
1. **Core Concept** - What makes your world unique?
2. **Scope Definition** - How big is your world?
3. **Tone and Themes** - What feelings and ideas drive it?
4. **Basic Rules** - How do fundamental systems work?

## Phase 2: Structure (Build the Framework)
1. **Create Taxonomies** - Classification systems for major elements
2. **Map Relationships** - How do systems interact?
3. **Establish Constraints** - What are the limits and boundaries?
4. **Timeline Framework** - Key historical periods or events

## Phase 3: Development (Fill in Details)
1. **Priority Elements** - Develop the most important pieces first
2. **Cluster Building** - Create related groups of content
3. **Detail Layering** - Add depth gradually
4. **Connection Weaving** - Link elements together

## Phase 4: Refinement (Polish and Perfect)
1. **Consistency Review** - Check for contradictions
2. **Gap Analysis** - Find areas needing development
3. **Enhancement** - Improve existing content
4. **Testing** - Use your world in stories or scenarios

## Best Practices

**Quality Over Quantity**
- Better to have fewer, well-developed elements
- Deep development creates more interesting connections

**Organic Growth**
- Let your world evolve naturally
- Follow your interests and curiosity

**Regular Review**
- Periodically check for consistency
- Update older content as the world develops

**Documentation**
- Keep good records of what you've created
- Use clear organization and naming

Where are you in this process, and what would help you move forward?"""
                    )
                )
            ]
        )
    
    else:
        raise ValueError(f"Unknown prompt: {name}")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available worldbuilding tools."""
    tools = [
        types.Tool(
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
        ),
        types.Tool(
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
        ),
        types.Tool(
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
        ),
        types.Tool(
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
        ),
        types.Tool(
            name="create_taxonomy_folders",
            description="Create folders for specific taxonomies as they are developed during worldbuilding",
            inputSchema={
                "type": "object",
                "properties": {
                    "world_directory": {
                        "type": "string",
                        "description": "Path to the world directory"
                    },
                    "taxonomies": {
                        "type": "array",
                        "description": "List of taxonomy objects with name and description",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Name of the taxonomy"},
                                "description": {"type": "string", "description": "Description of how this taxonomy applies to the world"}
                            },
                            "required": ["name", "description"]
                        }
                    }
                },
                "required": ["world_directory", "taxonomies"]
            }
        ),
        types.Tool(
            name="create_world_entry",
            description="Create a detailed entry for a specific world element within a taxonomy, referencing the taxonomy description",
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
                        "description": "Markdown content for the entry"
                    }
                },
                "required": ["world_directory", "taxonomy", "entry_name", "entry_content"]
            }
        ),
        types.Tool(
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
    ]
    
    if FAL_AVAILABLE:
        tools.append(
            types.Tool(
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
        )
    
    return tools

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Handle tool calls for worldbuilding operations."""
    
    if name == "save_world_content":
        if not arguments:
            return [types.TextContent(type="text", text="Error: No arguments provided")]
        
        filename = arguments.get("filename", "")
        content = arguments.get("content", "")
        directory = arguments.get("directory", ".")
        
        if not filename or not content:
            return [types.TextContent(type="text", text="Error: Both filename and content are required")]
        
        # Ensure filename has .md extension
        if not filename.endswith(".md"):
            filename += ".md"
        
        # Create directory if it doesn't exist
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Save the file
        file_path = dir_path / filename
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return [types.TextContent(type="text", text=f"Successfully saved content to {file_path}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error saving file: {str(e)}")]
    
    elif name == "read_world_content":
        if not arguments:
            return [types.TextContent(type="text", text="Error: No arguments provided")]
        
        filepath = arguments.get("filepath", "")
        if not filepath:
            return [types.TextContent(type="text", text="Error: filepath is required")]
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return [types.TextContent(type="text", text=f"Content of {filepath}:\n\n{content}")]
        except FileNotFoundError:
            return [types.TextContent(type="text", text=f"Error: File {filepath} not found")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error reading file: {str(e)}")]
    
    elif name == "list_world_files":
        directory = arguments.get("directory", ".") if arguments else "."
        
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return [types.TextContent(type="text", text=f"Error: Directory {directory} does not exist")]
            
            md_files = list(dir_path.glob("*.md"))
            if not md_files:
                return [types.TextContent(type="text", text=f"No markdown files found in {directory}")]
            
            file_list = "\n".join([f"- {f.name}" for f in sorted(md_files)])
            return [types.TextContent(type="text", text=f"Markdown files in {directory}:\n{file_list}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error listing files: {str(e)}")]
    
    elif name == "generate_image_from_markdown_file":
        if not FAL_AVAILABLE:
            return [types.TextContent(type="text", text="Error: requests library not available. Please install with: pip install requests")]
        
        if not arguments:
            return [types.TextContent(type="text", text="Error: No arguments provided")]
        
        filepath = arguments.get("filepath", "")
        style = arguments.get("style", "fantasy illustration")
        aspect_ratio = arguments.get("aspect_ratio", "1:1")
        
        if not filepath:
            return [types.TextContent(type="text", text="Error: filepath is required")]
        
        # Check for API key
        api_key = os.environ.get("FAL_KEY")
        if not api_key:
            return [types.TextContent(type="text", text="Error: FAL_KEY environment variable not set")]
        
        try:
            # Read the markdown file
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Extract title and create description
            lines = content.split('\n')
            title = ""
            description_lines = []
            
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                elif line.strip() and not line.startswith('#') and not line.startswith('---'):
                    description_lines.append(line.strip())
                    if len(description_lines) >= 3:  # Limit description length
                        break
            
            description = ' '.join(description_lines)
            
            # Create the prompt
            if title:
                prompt = f"{style} of {title}. {description}"
            else:
                prompt = f"{style}. {description}"
            
            # Prepare the API request
            headers = {
                "Authorization": f"Key {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "num_images": 1
            }
            
            # Make the API request to FAL
            response = requests.post(
                "https://fal.run/fal-ai/imagen4/preview",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                return [types.TextContent(type="text", text=f"Error: FAL API request failed with status {response.status_code}: {response.text}")]
            
            result = response.json()
            
            if "images" not in result or not result["images"]:
                return [types.TextContent(type="text", text="Error: No images returned from FAL API")]
            
            # Get the image URL
            image_url = result["images"][0]["url"]
            
            # Download and save the image
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                return [types.TextContent(type="text", text=f"Error: Failed to download image from {image_url}")]
            
            # Save the image to centralized images directory
            file_path = Path(filepath)
            
            # Find the world root directory (should contain README.md)
            world_root = file_path
            while world_root != world_root.parent:
                if (world_root / "README.md").exists() and (world_root / "overview").exists():
                    break
                world_root = world_root.parent
            else:
                # Fallback to parent directory if world root not found
                world_root = file_path.parent
            
            # Create centralized images directory
            images_dir = world_root / "images"
            images_dir.mkdir(exist_ok=True)
            
            # Determine category from file path for organization
            category = ""
            if "/entries/" in str(file_path):
                path_parts = str(file_path).split("/entries/")
                if len(path_parts) > 1:
                    category_part = path_parts[1].split("/")[0]
                    category = category_part + "/"
            
            # Create category subfolder in images if needed
            if category:
                category_dir = images_dir / category.rstrip("/")
                category_dir.mkdir(exist_ok=True)
                image_filename = f"{file_path.stem}.png"
                image_path = category_dir / image_filename
            else:
                image_filename = f"{file_path.stem}.png"
                image_path = images_dir / image_filename
            
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            
            seed_info = f"Seed: {result.get('seed', 'unknown')}" if 'seed' in result else ""
            
            return [types.TextContent(type="text", text=f"Successfully generated image for {filepath}\nSaved to: {image_path}\nPrompt used: {prompt}\nAspect ratio: {aspect_ratio}\n{seed_info}")]
            
        except FileNotFoundError:
            return [types.TextContent(type="text", text=f"Error: File {filepath} not found")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error generating image: {str(e)}")]
    
    elif name == "instantiate_world":
        if not arguments:
            return [types.TextContent(type="text", text="Error: No arguments provided")]
        
        world_name = arguments.get("world_name", "")
        world_content = arguments.get("world_content", "")
        taxonomies = arguments.get("taxonomies", [])
        base_directory = arguments.get("base_directory", ".")
        unique_suffix = arguments.get("unique_suffix", "timestamp")
        
        if not world_name or not world_content:
            return [types.TextContent(type="text", text="Error: Both world_name and world_content are required")]
        
        try:
            # Generate unique suffix
            if unique_suffix == "timestamp":
                suffix = datetime.now().strftime("%Y%m%d-%H%M%S")
            elif unique_suffix == "uuid":
                suffix = str(uuid.uuid4())
            elif unique_suffix == "short-uuid":
                suffix = str(uuid.uuid4())[:8]
            else:
                suffix = datetime.now().strftime("%Y%m%d-%H%M%S")  # fallback
            
            # Create base directory structure with unique folder name
            base_path = Path(base_directory)
            clean_world_name = world_name.lower().replace(" ", "-")
            unique_folder_name = f"{clean_world_name}-{suffix}"
            world_path = base_path / unique_folder_name
            world_path.mkdir(parents=True, exist_ok=True)
            
            # Create main world folders
            main_folders = ["overview", "taxonomies", "entries", "images", "notes"]
            created_folders = []
            
            for folder in main_folders:
                folder_path = world_path / folder
                folder_path.mkdir(exist_ok=True)
                created_folders.append(str(folder_path.relative_to(base_path)))
            
            # Create taxonomy files if provided (no subfolders)
            if taxonomies:
                taxonomies_path = world_path / "taxonomies"
                entries_path = world_path / "entries"
                
                for taxonomy in taxonomies:
                    taxonomy_name = taxonomy.get("name", "") if isinstance(taxonomy, dict) else taxonomy
                    taxonomy_desc = taxonomy.get("description", "") if isinstance(taxonomy, dict) else ""
                    clean_name = taxonomy_name.lower().replace(" ", "-").replace("_", "-")
                    
                    # Create taxonomy overview file directly in taxonomies folder
                    taxonomy_file = taxonomies_path / f"{clean_name}-overview.md"
                    taxonomy_content = f"""# {taxonomy_name.title()} - Taxonomy Overview

## Description
{taxonomy_desc}

## Classification Framework
This taxonomy provides a systematic way to categorize and understand {taxonomy_name.lower()} within the world. When creating entries in this category, consider:

- **Core characteristics** that define membership in this taxonomy
- **Variations and subtypes** that exist within this classification
- **Relationships** to other elements in the world
- **Cultural or functional significance** within the broader worldbuilding context

## Development Guidelines
Each {taxonomy_name.lower()} entry should explore:
- Unique features that distinguish it from similar elements
- Historical development or origins within the world
- Impact on other systems, cultures, or regions
- Potential for future development or change

## Cross-References
Consider how elements in this taxonomy connect to:
- Other taxonomies in this world
- The overall world themes and mechanics
- Specific locations, cultures, or time periods
"""
                    with open(taxonomy_file, "w", encoding="utf-8") as f:
                        f.write(taxonomy_content)
                    created_folders.append(str(taxonomy_file.relative_to(base_path)))
                    
                    # Generate image for taxonomy if FAL_KEY is available
                    if FAL_AVAILABLE and os.environ.get("FAL_KEY"):
                        try:
                            # Create taxonomy-specific prompt
                            taxonomy_prompt = f"Conceptual illustration of {taxonomy_name}, {taxonomy_desc}, fantasy art style, detailed digital illustration"
                            
                            headers = {
                                "Authorization": f"Key {os.environ.get('FAL_KEY')}",
                                "Content-Type": "application/json"
                            }
                            
                            payload = {
                                "prompt": taxonomy_prompt,
                                "aspect_ratio": "1:1",
                                "num_images": 1
                            }
                            
                            response = requests.post(
                                "https://fal.run/fal-ai/imagen4/preview",
                                headers=headers,
                                json=payload
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                if "images" in result and result["images"]:
                                    image_url = result["images"][0]["url"]
                                    image_response = requests.get(image_url)
                                    if image_response.status_code == 200:
                                        # Save taxonomy image
                                        taxonomy_image_path = world_path / "images" / f"{clean_name}-taxonomy.png"
                                        with open(taxonomy_image_path, "wb") as f:
                                            f.write(image_response.content)
                                        created_folders.append(str(taxonomy_image_path.relative_to(base_path)))
                        except Exception:
                            # Silently continue if image generation fails
                            pass
                    
                    # Create corresponding entry folder
                    entry_path = entries_path / clean_name
                    entry_path.mkdir(exist_ok=True)
                    created_folders.append(str(entry_path.relative_to(base_path)))
            
            # Save the world overview content
            overview_file = world_path / "overview" / "world-overview.md"
            with open(overview_file, "w", encoding="utf-8") as f:
                f.write(world_content)
            
            created_folders.append(str(overview_file.relative_to(base_path)))
            
            # Create README for the world
            taxonomies_text = ""
            if taxonomies:
                taxonomies_text = f"\n\n## Initial Taxonomies\n\n{chr(10).join(f'- **{taxonomy}**: Ready for development' for taxonomy in taxonomies)}\n"
            
            readme_content = f"""# {world_name}

This directory contains all the worldbuilding content for **{world_name}**.

## Directory Structure

- **overview/**: Core world documents and foundation
- **taxonomies/**: Classification systems and category definitions  
- **entries/**: Detailed entries for specific world elements
- **images/**: Generated and reference images
- **notes/**: Development notes and work-in-progress content{taxonomies_text}

## Getting Started

1. Review your world overview in `overview/world-overview.md`
2. Use the `create_taxonomy_folders` tool to add new taxonomies as needed
3. Define your taxonomies and create detailed entries
4. Generate images to visualize key concepts

## Taxonomy Development

As you develop your world, you'll identify key categories that need systematic development. Use the worldbuilding MCP to:
- Create folders for new taxonomies as they emerge
- Maintain consistency across related elements
- Build comprehensive classification systems

---
*World structure created by Vibe Worldbuilding MCP*
"""
            
            readme_file = world_path / "README.md"
            with open(readme_file, "w", encoding="utf-8") as f:
                f.write(readme_content)
            
            created_folders.append(str(readme_file.relative_to(base_path)))
            
            # Generate overview images if FAL_KEY is available
            image_generation_info = ""
            fal_key = os.environ.get("FAL_KEY")
            if fal_key:
                try:
                    # Extract key visual elements from the world content
                    # We'll generate 3 images: header, atmosphere detail, and concept detail
                    
                    # 1. Generate main header image (wide landscape for the world)
                    header_prompt = f"Epic wide landscape of {world_name}, fantasy digital art, cinematic composition"
                    
                    # Parse world content to extract more specific details
                    if "desert" in world_content.lower():
                        header_prompt = f"Epic desert landscape with futuristic elements, {world_name}, vast dunes and hidden technology, cinematic sci-fi art"
                    elif "forest" in world_content.lower():
                        header_prompt = f"Mystical forest landscape, {world_name}, ancient trees and magical atmosphere, fantasy digital art"
                    elif "city" in world_content.lower() or "urban" in world_content.lower():
                        header_prompt = f"Futuristic cityscape, {world_name}, towering structures and advanced technology, cyberpunk digital art"
                    
                    # Generate header image
                    headers = {
                        "Authorization": f"Key {fal_key}",
                        "Content-Type": "application/json"
                    }
                    
                    header_payload = {
                        "prompt": header_prompt + ", cinematic digital art",
                        "aspect_ratio": "16:9",
                        "num_images": 1
                    }
                    
                    header_response = requests.post(
                        "https://fal.run/fal-ai/imagen4/preview",
                        headers=headers,
                        json=header_payload
                    )
                    
                    header_result = header_response.json() if header_response.status_code == 200 else None
                    
                    if header_result and 'images' in header_result and header_result['images']:
                        header_image_url = header_result['images'][0]['url']
                        header_response = requests.get(header_image_url)
                        if header_response.status_code == 200:
                            header_path = world_path / "images" / "world-overview-header.png"
                            with open(header_path, 'wb') as f:
                                f.write(header_response.content)
                            image_generation_info += "\n- Generated header image: world-overview-header.png"
                    
                    # 2. Generate atmosphere detail image
                    atmosphere_prompt = f"Atmospheric detail from {world_name}, focusing on mood and environment, detailed fantasy illustration"
                    
                    atmosphere_payload = {
                        "prompt": atmosphere_prompt,
                        "aspect_ratio": "1:1",
                        "num_images": 1
                    }
                    
                    atmosphere_response = requests.post(
                        "https://fal.run/fal-ai/imagen4/preview",
                        headers=headers,
                        json=atmosphere_payload
                    )
                    
                    atmosphere_result = atmosphere_response.json() if atmosphere_response.status_code == 200 else None
                    
                    if atmosphere_result and 'images' in atmosphere_result and atmosphere_result['images']:
                        atmosphere_image_url = atmosphere_result['images'][0]['url']
                        atmosphere_response = requests.get(atmosphere_image_url)
                        if atmosphere_response.status_code == 200:
                            atmosphere_path = world_path / "images" / "world-overview-atmosphere.png"
                            with open(atmosphere_path, 'wb') as f:
                                f.write(atmosphere_response.content)
                            image_generation_info += "\n- Generated atmosphere image: world-overview-atmosphere.png"
                    
                    # 3. Generate concept detail image
                    concept_prompt = f"Key concept visualization from {world_name}, detailed fantasy illustration"
                    
                    concept_payload = {
                        "prompt": concept_prompt,
                        "aspect_ratio": "1:1",
                        "num_images": 1
                    }
                    
                    concept_response = requests.post(
                        "https://fal.run/fal-ai/imagen4/preview",
                        headers=headers,
                        json=concept_payload
                    )
                    
                    concept_result = concept_response.json() if concept_response.status_code == 200 else None
                    
                    if concept_result and 'images' in concept_result and concept_result['images']:
                        concept_image_url = concept_result['images'][0]['url']
                        concept_response = requests.get(concept_image_url)
                        if concept_response.status_code == 200:
                            concept_path = world_path / "images" / "world-overview-concept.png"
                            with open(concept_path, 'wb') as f:
                                f.write(concept_response.content)
                            image_generation_info += "\n- Generated concept image: world-overview-concept.png"
                    
                except Exception as e:
                    image_generation_info = f"\n\nNote: Image generation attempted but failed: {str(e)}"
            
            # Success message
            folder_list = "\n".join([f"- {folder}" for folder in sorted(created_folders)])
            if taxonomies:
                taxonomy_names = [t.get("name", "") if isinstance(t, dict) else t for t in taxonomies]
                taxonomy_info = f"\n\nInitial taxonomies created: {', '.join(taxonomy_names)}"
            else:
                taxonomy_info = "\n\nNo initial taxonomies created. Use 'create_taxonomy_folders' to add them as needed."
            
            return [types.TextContent(
                type="text", 
                text=f"Successfully instantiated '{world_name}' world project!\n\nProject folder: {unique_folder_name}\nFull path: {world_path}\n\nCreated structure:\n{folder_list}{taxonomy_info}{image_generation_info}\n\nNext steps:\n1. Review your world overview\n2. Create additional taxonomy folders as needed\n3. Begin creating detailed entries\n4. Generate images for key concepts"
            )]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error creating world structure: {str(e)}")]
    
    elif name == "create_taxonomy_folders":
        if not arguments:
            return [types.TextContent(type="text", text="Error: No arguments provided")]
        
        world_directory = arguments.get("world_directory", "")
        taxonomies = arguments.get("taxonomies", [])
        
        if not world_directory or not taxonomies:
            return [types.TextContent(type="text", text="Error: Both world_directory and taxonomies are required")]
        
        try:
            world_path = Path(world_directory)
            if not world_path.exists():
                return [types.TextContent(type="text", text=f"Error: World directory {world_directory} does not exist")]
            
            # Get world name from directory or README
            world_name = world_path.name.replace("-", " ").title()
            readme_path = world_path / "README.md"
            if readme_path.exists():
                with open(readme_path, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    if first_line.startswith("# "):
                        world_name = first_line[2:].split(" - ")[0].strip()
            
            created_folders = []
            
            # Create taxonomy files (no subfolders)
            taxonomies_path = world_path / "taxonomies"
            taxonomies_path.mkdir(exist_ok=True)
            
            for taxonomy in taxonomies:
                taxonomy_name = taxonomy.get("name", "")
                taxonomy_desc = taxonomy.get("description", "")
                clean_name = taxonomy_name.lower().replace(" ", "-").replace("_", "-")
                
                # Create taxonomy overview file directly in taxonomies folder
                taxonomy_file = taxonomies_path / f"{clean_name}-overview.md"
                taxonomy_content = f"""# {taxonomy_name.title()} - Taxonomy Overview

## Description
{taxonomy_desc}

## Classification Framework
This taxonomy provides a systematic way to categorize and understand {taxonomy_name.lower()} within the world. When creating entries in this category, consider:

- **Core characteristics** that define membership in this taxonomy
- **Variations and subtypes** that exist within this classification
- **Relationships** to other elements in the world
- **Cultural or functional significance** within the broader worldbuilding context

## Development Guidelines
Each {taxonomy_name.lower()} entry should explore:
- Unique features that distinguish it from similar elements
- Historical development or origins within the world
- Impact on other systems, cultures, or regions
- Potential for future development or change

## Cross-References
Consider how elements in this taxonomy connect to:
- Other taxonomies in this world
- The overall world themes and mechanics
- Specific locations, cultures, or time periods
"""
                with open(taxonomy_file, "w", encoding="utf-8") as f:
                    f.write(taxonomy_content)
                created_folders.append(f"taxonomies/{clean_name}-overview.md")
                
                # Generate image for taxonomy if FAL_KEY is available
                if FAL_AVAILABLE and os.environ.get("FAL_KEY"):
                    try:
                        # Create taxonomy-specific prompt
                        taxonomy_prompt = f"Conceptual illustration of {taxonomy_name}, {taxonomy_desc}, fantasy art style, detailed digital illustration"
                        
                        headers = {
                            "Authorization": f"Key {os.environ.get('FAL_KEY')}",
                            "Content-Type": "application/json"
                        }
                        
                        payload = {
                            "prompt": taxonomy_prompt,
                            "aspect_ratio": "1:1",
                            "num_images": 1
                        }
                        
                        response = requests.post(
                            "https://fal.run/fal-ai/imagen4/preview",
                            headers=headers,
                            json=payload
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            if "images" in result and result["images"]:
                                image_url = result["images"][0]["url"]
                                image_response = requests.get(image_url)
                                if image_response.status_code == 200:
                                    # Save taxonomy image
                                    images_dir = world_path / "images"
                                    images_dir.mkdir(exist_ok=True)
                                    taxonomy_image_path = images_dir / f"{clean_name}-taxonomy.png"
                                    with open(taxonomy_image_path, "wb") as f:
                                        f.write(image_response.content)
                                    created_folders.append(f"images/{clean_name}-taxonomy.png")
                    except Exception:
                        # Silently continue if image generation fails
                        pass
            
            # Create corresponding entry folders
            entries_path = world_path / "entries"
            entries_path.mkdir(exist_ok=True)
            
            for taxonomy in taxonomies:
                taxonomy_name = taxonomy.get("name", "")
                clean_name = taxonomy_name.lower().replace(" ", "-").replace("_", "-")
                entry_path = entries_path / clean_name
                entry_path.mkdir(exist_ok=True)
                created_folders.append(f"entries/{clean_name}")
            
            folder_list = "\n".join([f"- {folder}" for folder in sorted(created_folders)])
            taxonomy_names = [t.get("name", "") for t in taxonomies]
            return [types.TextContent(
                type="text",
                text=f"Successfully created taxonomy folders!\n\nCreated:\n{folder_list}\n\nTaxonomies added: {', '.join(taxonomy_names)}\n\nYou can now:\n1. Review the taxonomy overview files for guidance\n2. Add specific entries in the corresponding entries folders\n3. Use the 'create_world_entry' tool to add entries with automatic taxonomy reference"
            )]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error creating taxonomy folders: {str(e)}")]
    
    elif name == "create_world_entry":
        if not arguments:
            return [types.TextContent(type="text", text="Error: No arguments provided")]
        
        world_directory = arguments.get("world_directory", "")
        taxonomy = arguments.get("taxonomy", "")
        entry_name = arguments.get("entry_name", "")
        entry_content = arguments.get("entry_content", "")
        
        if not all([world_directory, taxonomy, entry_name, entry_content]):
            return [types.TextContent(type="text", text="Error: All parameters (world_directory, taxonomy, entry_name, entry_content) are required")]
        
        try:
            world_path = Path(world_directory)
            if not world_path.exists():
                return [types.TextContent(type="text", text=f"Error: World directory {world_directory} does not exist")]
            
            # Clean names
            clean_taxonomy = taxonomy.lower().replace(" ", "-").replace("_", "-")
            clean_entry = entry_name.lower().replace(" ", "-").replace("_", "-")
            
            # Check if taxonomy exists and read its overview
            taxonomy_overview_path = world_path / "taxonomies" / f"{clean_taxonomy}-overview.md"
            taxonomy_context = ""
            
            if taxonomy_overview_path.exists():
                with open(taxonomy_overview_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Extract the description section
                    lines = content.split('\n')
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
                    
                    if description_lines:
                        taxonomy_context = " ".join(description_lines)
            
            # Create the entry with taxonomy reference
            entry_path = world_path / "entries" / clean_taxonomy
            entry_path.mkdir(parents=True, exist_ok=True)
            
            entry_file = entry_path / f"{clean_entry}.md"
            
            # Add taxonomy context header if available
            header = ""
            if taxonomy_context:
                header = f"""---
**Taxonomy Context**: {taxonomy_context}
---

"""
            
            final_content = f"""{header}{entry_content}

---
*Entry in {taxonomy.title()} taxonomy*
"""
            
            with open(entry_file, "w", encoding="utf-8") as f:
                f.write(final_content)
            
            # Generate image for entry if FAL_KEY is available
            image_info = ""
            if FAL_AVAILABLE and os.environ.get("FAL_KEY"):
                try:
                    # Extract key visual elements from the entry content to create a good prompt
                    lines = entry_content.split('\n')
                    title = entry_name
                    description_lines = []
                    
                    for line in lines:
                        if line.startswith('# '):
                            title = line[2:].strip()
                        elif line.strip() and not line.startswith('#') and not line.startswith('---'):
                            description_lines.append(line.strip())
                            if len(description_lines) >= 3:  # Limit description length
                                break
                    
                    description = ' '.join(description_lines)
                    
                    # Create entry-specific prompt with taxonomy context
                    if taxonomy_context:
                        entry_prompt = f"Detailed illustration of {title}, {description}, within the context of {taxonomy_context[:100]}, fantasy art style, detailed digital art"
                    else:
                        entry_prompt = f"Detailed illustration of {title}, {description}, {taxonomy} themed, fantasy art style, detailed digital art"
                    
                    headers = {
                        "Authorization": f"Key {os.environ.get('FAL_KEY')}",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "prompt": entry_prompt,
                        "aspect_ratio": "1:1", 
                        "num_images": 1
                    }
                    
                    response = requests.post(
                        "https://fal.run/fal-ai/imagen4/preview",
                        headers=headers,
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if "images" in result and result["images"]:
                            image_url = result["images"][0]["url"]
                            image_response = requests.get(image_url)
                            if image_response.status_code == 200:
                                # Save entry image in organized structure
                                images_dir = world_path / "images"
                                images_dir.mkdir(exist_ok=True)
                                
                                # Create category subfolder for organization
                                category_dir = images_dir / clean_taxonomy
                                category_dir.mkdir(exist_ok=True)
                                
                                entry_image_path = category_dir / f"{clean_entry}.png"
                                with open(entry_image_path, "wb") as f:
                                    f.write(image_response.content)
                                
                                image_info = f"\n4. Generated image: images/{clean_taxonomy}/{clean_entry}.png"
                except Exception:
                    # Silently continue if image generation fails
                    pass
            
            relative_path = str(entry_file.relative_to(world_path))
            context_info = f"\n\nTaxonomy context included: {taxonomy_context[:100]}..." if taxonomy_context else "\n\nNo taxonomy overview found for reference."
            
            return [types.TextContent(
                type="text",
                text=f"Successfully created entry '{entry_name}' in {taxonomy} taxonomy!\n\nSaved to: {relative_path}{context_info}\n\nThe entry includes:\n1. Automatic reference to the taxonomy overview\n2. Your detailed content\n3. Taxonomy classification footer{image_info}"
            )]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error creating world entry: {str(e)}")]
    
    elif name == "build_static_site":
        if not arguments:
            return [types.TextContent(type="text", text="Error: world_directory is required")]
        
        world_directory = arguments.get("world_directory", "")
        action = arguments.get("action", "build")
        site_dir = arguments.get("site_dir", "site")
        
        if not world_directory:
            return [types.TextContent(type="text", text="Error: world_directory is required")]
        
        try:
            import subprocess
            import sys
            import shutil
            
            # Validate world directory exists
            world_path = Path(world_directory)
            if not world_path.exists():
                return [types.TextContent(type="text", text=f"Error: World directory {world_directory} does not exist")]
            
            # Check if it's a valid world directory (has overview folder)
            overview_path = world_path / "overview"
            if not overview_path.exists():
                return [types.TextContent(type="text", text=f"Error: {world_directory} is not a valid world directory (no overview folder found)")]
            
            # Get the directory where this script is located (should be the project root)
            script_dir = Path(__file__).parent.absolute()
            
            # Check if we're in the right directory (should have astro.config.mjs)
            astro_config_path = script_dir / "astro.config.mjs"
            if not astro_config_path.exists():
                return [types.TextContent(type="text", text=f"Error: astro.config.mjs not found in {script_dir}. Make sure Astro is configured in the project directory.")]
            
            # Check if node_modules exists
            node_modules_path = script_dir / "node_modules"
            if not node_modules_path.exists():
                return [types.TextContent(type="text", text=f"Error: node_modules not found in {script_dir}. Run 'npm install' first.")]
            
            if action == "build":
                # Create a temporary symlink of the world in the project directory so Astro can find it
                world_name = world_path.name
                temp_world_link = script_dir / world_name
                
                # Remove existing symlink if it exists
                if temp_world_link.exists() or temp_world_link.is_symlink():
                    if temp_world_link.is_symlink():
                        temp_world_link.unlink()
                    else:
                        shutil.rmtree(temp_world_link)
                
                # Create symlink to the world directory
                temp_world_link.symlink_to(world_path.absolute())
                
                # Clean up old content symlinks and create new ones
                content_dir = script_dir / "src" / "content"
                content_dir.mkdir(parents=True, exist_ok=True)
                
                # Create symlinks for the content directories
                content_links = ["overview", "taxonomies", "entries"]
                for link_name in content_links:
                    link_path = content_dir / link_name
                    source_path = world_path / link_name
                    
                    # Remove existing symlink if it exists
                    if link_path.exists() or link_path.is_symlink():
                        if link_path.is_symlink():
                            link_path.unlink()
                        else:
                            shutil.rmtree(link_path)
                    
                    # Create symlink if source exists
                    if source_path.exists():
                        link_path.symlink_to(source_path.absolute())
                
                # Copy images to public directory for the build
                world_images_path = world_path / "images"
                public_images_path = script_dir / "public" / "images" / world_name
                
                if world_images_path.exists():
                    # Remove existing public images for this world
                    if public_images_path.exists():
                        shutil.rmtree(public_images_path)
                    
                    # Copy images to public directory
                    shutil.copytree(world_images_path, public_images_path)
                
                try:
                    # Build the static site
                    result = subprocess.run(
                        ["npm", "run", "build"],
                        capture_output=True,
                        text=True,
                        timeout=300,  # 5 minutes timeout
                        cwd=script_dir  # Run from the project directory
                    )
                    
                    if result.returncode == 0:
                        # Move the built site from dist to the world's site directory
                        source_dist = script_dir / "dist"
                        target_site = world_path / site_dir
                        
                        # Remove existing site directory if it exists
                        if target_site.exists():
                            shutil.rmtree(target_site)
                        
                        # Move the built site
                        if source_dist.exists():
                            shutil.move(str(source_dist), str(target_site))
                            
                            # Count generated files
                            html_files = list(target_site.rglob("*.html"))
                            asset_files = list(target_site.rglob("*.css")) + list(target_site.rglob("*.js"))
                            
                            return [types.TextContent(
                                type="text",
                                text=f"✅ Static site built successfully for {world_name}!\n\nSite location: {target_site.absolute()}\nGenerated {len(html_files)} HTML pages and {len(asset_files)} asset files.\n\nTo serve the site locally:\n- Navigate to {target_site}\n- Run 'python -m http.server 8000' or any static file server\n- Open http://localhost:8000"
                            )]
                        else:
                            return [types.TextContent(
                                type="text",
                                text=f"Build completed but dist directory not found.\n\nBuild output:\n{result.stdout}\n\nErrors:\n{result.stderr}"
                            )]
                    else:
                        return [types.TextContent(
                            type="text",
                            text=f"Build failed with exit code {result.returncode}\n\nErrors:\n{result.stderr}\n\nOutput:\n{result.stdout}"
                        )]
                finally:
                    # Clean up the temporary symlink
                    if temp_world_link.exists() or temp_world_link.is_symlink():
                        temp_world_link.unlink()
                    
                    # Clean up public images
                    public_images_path = script_dir / "public" / "images" / world_name
                    if public_images_path.exists():
                        shutil.rmtree(public_images_path)
                    
                    # Clean up content symlinks
                    content_dir = script_dir / "src" / "content"
                    content_links = ["overview", "taxonomies", "entries"]
                    for link_name in content_links:
                        link_path = content_dir / link_name
                        if link_path.exists() or link_path.is_symlink():
                            if link_path.is_symlink():
                                link_path.unlink()
                            else:
                                shutil.rmtree(link_path)
            
            elif action == "dev":
                # Create temporary symlink for development
                world_name = world_path.name
                temp_world_link = script_dir / world_name
                
                if temp_world_link.exists() or temp_world_link.is_symlink():
                    if temp_world_link.is_symlink():
                        temp_world_link.unlink()
                    else:
                        shutil.rmtree(temp_world_link)
                
                temp_world_link.symlink_to(world_path.absolute())
                
                # Create content symlinks that Astro expects
                content_dir = script_dir / "src" / "content"
                content_dir.mkdir(parents=True, exist_ok=True)
                
                # Create symlinks for the content directories
                content_links = ["overview", "taxonomies", "entries"]
                for link_name in content_links:
                    link_path = content_dir / link_name
                    source_path = world_path / link_name
                    
                    # Remove existing symlink if it exists
                    if link_path.exists() or link_path.is_symlink():
                        if link_path.is_symlink():
                            link_path.unlink()
                        else:
                            shutil.rmtree(link_path)
                    
                    # Create symlink if source exists
                    if source_path.exists():
                        link_path.symlink_to(source_path.absolute())
                
                return [types.TextContent(
                    type="text",
                    text=f"✅ Development setup ready for {world_name}!\n\nTo start the development server:\n1. Open a terminal in {script_dir}\n2. Run: npm run dev\n3. Open http://localhost:4321\n\nNote: The world has been temporarily linked for development. The symlink will be cleaned up when you build the site."
                )]
            
            elif action == "preview":
                # Check if site directory exists in the world
                site_path = world_path / site_dir
                if not site_path.exists():
                    return [types.TextContent(
                        type="text",
                        text=f"No built site found in {site_path}. Run the build action first."
                    )]
                
                return [types.TextContent(
                    type="text",
                    text=f"To preview the built site for {world_path.name}:\n\n1. Navigate to: {site_path}\n2. Run: python -m http.server 8000\n3. Open: http://localhost:8000\n\nOr use any other static file server of your choice."
                )]
            
            else:
                return [types.TextContent(type="text", text=f"Unknown action: {action}. Use 'build', 'dev', or 'preview'.")]
                
        except subprocess.TimeoutExpired:
            return [types.TextContent(type="text", text="Build timed out after 5 minutes. Your project might be too large or there may be an issue with the build process.")]
        except FileNotFoundError:
            return [types.TextContent(type="text", text="Error: npm not found. Make sure Node.js and npm are installed on your system.")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error building static site: {str(e)}")]
    
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Main entry point for the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="vibe-worldbuilding",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())