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

## Guidelines
This taxonomy contains all {taxonomy_name.lower()} elements in the world. Each entry should:
- Follow the world's established rules and themes
- Reference this overview for consistency
- Build upon the concepts described above

## Related Elements
[Connections to other taxonomies and world elements]

---
*Taxonomy created for {world_name}*
"""
                    with open(taxonomy_file, "w", encoding="utf-8") as f:
                        f.write(taxonomy_content)
                    created_folders.append(str(taxonomy_file.relative_to(base_path)))
                    
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
            
            # Success message
            folder_list = "\n".join([f"- {folder}" for folder in sorted(created_folders)])
            if taxonomies:
                taxonomy_names = [t.get("name", "") if isinstance(t, dict) else t for t in taxonomies]
                taxonomy_info = f"\n\nInitial taxonomies created: {', '.join(taxonomy_names)}"
            else:
                taxonomy_info = "\n\nNo initial taxonomies created. Use 'create_taxonomy_folders' to add them as needed."
            
            return [types.TextContent(
                type="text", 
                text=f"Successfully instantiated '{world_name}' world project!\n\nProject folder: {unique_folder_name}\nFull path: {world_path}\n\nCreated structure:\n{folder_list}{taxonomy_info}\n\nNext steps:\n1. Review your world overview\n2. Create additional taxonomy folders as needed\n3. Begin creating detailed entries\n4. Generate images for key concepts"
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

## Guidelines
This taxonomy contains all {taxonomy_name.lower()} elements in the world. Each entry should:
- Follow the world's established rules and themes
- Reference this overview for consistency
- Build upon the concepts described above

## Related Elements
[Connections to other taxonomies and world elements]

---
*Taxonomy created for {world_name}*
"""
                with open(taxonomy_file, "w", encoding="utf-8") as f:
                    f.write(taxonomy_content)
                created_folders.append(f"taxonomies/{clean_name}-overview.md")
            
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
            taxonomy_overview_path = world_path / "taxonomies" / clean_taxonomy / f"{clean_taxonomy}-overview.md"
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
            
            relative_path = str(entry_file.relative_to(world_path))
            context_info = f"\n\nTaxonomy context included: {taxonomy_context[:100]}..." if taxonomy_context else "\n\nNo taxonomy overview found for reference."
            
            return [types.TextContent(
                type="text",
                text=f"Successfully created entry '{entry_name}' in {taxonomy} taxonomy!\n\nSaved to: {relative_path}{context_info}\n\nThe entry includes:\n1. Automatic reference to the taxonomy overview\n2. Your detailed content\n3. Taxonomy classification footer"
            )]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error creating world entry: {str(e)}")]
    
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