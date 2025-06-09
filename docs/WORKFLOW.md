# Vibe Worldbuilding MCP Workflow

This document outlines the proper sequence of MCP commands for building a complete world from concept to finished site.

## Complete Workflow

### 1. World Foundation
```
instantiate_world
├── world_name: "my-fantasy-realm"
├── world_content: "# Rich world concept with overview, core concepts, tone..."
└── base_directory: "./worlds"
```

**Creates:**
- World directory: `my-fantasy-realm-{timestamp}/`
- Basic folder structure: `overview/`, `entries/`, `images/`, `notes/`, `taxonomies/`
- World overview file: `overview/world-overview.md`

### 2. Taxonomy Creation (for each taxonomy)
```
generate_taxonomy_guidelines
├── taxonomy_name: "characters"
└── taxonomy_description: "The people, creatures, and entities in this world"

create_taxonomy_folders  
├── world_directory: "./worlds/my-fantasy-realm-{timestamp}"
├── taxonomy_name: "characters"
├── taxonomy_description: "The people, creatures, and entities in this world"
└── custom_guidelines: "{generated guidelines from previous step}"
```

**Creates:**
- Taxonomy overview: `taxonomies/characters-overview.md` (with custom guidelines)
- Entry directory: `entries/characters/`

### 3. Entry Creation (for each world element)
```
create_world_entry
├── world_directory: "./worlds/my-fantasy-realm-{timestamp}"
├── taxonomy: "characters"
├── entry_name: "The Dragon Rider"
└── entry_content: "Detailed description of the character..."
```

**Creates:**
- Entry file: `entries/characters/the-dragon-rider.md`
- **Auto-triggers:** `identify_stub_candidates` and `create_stub_entries` for any referenced entities

### 4. Image Generation (optional)
```
generate_image_from_markdown_file
├── filepath: "./worlds/my-fantasy-realm-{timestamp}/entries/characters/the-dragon-rider.md"
├── style: "character design"
└── aspect_ratio: "16:9"
```

**Creates:**
- Image file: `images/characters/the-dragon-rider.png`

### 5. Site Building
```
build_static_site
├── world_directory: "./worlds/my-fantasy-realm-{timestamp}"
└── action: "build"
```

**Creates:**
- Complete static website: `site/` directory
- Navigation structure for all taxonomies and entries
- Gallery with all generated images

## Example: Full World Creation

Here's the complete sequence used by the comprehensive test:

```python
# 1. Create world foundation
await handle_world_tool("instantiate_world", {
    "world_name": "mystic-realms",
    "world_content": "# The Mystic Realms\n\n## Overview\nFloating islands in magical aurora streams...",
    "base_directory": "./test-worlds"
})

# 2. Create each taxonomy
taxonomies = [
    {"name": "islands", "description": "Floating landmasses with unique magical properties"},
    {"name": "inhabitants", "description": "People, creatures, and entities"},
    {"name": "magic_systems", "description": "Schools and approaches to magic"},
    {"name": "artifacts", "description": "Magical items and relics"},
    {"name": "organizations", "description": "Groups, guilds, and societies"}
]

for taxonomy in taxonomies:
    # Generate custom guidelines
    guidelines_result = await handle_taxonomy_tool("generate_taxonomy_guidelines", {
        "taxonomy_name": taxonomy["name"],
        "taxonomy_description": taxonomy["description"]
    })
    
    # Create taxonomy with guidelines
    await handle_taxonomy_tool("create_taxonomy_folders", {
        "world_directory": str(world_directory),
        "taxonomy_name": taxonomy["name"], 
        "taxonomy_description": taxonomy["description"],
        "custom_guidelines": guidelines_result[0].text
    })

# 3. Create detailed entries
await handle_entry_tool("create_world_entry", {
    "world_directory": str(world_directory),
    "taxonomy": "islands",
    "entry_name": "The Floating Academy",
    "entry_content": "Detailed description with references to other entities..."
})
# Auto-stub generation happens automatically for any referenced entities

# 4. Generate images (optional)
await handle_image_tool("generate_image_from_markdown_file", {
    "filepath": f"{world_directory}/entries/islands/the-floating-academy.md",
    "style": "fantasy architecture",
    "aspect_ratio": "16:9"
})

# 5. Build final site
await handle_site_tool("build_static_site", {
    "world_directory": str(world_directory),
    "action": "build"
})
```

## Key Points

### Proper Command Sequence
1. **World first**: Always start with `instantiate_world`
2. **Taxonomies second**: Use the two-step process (`generate_taxonomy_guidelines` → `create_taxonomy_folders`)
3. **Entries third**: Create rich content with `create_world_entry`
4. **Images fourth**: Optionally generate visuals
5. **Site last**: Build the final website

### Auto-Stub Generation
- Happens automatically during `create_world_entry`
- LLM analyzes content and identifies referenced entities
- Creates minimal stub entries for new entities
- Respects existing entries (won't overwrite)

### File Naming Conventions
- Taxonomies: `taxonomy_name` → `taxonomy-name-overview.md` (underscores become hyphens)
- Entries: `entry_name` → `entry-name.md` (spaces become hyphens, lowercase)
- Images: `entry_name` → `entry-name.png` (matches entry naming)

### Testing the Workflow
Use the comprehensive test to validate the entire pipeline:
```bash
# Full workflow test (creates complete world)
python tests/test_e2e_comprehensive.py --verbose --skip-images

# Keep test world for inspection
python tests/test_e2e_comprehensive.py --verbose --skip-images
# (no --cleanup flag means the test world stays for exploration)
```

This test demonstrates the complete workflow by creating a rich fantasy world with multiple taxonomies, detailed entries, auto-generated stubs, and a full navigable website.