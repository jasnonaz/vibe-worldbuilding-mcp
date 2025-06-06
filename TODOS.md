# Vibe Worldbuilder TODOs

## High Priority

### Fix Taxonomy Creation Workflow
- **Issue**: The two-step taxonomy creation process (generate_taxonomy_guidelines → create_taxonomy_folders) isn't working smoothly
- **Problem**: Users need to manually copy guidelines between tools, which is error-prone
- **Solution Options**:
  1. Combine back into single tool with better prompting
  2. Add better validation/error messages to enforce workflow
  3. Create a wrapper tool that handles both steps
- **Status**: Pending

### Add End-to-End Generation Tool
- **Issue**: Need a way to automatically generate complete worlds for testing
- **Requirements**:
  1. Create world structure
  2. Generate multiple taxonomies with guidelines
  3. Create sample entries for each taxonomy
  4. Generate images
  5. Build static site
- **Purpose**: Testing and demonstration without manual steps
- **Status**: Pending