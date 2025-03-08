# Image Generation Guide for Vibe Worldbuilding

This guide explains how to use the image generation feature in the Vibe Worldbuilding MCP.

## Setup

Before you can generate images, you need to:

1. Get an API key for Google's Imagen API
2. Set it as an environment variable:
   ```
   export IMAGEN_API_KEY="your_api_key_here"
   ```
   
   On Windows, use:
   ```
   set IMAGEN_API_KEY=your_api_key_here
   ```

3. Install the required Python library:
   ```
   pip install google-generativeai
   ```

## Generating Images

After you've created a markdown file (such as a world overview, taxonomy, or entry), you can generate an image for it using the `generate_image_from_markdown_file` tool:

```
Use the generate_image_from_markdown_file tool with path="/path/to/your/file.md"
```

### How It Works

The tool:
1. Reads your markdown file
2. Extracts the title (first heading)
3. Extracts a description from the first few paragraphs
4. Creates a prompt for image generation
5. Calls the Imagen API to generate an image
6. Saves the image in an "images" folder next to your markdown file

### Example

Let's say you've created a file called "crystal_forest.md" with the following content:

```markdown
# The Crystal Forest

## Overview
The Crystal Forest is a magical woodland where trees have crystalline trunks and branches. The sunlight refracts through these crystal trees, creating rainbows that dance across the forest floor.

## Geography
Located in the northeastern region of the continent, the Crystal Forest spans approximately 500 square miles.
```

You can generate an image for this entry with:

```
Use the generate_image_from_markdown_file tool with path="/path/to/Entries/places/crystal_forest.md"
```

The tool will create an image that represents the Crystal Forest and save it as "images/the_crystal_forest.png".

## Tips for Better Images

For the best results:

- Make sure your markdown file has a clear title (first heading)
- Include descriptive details in the first few paragraphs
- Be specific about visual aspects (colors, sizes, materials, etc.)
- Keep in mind that the tool uses only the title and first few paragraphs for context

## Troubleshooting

If you encounter issues:

- Check that your API key is correctly set
- Verify the file path is correct
- Ensure the markdown file exists and has content
- Check that you have permissions to create an images directory
- If the image looks wrong, try editing your markdown to include more visual details
