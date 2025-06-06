# Claude Development Guidelines

## Design Principles

### Outsource Intelligence to Client LLM
When building features that require content analysis, entity detection, or semantic understanding, **always create tools/functions that allow the client LLM to perform the analysis** rather than implementing the logic programmatically.

**Example**: For auto-stub generation, instead of writing code to parse content and detect entity references, create a tool that presents the content to the client LLM and asks it to identify what should become stub entries.

**Benefits**:
- Leverages the LLM's superior natural language understanding
- More flexible and context-aware than rule-based approaches  
- Easier to maintain and adapt to different content types
- Better handles edge cases and nuanced references

## Current Features

### Auto-Stub Generation
- Client LLM identifies entities in generated content that should become stub entries
- System creates minimal 1-2 sentence stub entries for new entities
- Integrated into `create_world_entry` workflow