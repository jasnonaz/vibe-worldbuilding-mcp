"""Taxonomy-related prompts for classification systems.

This module contains prompts specifically for creating and working with
taxonomies - the classification systems that organize world elements.
"""

import mcp.types as types


def get_taxonomy_prompt() -> types.GetPromptResult:
    """Get the prompt for creating classification systems and taxonomies."""
    return types.GetPromptResult(
        description="Create classification systems",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="""# Creating World Taxonomies

Taxonomies help organize and categorize the elements of your world, creating systematic frameworks that ensure consistency and inspire new ideas.

## Types of Taxonomies to Consider

**Social/Cultural Systems**
- Government types and structures
- Social classes or castes
- Cultural groups and ethnicities
- Professions and roles

**Magical/Technological Systems**
- Schools or types of magic
- Technology categories and advancement levels
- Energy sources and their applications

**Biological/Ecological**
- Species and subspecies
- Ecosystems and biomes
- Evolutionary relationships

**Geographic/Spatial**
- Region types and climates
- Settlement categories
- Architectural styles

**Temporal/Historical**
- Era classifications
- Event types and scales
- Calendar systems

## Creating Your Taxonomy

Choose a category that's important to your world and we'll create a systematic classification. This will include:
1. Clear categories and subcategories
2. Defining characteristics for each type
3. Examples of each category
4. Relationships between categories

What type of classification system interests you most for your world?"""
                )
            )
        ]
    )


# Taxonomy prompt handlers mapping
TAXONOMY_PROMPT_HANDLERS = {
    "taxonomy": get_taxonomy_prompt,
}


def handle_taxonomy_prompt(name: str) -> types.GetPromptResult:
    """Handle taxonomy-related prompt requests.
    
    Args:
        name: Prompt name
        
    Returns:
        GetPromptResult for the requested prompt
        
    Raises:
        ValueError: If prompt name is not recognized
    """
    if name not in TAXONOMY_PROMPT_HANDLERS:
        raise ValueError(f"Unknown taxonomy prompt: {name}")
    
    return TAXONOMY_PROMPT_HANDLERS[name]()