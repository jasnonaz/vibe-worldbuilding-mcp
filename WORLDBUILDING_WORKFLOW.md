# Worldbuilding Workflow Guide

This guide explains how to use the vibe-worldbuilding MCP tools to create a complete worldbuilding project.

## Overview

The worldbuilding system creates:
- **Structured world content** organized by taxonomies (characters, locations, artifacts, etc.)
- **Interconnected entries** with automatic crosslinking between related elements
- **Static websites** for browsing and sharing your world
- **AI-generated images** for visual representation of world elements

## Step-by-Step Workflow

### 1. Create a New World

Use `instantiate_world` to create the basic world structure:

```
- World name: "My Fantasy Realm"
- World content: Your foundational world overview/concept
- Initial taxonomies: Start with 2-3 core taxonomies (e.g., Characters, Locations, Artifacts)
```

**Creates:**
- World directory with timestamp
- Basic folder structure
- World overview file
- Initial taxonomy guidelines

### 2. Design Your Taxonomies

Before creating entries, plan your world's organization:

**Common taxonomies:**
- **Characters** - People, beings, entities
- **Locations** - Places, regions, buildings
- **Artifacts** - Items, weapons, magical objects
- **Organizations** - Factions, guilds, governments
- **Events** - Historical moments, ongoing situations
- **Concepts** - Magic systems, technologies, philosophies

**For each new taxonomy, use `create_taxonomy_folders`:**
- Taxonomy name and description
- Custom entry guidelines specific to your world

### 3. Create World Entries

Use `create_world_entry` in this order:

#### A. Foundation Entries First
Start with the most important, central elements:
- Key characters (protagonists, major figures)
- Important locations (capitals, home bases)
- Core artifacts or concepts

#### B. World Context Integration
- Each new entry automatically receives context about existing entries
- The system suggests crosslinks to related elements
- Links are selective (2-4 meaningful connections per entry)

#### C. Call the tool twice:
1. **First call** (empty content): Get world context and linking suggestions
2. **Second call** (with content): Create the actual entry with crosslinks

**Example workflow:**
```
1. create_world_entry("characters", "Queen Lyralei", "") → Get context
2. create_world_entry("characters", "Queen Lyralei", "Your detailed content with crosslinks")
```

### 4. Auto-Stub Generation (Optional)

After creating detailed entries, use auto-stub generation to expand your world:

1. The system analyzes your entries for mentioned entities
2. Suggests new stub entries for significant references
3. Use `create_stub_entries` to create placeholder entries
4. Later expand stubs into full entries

### 5. Generate Entry Descriptions (Optional)

For existing entries without YAML frontmatter:

1. `generate_entry_descriptions` - Analyze entries needing descriptions
2. `apply_entry_descriptions` - Add generated descriptions to frontmatter

### 6. Build Your World Website

Use `build_static_site` to create a browsable website:

- Generates HTML pages for all entries
- Creates taxonomy navigation
- Converts markdown links to working HTML links
- Includes generated images

**Always rebuild after making changes to see updates!**

## Best Practices

### Entry Creation Strategy

**Start Small, Build Out:**
1. Create 3-5 foundation entries in your core taxonomies
2. Let auto-stub generation suggest expansions
3. Gradually develop stubs into full entries
4. Add new taxonomies as your world grows

**Content Guidelines:**
- **200-500 words** for full entries
- **1-2 sentences** for stub entries
- Focus on unique characteristics and world connections
- Use selective crosslinking (2-4 meaningful links per entry)

### Linking Strategy

**Link when:**
- The reference is central to understanding this entry
- Creates meaningful narrative connections
- Provides important context or background

**Don't link when:**
- It's just a passing mention
- The reference is obvious or redundant
- It would create link overload

### Testing and Validation

After any changes:
1. **Rebuild the site** using `build_static_site`
2. **Verify site serves correctly** - check HTML output
3. **Test crosslinks** - ensure markdown converts to working links
4. **Check navigation** - confirm all entries appear in site structure

## Tool Reference

### Core Tools
- `instantiate_world` - Create new world project
- `create_taxonomy_folders` - Add new taxonomy with guidelines
- `create_world_entry` - Create detailed world entries
- `build_static_site` - Generate website

### Expansion Tools
- `identify_stub_candidates` - Analyze entries for expansion opportunities
- `create_stub_entries` - Create multiple placeholder entries
- `generate_entry_descriptions` - Create YAML frontmatter descriptions
- `apply_entry_descriptions` - Add descriptions to existing entries

### Utility Tools
- `save_world_content` - Save standalone markdown files
- `read_world_content` - Read existing content
- `list_world_files` - Browse world structure
- `generate_image_from_markdown_file` - Create images for entries

## Example Complete Workflow

```
1. instantiate_world("Mystical Archipelago", world_concept, [characters, locations, artifacts])

2. create_taxonomy_folders("organizations", "Guilds and factions", custom_guidelines)

3. create_world_entry("characters", "Captain Marina Saltwind", "") → Review context
   create_world_entry("characters", "Captain Marina Saltwind", detailed_content)

4. create_world_entry("locations", "Port Starfall", "") → Review context  
   create_world_entry("locations", "Port Starfall", detailed_content)

5. create_world_entry("artifacts", "The Compass of Winds", "") → Review context
   create_world_entry("artifacts", "The Compass of Winds", detailed_content)

6. identify_stub_candidates(entry_content) → Review suggestions
   create_stub_entries([suggested_stubs])

7. build_static_site() → Generate website

8. Iterate: expand stubs, add entries, rebuild site
```

This creates a rich, interconnected world with a browsable website showcasing all your creative work!