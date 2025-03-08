# Vibe Worldbuilding MCP

A Model Context Protocol (MCP) for creating detailed fictional worlds with Claude, complete with automatic image generation.

## Overview

This MCP helps you build rich, cohesive fictional worlds through a structured approach to worldbuilding. It uses Claude's capabilities to help you develop concepts, explore details, and maintain consistency. The MCP can also generate images to visually represent your world's elements.

## Installation

1. Install the MCP CLI:
   ```
   pip install mcp
   ```

2. Install required dependencies:
   ```
   pip install google-generativeai
   ```

3. Install the Vibe Worldbuilding MCP with your Google AI API key:
   ```
   cd /path/to/vibe-worldbuilding-mcp
   mcp install vibe_worldbuilding_server.py -v IMAGEN_API_KEY=your_api_key_here
   ```

   The `-v` flag sets the environment variable needed for image generation. If you don't have a Google AI API key for Imagen, you can still use the MCP for worldbuilding, but the image generation feature won't work.

   Alternatively, you can test the MCP in development mode:
   ```
   mcp dev vibe_worldbuilding_server.py -v IMAGEN_API_KEY=your_api_key_here
   ```

## How to Use

The MCP provides several prompts to guide your worldbuilding process:

1. **start-worldbuilding** - Begin a new world project
2. **continue-worldbuilding** - Resume work on an existing world
3. **world-foundation** - Develop the core concepts of your world
4. **taxonomy** - Create classification systems for world elements
5. **world-entry** - Create detailed entries for specific elements
6. **consistency-review** - Check for logical consistency
7. **entry-revision** - Revise and improve existing entries
8. **workflow** - Get guidance on the overall process

### Image Generation

The MCP can generate images for your world elements. After creating a markdown file for an entry, taxonomy, or other element, use the `generate_image_from_markdown_file` tool:

```
Use the generate_image_from_markdown_file tool with path="/path/to/your/file.md"
```

The tool will:
1. Read the content of your markdown file
2. Extract the title and description
3. Generate an appropriate image using Google's Imagen API
4. Save the image in an "images" folder next to your markdown file

You can then upload the generated image to Claude to view it in your conversation.

## Worldbuilding Workflow

1. Start with the **start-worldbuilding** prompt to begin
2. For each new session, begin with **continue-worldbuilding**
3. Develop your world in this order:
   - World foundation (core concept and overview)
   - Taxonomies (classification systems)
   - Specific entries (detailed articles)
4. Let your world grow organically by developing elements that interest you
5. Generate images for your world elements to bring them to life visually

## Example Session

```
User: Let's create a new world.

[User selects the "start-worldbuilding" prompt from the MCP menu]

Claude: [Displays the worldbuilding prompt]

User: I'd like to create a world where sound has magical properties.

Claude: [Helps develop the concept and explores implications]

User: Let's save this as my world overview file.

Claude: [Saves the content to world-overview.md]

User: Now generate an image for this overview.

[User uses the generate_image_from_markdown_file tool]

Claude: [Generates an image and saves it to disk]
```

## Requirements

- A Google AI API key for Imagen (set as the IMAGEN_API_KEY environment variable)
- Google Generative AI Python library (`google-generativeai`)
- MCP CLI tool


## Tips for Success

- Build your world incrementally, starting with core concepts
- Create clusters of related content
- Review for consistency regularly
- Focus on quality over quantity
- Let your world emerge organically
- Use generated images to inspire further worldbuilding
