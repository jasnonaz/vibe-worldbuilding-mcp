# Complete Worldbuilding Workflow

This document outlines the full end-to-end process for creating a complete world using the Vibe Worldbuilding MCP system.

## Overview

The complete workflow takes a world from initial concept to a fully realized, consistent, and published world with:
- Rich world overview and foundation
- Multiple taxonomies with custom guidelines
- 20-30+ detailed entries across all taxonomies
- Auto-generated stub entries for referenced entities
- Consistency analysis and improvements
- Generated images for key concepts
- Static website for exploration

## Phase 1: World Foundation

### 1.1 Create World Structure
Use `instantiate_world` with:
- Compelling world name
- Rich 3-4 paragraph world overview
- 4-6 initial taxonomies that capture the world's core elements

**Example tool call:**
```
mcp__vibe-worldbuilding__instantiate_world
Parameters:
- world_name: "The Crimson Archipelago"
- world_content: "A vast ocean world of floating islands connected by crimson coral bridges..."
- taxonomies: [
    {"name": "Sky Islands", "description": "Major floating landmasses and their unique characteristics"},
    {"name": "Coral Architects", "description": "The mysterious beings who shape the living bridges"},
    {"name": "Wind Ships", "description": "Vessels that navigate the aerial currents between islands"}
  ]
- base_directory: "./example_worlds"
```

This automatically:
- Creates world directory structure with metadata folder
- Generates visual style prompt based on world themes
- Creates overview images and favicon
- Sets up taxonomy folders

**Example taxonomies for fantasy worlds:**
- Characters/Heroes/Inhabitants
- Locations/Realms/Places
- Magic Systems/Powers/Abilities
- Artifacts/Items/Relics
- Organizations/Factions/Groups
- Creatures/Monsters/Beings

### 1.2 Generate Visual Style
After world creation:
1. Review the generated visual style request in `metadata/visual_style_request.md`
2. Generate a 2-3 sentence visual style description that captures the world's aesthetic
3. Save it to `metadata/visual_style.txt` using Claude Code's Write tool

**Example visual styles:**
- "Epic fantasy oil painting style with rich earth tones and golden accents. Dramatic chiaroscuro lighting with deep shadows and warm highlights."
- "Cyberpunk digital art with neon purple and electric blue accents against dark urban backgrounds. Moody atmospheric lighting with volumetric fog effects."
- "Clean vector art style with a limited palette of blues and whites. Soft, diffused lighting and minimalist composition."

### 1.3 Develop Taxonomies
For each taxonomy, use the streamlined LLM-first approach:

**Recommended:** Use `create_taxonomy_with_llm_guidelines` for best results:
1. Call with taxonomy name and description (no guidelines)
2. Respond to the generated prompt with flexible, engaging guidelines
3. Call again with your LLM-generated guidelines to create the taxonomy

**Example tool calls:**
```
# First call - get the prompt
mcp__vibe-worldbuilding__create_taxonomy_with_llm_guidelines
Parameters:
- world_directory: "./example_worlds/the-crimson-archipelago-20250614-123456"
- taxonomy_name: "Sky Islands"
- taxonomy_description: "Major floating landmasses and their unique characteristics"

# Second call - after generating guidelines
mcp__vibe-worldbuilding__create_taxonomy_with_llm_guidelines
Parameters:
- world_directory: "./example_worlds/the-crimson-archipelago-20250614-123456"
- taxonomy_name: "Sky Islands"
- taxonomy_description: "Major floating landmasses and their unique characteristics"
- llm_generated_guidelines: "[Your generated guidelines here...]"
```

**Alternative:** Use `create_taxonomy` (legacy two-step process):
1. Call without guidelines to get LLM-generated structure
2. Call again with the generated guidelines to create the taxonomy folder

The streamlined tool prevents workflow errors and ensures consistent use of the improved flexible guidelines system.

## Phase 2: Content Creation

### 2.1 Create Core Entries
Create 4-6 entries per taxonomy, focusing on:
- **Central characters/places** that drive the world's conflicts
- **Interconnected elements** that reference each other
- **Varying detail levels** - some detailed, some brief

**Example tool calls:**
```
# First call - get world context
mcp__vibe-worldbuilding__create_world_entry
Parameters:
- world_directory: "./example_worlds/the-crimson-archipelago-20250614-123456"
- taxonomy: "Sky Islands"
- entry_name: "The Celestial Spire"

# Second call - create entry with content
mcp__vibe-worldbuilding__create_world_entry
Parameters:
- world_directory: "./example_worlds/the-crimson-archipelago-20250614-123456"
- taxonomy: "Sky Islands"
- entry_name: "The Celestial Spire"
- entry_content: "# The Celestial Spire\n\nThe highest floating island in the archipelago..."
```

### 2.2 Auto-Stub Generation
The system automatically:
- Identifies entities mentioned in entries that don't exist yet
- Creates stub entries with 1-2 sentence descriptions
- Places them in appropriate taxonomies

### 2.3 Expand Content
Target 20-30+ total entries by:
- Expanding key stub entries into full entries
- Adding new entries that connect to existing ones
- Ensuring good coverage across all taxonomies

## Phase 3: Content Processing

### 3.1 Generate Descriptions
Use `generate_entry_descriptions` to:
- Analyze all entries for consistent description generation
- Create concise summaries for navigation and search

### 3.2 Apply Descriptions
Use `add_entry_frontmatter` to:
- Add generated descriptions to entry frontmatter
- Ensure consistent metadata across all entries

## Phase 4: Consistency Analysis

### 4.1 Run Analysis
Use `analyze_world_consistency` to:
- Sample 15-20 entries randomly
- Identify inconsistencies, contradictions, and missing connections
- Generate specific edit suggestions

### 4.2 Apply Fixes
Review the analysis and:
- Fix naming inconsistencies
- Resolve timeline conflicts
- Add missing cross-references
- Strengthen world connections

### 4.3 Iterative Improvement
- Run consistency analysis multiple times
- Each pass should find fewer issues
- Continue until no major inconsistencies remain

## Phase 5: Visual Enhancement

### 5.1 Image Prompt Generation
For key entries, use `generate_image_prompt_for_entry` to:
1. Call without `image_prompt` to get LLM guidance for optimal prompts
2. Generate 30-40 word image-specific prompts with visual details
3. Call again with the generated prompt to save it to entry frontmatter

### 5.2 Generate Images
Use `generate_image_from_markdown_file` for entries with image prompts:
- **Automatic Style Consistency**: Uses world visual style automatically
- **Priority Order**: World style > Image prompt > Fallback style
- **Organized Storage**: Images saved to `images/[taxonomy]/[entry].png`

**Target entries for images:**
- World overview (automatically created during instantiation)
- Key locations and districts
- Important characters and leaders
- Unique creatures and beings
- Significant artifacts and items

### 5.3 Image Integration
- Images automatically integrate into the world structure
- Both source markdown and static site include images
- Consistent visual style across all world imagery
- Gallery pages showcase all generated artwork

## Phase 6: Publication

### 6.1 Build Static Site
Use `build_static_site` to:
- Generate complete website with navigation
- Create taxonomy overview pages
- Build individual entry pages
- Include image galleries

### 6.2 Final Review
- Test site navigation and links
- Verify all content displays correctly
- Check image integration
- Validate taxonomy organization

## Quality Checkpoints

### Content Quality
- [ ] World overview is compelling and establishes core concepts
- [ ] Visual style saved to metadata/visual_style.txt
- [ ] Each taxonomy has 4+ entries
- [ ] Entries reference each other naturally
- [ ] Total entry count: 20-30+
- [ ] Mix of detailed and brief entries

### Consistency Quality
- [ ] No naming contradictions
- [ ] Timeline consistency
- [ ] Logical cross-references
- [ ] Consistent tone and style
- [ ] World rules are maintained

### Technical Quality
- [ ] All entries have proper frontmatter
- [ ] Visual style consistency across all images
- [ ] Image prompts saved to entry frontmatter where appropriate
- [ ] Images generate successfully using world style
- [ ] Static site builds without errors
- [ ] Navigation works correctly
- [ ] All links resolve properly

## Real-World Test Results

We tested this complete workflow with "The Shattered Realms" and achieved:

### Created Content
- **29 total entries** across 6 taxonomies
- **13 full detailed entries** with rich interconnections
- **16 stub entries** for referenced entities
- **Automatic image generation** for key concepts
- **Complete static website** with navigation

### Consistency Analysis Findings
The analysis of 20 random entries identified:
- Missing cross-references between related entries
- Opportunities to expand key stub entries
- Timeline relationships that could be clearer
- Organization connections needing strengthening

### Key Success Factors
1. **Rich world foundation** with clear central conflict (magical chaos)
2. **Interconnected taxonomies** that naturally reference each other
3. **Auto-stub generation** creating organic growth patterns
4. **Multiple consistency passes** finding and fixing issues
5. **Progressive expansion** from stubs to full entries

## Estimated Timeline

- **Phase 1**: 10-15 minutes (foundation)
- **Phase 2**: 30-45 minutes (content creation)
- **Phase 3**: 5-10 minutes (processing)
- **Phase 4**: 15-20 minutes (consistency)
- **Phase 5**: 10-15 minutes (images)
- **Phase 6**: 5-10 minutes (publication)

**Total**: 75-115 minutes for complete world

## Tips for Success

1. **Start with conflict** - Your world overview should establish central tensions
2. **Think interconnected** - Every entry should reference 2-3 other elements
3. **Embrace inconsistency** - Let the consistency tool find and fix issues
4. **Iterate frequently** - Run consistency analysis multiple times
5. **Mix detail levels** - Not every entry needs to be a novel
6. **Trust the automation** - Let stub generation guide organic growth

## Common Pitfalls

- Creating isolated entries that don't connect
- Making everything too detailed (content overload)
- Skipping consistency analysis phases
- Not iterating on feedback from analysis
- Forgetting to establish clear world rules early

This workflow ensures you end up with a rich, consistent, and explorable world that feels lived-in and interconnected.