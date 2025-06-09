# Vibe Worldbuilding MCP

A Model Context Protocol (MCP) server for creating detailed fictional worlds with Claude, complete with automatic image generation.

## Overview

This MCP helps you build rich, cohesive fictional worlds through a structured approach to worldbuilding. It uses Claude's capabilities to help you develop concepts, explore details, and maintain consistency. The MCP can also generate images to visually represent your world's elements using Google's Imagen API.

## Features

- **Structured Worldbuilding Prompts**: Guided workflows for developing different aspects of your world
- **Content Management**: Save, read, and organize your worldbuilding content in markdown files  
- **Auto-Stub Generation**: Automatically identify and create stub entries for entities mentioned in your content
- **Image Generation**: Create visual representations of your world elements using Google Imagen
- **Static Site Generation**: Build beautiful websites from your worldbuilding content using Astro
- **Consistency Tools**: Review and maintain coherence across your world's elements
- **Flexible Workflow**: Support for both new projects and continuing existing work

## Installation

### Prerequisites

- Python 3.8 or higher
- MCP CLI tool
- FAL API key (for image generation)

### Setup

1. **Install the MCP CLI**:
   ```bash
   pip install mcp
   ```

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a FAL API Key**:
   - Visit [FAL AI](https://fal.ai/)
   - Create an account and get your API key for Imagen4 access

4. **Install the Vibe Worldbuilding MCP**:
   ```bash
   cd /path/to/vibe-worldbuilder
   mcp install vibe_worldbuilding_server.py -v FAL_KEY=your_fal_api_key_here
   ```

   The `-v` flag sets the environment variable needed for image generation. If you don't have a FAL API key, you can still use the MCP for worldbuilding without image generation:
   ```bash
   mcp install vibe_worldbuilding_server.py
   ```

### Development Mode

To test the MCP in development mode:
```bash
mcp dev vibe_worldbuilding_server.py -v FAL_KEY=your_fal_api_key_here
```

### Claude Desktop Configuration

To use this MCP with Claude Desktop, add the following configuration to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "vibe-worldbuilding": {
      "command": "python",
      "args": ["/path/to/vibe-worldbuilder/vibe_worldbuilding_server.py"],
      "env": {
        "FAL_KEY": "your_fal_api_key_here"
      }
    }
  }
}
```

**Important**: Replace `/path/to/vibe-worldbuilder/` with the actual absolute path to your vibe-worldbuilder directory, and replace `your_fal_api_key_here` with your actual FAL API key.

The configuration file is typically located at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

After adding the configuration, restart Claude Desktop to load the MCP server.

## How to Use

The MCP provides several prompts to guide your worldbuilding process:

### Available Prompts

- **start-worldbuilding** - Begin a new world project
- **continue-worldbuilding** - Resume work on an existing world
- **world-foundation** - Develop the core concepts of your world
- **taxonomy** - Create classification systems for world elements
- **world-entry** - Create detailed entries for specific elements
- **consistency-review** - Check for logical consistency
- **entry-revision** - Revise and improve existing entries
- **workflow** - Get guidance on the overall process

### Available Tools

- **save_world_content** - Save worldbuilding content to markdown files
- **read_world_content** - Read existing worldbuilding files
- **list_world_files** - List all worldbuilding files in a directory
- **instantiate_world** - Create a complete world project structure in a uniquely named folder
- **generate_taxonomy_guidelines** - Generate structured entry guidelines for a specific taxonomy type
- **create_taxonomy_folders** - Create a taxonomy with custom guidelines for a world project
- **create_world_entry** - Create entries within taxonomies that automatically reference the taxonomy overview
- **identify_stub_candidates** - Analyze entry content to identify entities that should become stub entries
- **create_stub_entries** - Create multiple stub entries based on analysis
- **generate_image_from_markdown_file** - Generate images from your content (requires API key)
- **build_static_site** - Generate a static website from your worldbuilding content

## Image Generation

The MCP can generate images for your world elements using FAL's Imagen4 API. After creating a markdown file for an entry, taxonomy, or other element:

1. Use the `generate_image_from_markdown_file` tool with the path to your markdown file
2. The tool will:
   - Read the content of your markdown file
   - Extract the title and description
   - Generate an appropriate image using FAL's Imagen4 API
   - Save the image in an "images" folder next to your markdown file
3. Options available:
   - **Style**: Art style for the image (default: "fantasy illustration")
   - **Aspect ratio**: Choose from 1:1, 16:9, 9:16, 3:4, or 4:3

You can then upload the generated image to Claude to view it in your conversation.

## Auto-Stub Generation

The MCP includes intelligent stub generation to help you quickly expand your world by creating placeholder entries for entities mentioned in your content.

### How It Works

1. **Create an entry** using `create_world_entry` 
2. **Analyze the content** using `identify_stub_candidates` - this presents the entry content to Claude along with existing taxonomies and entries
3. **Claude identifies** entities that deserve their own entries (characters, locations, items, etc.)
4. **Create stubs** using `create_stub_entries` with the identified entities
5. **Stub entries** are created with brief descriptions and marked as stubs for future development

### Stub Entry Features

- **Brief descriptions**: 1-2 sentences explaining what the entity is
- **Proper categorization**: Placed in appropriate taxonomies (existing or new)
- **Stub markers**: Clearly marked as needing further development
- **Avoiding duplicates**: Won't create entries that already exist
- **Taxonomy creation**: Can create new taxonomies if needed for new entity types

This feature helps you maintain comprehensive world coverage without losing track of important elements mentioned in your detailed entries.

## Static Site Generation

The MCP can generate beautiful static websites from your worldbuilding content using Astro. This creates a navigable website that showcases your world with:

- **Homepage** with world overview and navigation
- **Taxonomy pages** with lists of all entries in each category
- **Entry pages** with full content and images
- **Responsive design** that works on all devices
- **Fast performance** with optimized static files

### Using Static Site Generation

1. **Build your world** using the standard worldbuilding tools
2. **Generate images** for visual content (optional but recommended)
3. **Use the `build_static_site` tool** with your world directory path
4. **View your website** by serving the generated `site/` folder:
   ```bash
   cd your-world-directory/site
   python3 -m http.server 8080
   ```
   Then open http://localhost:8080 in your browser

## Recommended Workflow

1. **Start** with the `start-worldbuilding` prompt to begin
2. **Create** your world foundation document with core concepts
3. **Instantiate** your world project using the `instantiate_world` tool with your foundation content
4. **Add taxonomies** by first using `generate_taxonomy_guidelines` to create custom entry guidelines, then `create_taxonomy_folders` to create the taxonomy with those guidelines
5. **Develop** specific entries using `create_world_entry` which automatically references the taxonomy context
6. **Create stub entries** for referenced entities using `identify_stub_candidates` and `create_stub_entries` tools
7. **Generate** images for your world elements to bring them to life visually
8. **Review** regularly for consistency and coherence using the consistency-review prompt
9. **Continue** each new session with `continue-worldbuilding`

## Example Session

```
User: Let's create a new world.

[User selects the "start-worldbuilding" prompt from the MCP menu]

Claude: [Displays the worldbuilding prompt]

User: I'd like to create a world where sound has magical properties.

Claude: [Helps develop the concept and explores implications]

User: Let's create the world project structure.

Claude: [Uses instantiate_world tool with the world content and any initial taxonomies]

User: I want to add a "religions" taxonomy to develop the belief systems.

Claude: [Uses create_taxonomy_folders tool with taxonomy name and description of how religions work in this world]

User: Let me create an entry for the "Church of Resonance".

Claude: [Uses create_world_entry tool which automatically includes the religions taxonomy context]

User: I notice this entry mentions several characters and a sacred artifact. Let's create stubs for them.

Claude: [Uses identify_stub_candidates tool to analyze the content, then create_stub_entries to generate placeholder entries]

User: Now generate an image for the world overview.

[User uses the generate_image_from_markdown_file tool]

Claude: [Generates an image and saves it to the images folder]
```

## File Organization

The MCP automatically creates organized project folders and will create:

### Project Structure
Each world gets its own unique folder named: `{world-name}-{unique-suffix}`

**Unique suffix options**:
- `timestamp` (default): `my-world-20250603-143022`
- `uuid`: `my-world-a1b2c3d4-e5f6-7890-abcd-ef1234567890`  
- `short-uuid`: `my-world-a1b2c3d4`

### Folder Structure
- **overview/**: Core world documents and foundation
- **taxonomies/**: Taxonomy overview files (no subfolders)
- **entries/**: Detailed entries organized by taxonomy
- **images/**: Centralized image storage organized by category
- **notes/**: Development notes and work-in-progress content

### File Organization
- `overview/world-overview.md` - Core world concept
- `taxonomies/{category}-overview.md` - Taxonomy descriptions (flat structure)
- `entries/{category}/{entry-name}.md` - Detailed world elements
- `images/{category}/{image-name}.png` - Organized visual content

## Requirements

- **FAL API key** for Imagen4 (set as the `FAL_KEY` environment variable)
- **Requests Python library** (`requests`)
- **MCP CLI tool**

## Tips for Success

- **Build incrementally** - Start with core concepts before diving into details
- **Create clusters** of related content that build on each other
- **Review regularly** for consistency and logical coherence
- **Focus on quality** over quantity - fewer, well-developed elements are better
- **Follow your interests** - Let your world emerge organically
- **Use images** to inspire further worldbuilding and bring concepts to life

## Troubleshooting

### Image Generation Issues

- **No API key**: Set the `FAL_KEY` environment variable
- **API errors**: Check your FAL API quota and billing status
- **Import errors**: Install `requests` with `pip install requests`

### File Issues

- **Permission errors**: Ensure you have write permissions in your working directory
- **Path issues**: Use absolute paths or ensure your working directory is correct

## Testing

The vibe-worldbuilding system includes a comprehensive test suite to ensure all components work correctly together.

### Test Structure

The testing framework uses isolated test worlds to validate the complete worldbuilding pipeline:

```
tests/                # Test suite code
├── run_tests.py      # Unified test runner
├── test_e2e_simple.py       # Simple integration test  
└── test_e2e_integration.py  # Full integration test

test-worlds/          # Isolated test environments (git-ignored)
├── unit/             # Unit test worlds for specific features
├── integration/      # End-to-end integration test worlds
└── performance/      # Performance and load test worlds
```

### Running Tests

**Unified Test Runner:**
```bash
# Run all tests
python tests/run_tests.py

# Run specific test type
python tests/run_tests.py integration --verbose
python tests/run_tests.py unit --verbose  
python tests/run_tests.py performance --verbose

# Keep test worlds for inspection
python tests/run_tests.py integration --no-cleanup --verbose
```

**Individual Tests:**
```bash
# Simple test (basic functionality)
python tests/test_e2e_simple.py --verbose --cleanup

# Comprehensive test (complete world creation)  
python tests/test_e2e_comprehensive.py --verbose --skip-images

# Full integration test (all features)
python tests/test_e2e_integration.py --verbose --cleanup
```

**Test Options:**
- `--verbose`: Show detailed test output
- `--cleanup`: Remove test worlds after completion
- `--base-dir ./test-worlds`: Specify test directory (default: current directory)

### Test Coverage

The test suite validates:

1. **World Creation**: Project instantiation with proper directory structure
2. **Taxonomy Management**: Creating taxonomies with custom guidelines
3. **Entry Creation**: Content creation with auto-stub generation
4. **Image Generation**: Visual content creation (requires FAL API key)
5. **Site Building**: Static website generation with gallery functionality
6. **Content Validation**: Verifying generated content structure and links
7. **File Organization**: Ensuring proper file placement and naming
8. **Error Handling**: Testing failure scenarios and recovery

### Test Environments

Tests run in isolated `test-worlds/` directories that:
- Don't interfere with real worldbuilding projects
- Can be safely created and destroyed
- Use deterministic naming for consistency
- Support parallel test execution

### Test Data

Test worlds use predefined fantasy content to ensure:
- Consistent test results across runs
- Comprehensive feature coverage
- Realistic usage patterns
- Edge case validation

### Performance Testing

Integration tests include timing measurements to detect:
- Performance regressions
- Resource usage patterns
- Bottlenecks in the pipeline
- API rate limiting issues

### Adding New Tests

When adding new features:
1. Add unit tests for individual components
2. Update integration tests for end-to-end validation
3. Include error case testing
4. Document test data requirements
5. Update test coverage metrics

### Test Configuration

Tests respect environment variables:
- `FAL_KEY`: For image generation testing
- `TEST_TIMEOUT`: Maximum test duration (default: 300s)
- `TEST_CLEANUP`: Auto-cleanup test worlds (default: true)

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please feel free to submit issues and enhancement requests.

### Development Workflow

1. **Fork and clone** the repository
2. **Create test worlds** in `test-worlds/` for development
3. **Run the test suite** to ensure existing functionality works
4. **Add tests** for new features or bug fixes
5. **Submit a pull request** with test results