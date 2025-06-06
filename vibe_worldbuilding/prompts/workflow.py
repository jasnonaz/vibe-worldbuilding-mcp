"""Workflow and revision prompts for maintaining and improving worlds.

This module contains prompts for consistency checking, entry revision,
and other maintenance activities for existing worldbuilding projects.
"""

import mcp.types as types


def get_consistency_review_prompt() -> types.GetPromptResult:
    """Get the prompt for reviewing world consistency and coherence."""
    return types.GetPromptResult(
        description="Review world consistency",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="""# World Consistency Review

Let's examine your world for logical consistency, internal coherence, and potential areas that need development or revision.

## Areas to Check

**Internal Logic**
- Do your world's rules work consistently?
- Are there contradictions in how systems operate?
- Do cause-and-effect relationships make sense?

**Cultural Coherence**
- Do societies develop logically from their circumstances?
- Are belief systems and values internally consistent?
- Do economic and political systems align with the world's reality?

**Temporal Consistency**
- Does your world's history flow logically?
- Are technological/magical advancement rates reasonable?
- Do events have appropriate consequences?

**Geographic Logic**
- Do climates, ecosystems, and geography make sense together?
- Are trade routes and settlements positioned logically?
- Do natural resources align with civilizations?

## Review Process

Share the elements of your world you'd like me to review. This could include:
- Your foundation document
- Taxonomies and classification systems
- Specific entries or detailed elements
- Any areas where you sense potential problems

I'll help identify:
1. Inconsistencies or contradictions
2. Areas that need more development
3. Opportunities to strengthen connections
4. Suggestions for resolving issues

What aspects of your world would you like to review for consistency?"""
                )
            )
        ]
    )


def get_entry_revision_prompt() -> types.GetPromptResult:
    """Get the prompt for revising and improving existing entries."""
    return types.GetPromptResult(
        description="Revise existing entries",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="""# Revising World Entries

Let's improve and refine existing elements of your world to make them more compelling, consistent, and detailed.

## Types of Revisions

**Expansion and Depth**
- Add missing details or context
- Develop underdeveloped aspects
- Increase complexity and nuance

**Consistency Fixes**
- Resolve contradictions with other elements
- Align with established world rules
- Ensure logical coherence

**Enhancement and Polish**
- Improve clarity and readability
- Strengthen the most interesting aspects
- Add sensory details and atmosphere

**Connection Building**
- Link to other world elements
- Develop relationships and dependencies
- Create interesting tensions or harmonies

## Revision Process

Share the entry or element you'd like to revise. I'll help you:

1. **Identify** areas for improvement
2. **Brainstorm** enhancement options
3. **Develop** specific improvements
4. **Integrate** changes with the broader world
5. **Polish** the final result

You can share:
- A specific entry you want to improve
- Multiple related elements to revise together
- An area where you feel something is missing
- Content that doesn't feel quite right

What would you like to work on improving?"""
                )
            )
        ]
    )


# Workflow prompt handlers mapping
WORKFLOW_PROMPT_HANDLERS = {
    "consistency-review": get_consistency_review_prompt,
    "entry-revision": get_entry_revision_prompt,
}


def handle_workflow_prompt(name: str) -> types.GetPromptResult:
    """Handle workflow and revision prompt requests.
    
    Args:
        name: Prompt name
        
    Returns:
        GetPromptResult for the requested prompt
        
    Raises:
        ValueError: If prompt name is not recognized
    """
    if name not in WORKFLOW_PROMPT_HANDLERS:
        raise ValueError(f"Unknown workflow prompt: {name}")
    
    return WORKFLOW_PROMPT_HANDLERS[name]()