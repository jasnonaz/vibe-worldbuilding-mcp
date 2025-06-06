"""Entry-related prompts for creating and working with world entries.

This module contains prompts for creating detailed entries and working
with specific world elements within taxonomies.
"""

import mcp.types as types


def get_world_entry_prompt() -> types.GetPromptResult:
    """Get the prompt for creating detailed world entries."""
    return types.GetPromptResult(
        description="Create detailed world entries",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="""# Creating Detailed World Entries

Let's dive deep into a specific element of your world and create a comprehensive entry that brings it to life.

## Types of Entries

**Places**
- Cities, regions, landmarks, or buildings
- Include geography, culture, history, and notable features

**Characters/Beings**
- Important individuals, species, or groups
- Cover appearance, personality, abilities, and relationships

**Objects/Artifacts**
- Magical items, technologies, or significant objects
- Detail function, history, appearance, and impact

**Events/Phenomena**
- Historical events, natural phenomena, or ongoing situations
- Explain causes, effects, timeline, and significance

**Systems/Concepts**
- Magic systems, governments, religions, or philosophies
- Break down mechanics, beliefs, structures, and implications

## Entry Structure

Each entry should include:
1. **Overview** - Quick summary and significance
2. **Description** - Detailed explanation of key aspects
3. **History/Context** - Background and development
4. **Relationships** - Connections to other world elements
5. **Impact** - Effects on the broader world

What specific element of your world would you like to develop into a detailed entry?"""
                )
            )
        ]
    )


# Entry prompt handlers mapping
ENTRY_PROMPT_HANDLERS = {
    "world-entry": get_world_entry_prompt,
}


def handle_entry_prompt(name: str) -> types.GetPromptResult:
    """Handle entry-related prompt requests.
    
    Args:
        name: Prompt name
        
    Returns:
        GetPromptResult for the requested prompt
        
    Raises:
        ValueError: If prompt name is not recognized
    """
    if name not in ENTRY_PROMPT_HANDLERS:
        raise ValueError(f"Unknown entry prompt: {name}")
    
    return ENTRY_PROMPT_HANDLERS[name]()