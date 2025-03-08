# Vibe Worldbuilding MCP

A streamlined system for creating and managing fictional worlds.

## Overview

Vibe Worldbuilding is designed to help you create comprehensive fictional worlds with a seamless, integrated process. The system helps you develop:

1. **World Foundation**: Core concept documents detailing the fundamental aspects of your world
2. **Taxonomies**: Classification systems for organizing the major elements of your world
3. **Entries**: Detailed information about specific elements in your world

## Setup Instructions

### Installing the MCP

1. Download the `vibe-worldbuilding-mcp` folder
2. Ensure you have Python installed on your system
3. Install follow this guide to get set up with MCP https://modelcontextprotocol.io/quickstart/user
4. Start the server:
   ```
   python vibe_worldbuilding_server.py
   ```

### Using with Claude Cloud Desktop

If you're using Claude Cloud Desktop:

1. Ensure the File System MCP is installed and enabled
2. Start a new chat with Claude
3. Say "I want to start a new Vibe worldbuilding session"
4. Claude will initialize the worldbuilding process
5. Follow the prompts and verify that files and folders are being created in your chosen directory

## How to Use

### Starting a New World

1. Use the command `start_worldbuilding()` to initialize the process
2. Share your world concept when prompted
3. The system will automatically:
   - Create necessary file structure
   - Generate a world foundation document
   - Develop initial taxonomies

### Main Workflows

The MCP supports three main workflows:

1. **Create/Update World Foundation**
   - Establish or refine the core concepts of your world
   - System will create the world foundation document in the proper format

2. **Create/Update Taxonomies**
   - Develop classification systems for major elements like regions, cultures, species, etc.
   - System will generate taxonomy documents in the proper format

3. **Create/Update Entries**
   - Create detailed entries for specific elements mentioned in your world
   - System will generate entry documents following appropriate templates

## Project Structure

The worldbuilding process will generate a directory structure like this:

```
your_world/
│
├── overview/
│   └── world_foundation.md
│
├── taxonomies/
│   ├── regions.md
│   ├── cultures.md
│   └── ...
│
└── entries/
    ├── place_one.md
    ├── character_one.md
    └── ...
```

## Future Development

### Planned Features

1. **Interlinking System**
   - Create automatic connections between related entries
   - Build a web of interlinked content that makes navigation intuitive

2. **Frontend Viewer**
   - Develop a web interface to browse and navigate your world
   - Allow clicking between interlinked pages for seamless exploration

3. **Image Generation**
   - Automatically generate images for entries
   - Visual representation of places, characters, and concepts
   - Include images directly on frontend pages

### Current Status

The core functionality for world creation is implemented. The interlinking system, frontend viewer, and image generation features are under development.

## Best Practices

- Start with a clear core concept
- Let the system guide you through the development process
- Focus on one aspect at a time (world foundation, taxonomies, entries)
- Use the taxonomies to organize your thinking about different elements
- Develop entries for the most interesting or important elements first
- Allow your world to grow organically from the foundation

