"""Core worldbuilding prompts for starting and continuing projects.

This module contains prompts for fundamental worldbuilding activities like
starting new projects, continuing existing work, and establishing foundations.
"""

import mcp.types as types


def get_start_worldbuilding_prompt() -> types.GetPromptResult:
    """Get the prompt for starting a new worldbuilding project."""
    return types.GetPromptResult(
        description="Begin a new world project",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="""# Starting a New World

Welcome to worldbuilding! Let's create something amazing together.

## What is your world about?

Think about the core concept that makes your world unique. This could be:
- A central magical/technological system
- A unique physical law or property
- An interesting social structure
- A fascinating historical event
- A compelling conflict or tension

Take your time to describe your initial idea. Don't worry about details yet - we'll develop those together.

What draws you to this world concept? What excites you about exploring it further?"""
                )
            )
        ]
    )


def get_continue_worldbuilding_prompt() -> types.GetPromptResult:
    """Get the prompt for continuing work on an existing world."""
    return types.GetPromptResult(
        description="Resume work on an existing world",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="""# Continuing Your World

Welcome back to your worldbuilding project!

## Where we left off

To help me understand where we are in your world's development, please share:

1. **What world are you working on?** (Brief reminder of the core concept)
2. **What have you developed so far?** (Overview, taxonomies, specific entries)
3. **What would you like to focus on today?** (New areas, refinements, consistency checks)

You can also paste any existing content you'd like me to review or build upon.

What aspect of your world is calling to you today?"""
                )
            )
        ]
    )


def get_world_foundation_prompt() -> types.GetPromptResult:
    """Get the prompt for developing core world concepts and foundations."""
    return types.GetPromptResult(
        description="Develop core world concepts",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="""# Building Your World's Foundation

Let's establish the fundamental aspects of your world that everything else will build upon.

## Core Questions to Explore

**The Central Concept**
- What makes your world unique and interesting?
- What is the "big idea" that drives everything else?

**Physical Reality**
- How do the basic laws of physics, magic, or technology work?
- What are the fundamental forces that shape daily life?

**Scale and Scope**
- Is this a single location, planet, galaxy, or multiverse?
- What time period(s) does your world cover?

**Tone and Themes**
- What feelings should your world evoke?
- What questions or themes do you want to explore?

## Creating Your Foundation Document

We'll work together to create a foundational document that captures:
1. Your world's elevator pitch (1-2 sentences)
2. Core mechanics/systems
3. Key themes and tone
4. Scope and boundaries

What aspect would you like to start with?"""
                )
            )
        ]
    )


def get_workflow_prompt() -> types.GetPromptResult:
    """Get the prompt for worldbuilding process guidance."""
    return types.GetPromptResult(
        description="Worldbuilding process guidance",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="""# Worldbuilding Workflow Guide

Here's a systematic approach to building rich, cohesive fictional worlds:

## Phase 1: Foundation (Start Here)
1. **Core Concept** - What makes your world unique?
2. **Scope Definition** - How big is your world?
3. **Tone and Themes** - What feelings and ideas drive it?
4. **Basic Rules** - How do fundamental systems work?

## Phase 2: Structure (Build the Framework)
1. **Create Taxonomies** - Classification systems for major elements
2. **Map Relationships** - How do systems interact?
3. **Establish Constraints** - What are the limits and boundaries?
4. **Timeline Framework** - Key historical periods or events

## Phase 3: Development (Fill in Details)
1. **Priority Elements** - Develop the most important pieces first
2. **Cluster Building** - Create related groups of content
3. **Detail Layering** - Add depth gradually
4. **Connection Weaving** - Link elements together

## Phase 4: Refinement (Polish and Perfect)
1. **Consistency Review** - Check for contradictions
2. **Gap Analysis** - Find areas needing development
3. **Enhancement** - Improve existing content
4. **Testing** - Use your world in stories or scenarios

## Best Practices

**Quality Over Quantity**
- Better to have fewer, well-developed elements
- Deep development creates more interesting connections

**Organic Growth**
- Let your world evolve naturally
- Follow your interests and curiosity

**Regular Review**
- Periodically check for consistency
- Update older content as the world develops

**Documentation**
- Keep good records of what you've created
- Use clear organization and naming

Where are you in this process, and what would help you move forward?"""
                )
            )
        ]
    )


# Core prompt handlers mapping
CORE_PROMPT_HANDLERS = {
    "start-worldbuilding": get_start_worldbuilding_prompt,
    "continue-worldbuilding": get_continue_worldbuilding_prompt,
    "world-foundation": get_world_foundation_prompt,
    "workflow": get_workflow_prompt,
}


def handle_core_prompt(name: str) -> types.GetPromptResult:
    """Handle core worldbuilding prompt requests.
    
    Args:
        name: Prompt name
        
    Returns:
        GetPromptResult for the requested prompt
        
    Raises:
        ValueError: If prompt name is not recognized
    """
    if name not in CORE_PROMPT_HANDLERS:
        raise ValueError(f"Unknown core prompt: {name}")
    
    return CORE_PROMPT_HANDLERS[name]()