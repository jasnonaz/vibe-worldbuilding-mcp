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

## Architecture Principles

### File Size and Modularity
**Keep modules focused and manageable for Claude Code:**
- **200-500 lines per file**: Optimal for Claude to understand full context quickly
- **Single responsibility**: Each module should handle one clear aspect of functionality
- **Clear interfaces**: Well-defined functions with type hints and docstrings
- **Minimal coupling**: Modules should depend on abstractions, not implementations

### Project Structure Guidelines
```
vibe_worldbuilding/
├── server.py              # Main MCP server setup (~100 lines)
├── config.py              # Configuration and constants (~50 lines)
├── prompts/               # Organized by prompt category
├── tools/                 # One file per logical tool group
├── utils/                 # Shared utilities and helpers
└── types/                 # Type definitions and schemas
```

### Refactoring Strategy
1. **Extract schemas first**: Create type definitions before splitting logic
2. **Group related functionality**: Tools that work together stay together
3. **Preserve interfaces**: Maintain existing MCP tool signatures during refactoring
4. **Test incrementally**: Verify functionality after each phase
5. **Clear imports**: Make dependencies explicit and minimal

### Benefits for Claude Code
- **Faster analysis**: Smaller files load and understand quickly
- **Better error isolation**: Issues contained to specific modules
- **Easier navigation**: Clear module boundaries and responsibilities
- **Focused context**: Claude can understand each piece in isolation
- **Incremental development**: Add features without touching core logic

## Current Features

### Auto-Stub Generation
- Client LLM identifies entities in generated content that should become stub entries
- System creates minimal 1-2 sentence stub entries for new entities
- Integrated into `create_world_entry` workflow

## Development Workflow

### Adding New Features
1. **Design**: Plan the feature with LLM-first principles
2. **Schema**: Define types and interfaces in `types/` module
3. **Implementation**: Build in focused, single-purpose modules
4. **Integration**: Connect to main server with minimal coupling
5. **Testing**: Verify functionality works end-to-end