# Claude Development Guidelines

## Claude Code File Location Requirements

Claude Code expects this CLAUDE.md file at the project root for automatic discovery:
- Claude reads CLAUDE.md files recursively from the current working directory up to root
- Project-specific guidelines should be in the root CLAUDE.md and committed to source control
- This enables consistent development practices across team members and sessions
- The file is automatically loaded when Claude Code runs in this project directory

## Project Scope
**This project builds the worldbuilding MCP server and tools - NOT individual worlds**:
- We develop the MCP server that enables worldbuilding
- We create tools that generate, manage, and process world content
- We do NOT create one-off scripts to fix specific worlds
- All fixes should be implemented in the MCP tools themselves
- Example worlds are reference implementations, not the primary deliverable

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

### Modular Architecture (Phase 2 Complete)
- **entries/creation.py** (234 lines): Entry creation with context integration
- **entries/stub_generation.py** (289 lines): Auto-stub analysis and creation  
- **entries/content_processing.py** (293 lines): Batch description operations
- **entries/utilities.py** (204 lines): Shared helper functions
- **tools/entries.py**: Clean router pattern for backward compatibility

## Development Workflow

### Adding New Features
1. **Design**: Plan the feature with LLM-first principles
2. **Schema**: Define types and interfaces in `types/` module
3. **Implementation**: Build in focused, single-purpose modules
4. **Integration**: Connect to main server with minimal coupling
5. **Testing**: Verify functionality works end-to-end

### Debugging Common Issues
**When code doesn't behave as expected, it's usually logical flow issues, NOT caching:**
- **Multiple functions**: Check if there are multiple similar functions being called
- **Tool routing**: Verify the correct handler is being invoked by the MCP server
- **Parameter flow**: Trace how arguments flow through the call stack
- **Function precedence**: Look for function name conflicts or import issues
- **Don't assume caching**: Module import issues are rare - focus on logic first

### Code Quality Standards
- **ALWAYS run tests before committing**: Use `python tests/test_e2e_simple.py` or comprehensive tests
- Run `python scripts/lint.py` before committing
- Follow the 200-500 line module size guideline
- Maintain backward compatibility for MCP tool signatures
- Use comprehensive integration tests in `tests/` directory
- Document architectural decisions in `docs/ARCHITECTURE.md`

## Testing Infrastructure
- **Comprehensive E2E tests**: Full worldbuilding pipeline validation
- **Integration tests**: MCP tool workflow verification
- **Test isolation**: Automated cleanup of test worlds
- **CI/CD ready**: Structured test suite in `tests/` directory

## Worldbuilding Workflow and Site Building
- **Check the workflow documentation**: For detailed worldbuilding instructions and site building, refer to `docs/COMPLETE_WORKFLOW.md`
- **Building static sites**: Use the MCP tool `mcp__vibe-worldbuilding__build_static_site` with parameters:
  - `world_directory`: Path to the world folder
  - `action`: "build" (to generate static files)
- **Complete workflow phases**: The workflow document outlines all phases from world foundation through publication

## Important Instruction Reminders
- Do what has been asked; nothing more, nothing less
- NEVER create files unless they're absolutely necessary for achieving your goal
- ALWAYS prefer editing an existing file to creating a new one
- NEVER proactively create documentation files (*.md) or README files unless explicitly requested