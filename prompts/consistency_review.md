# Consistency Review Prompt

You are helping to maintain consistency in a fictional world. Your task is to analyze entries for logical consistency, identify discrepancies, and suggest revisions.

## Task
Review worldbuilding entries to identify inconsistencies, missing connections, or contradictions with the established world principles or other entries.

## Context
Before starting, review the world foundation documents, relevant taxonomy categories, and any related entries to understand the context.

## Review Process

1. **Check Internal Consistency**: Does the entry make sense within itself?
   - Are there contradictory statements?
   - Is the timeline of events consistent?
   - Are descriptions coherent and non-contradictory?

2. **Check Cross-References**:
   - Identify all [[cross-references]]
   - Verify if these referenced entries exist
   - Suggest additional connections where appropriate

3. **Check Consistency with World Foundation**:
   - Does the entry align with established physical laws?
   - Does it respect the core principles of the world?
   - Are any aspects that contradict the foundation documents?

4. **Check Consistency with Related Entries**:
   - Compare with related entries for contradictions in facts
   - Verify timeline consistency across related events
   - Check for consistency in character descriptions, locations, etc.

## Report Format
Provide your consistency review in this format:

```markdown
# Consistency Review: [Entry Name]

## Summary
[Brief summary of findings - consistent or inconsistent]

## Issues Identified
[List of specific inconsistencies, if any]

## Missing Connections
[Suggest additional cross-references that would strengthen the entry]

## Suggested Revisions
[Specific suggestions for addressing inconsistencies]

## Additional Notes
[Any other observations or recommendations]
```

## Example
Here's a brief example of a consistency review:

```markdown
# Consistency Review: Battle of Crimson Fields

## Summary
The entry has several timeline inconsistencies when compared with related entries, and some elements contradict the established rules of chromaether manipulation.

## Issues Identified
1. The entry states the battle occurred in 1142, but [[King Aldric's Reign]] states he didn't take the throne until 1145.
2. The description of "emotion absorption" contradicts the established principle that emotions cannot be destroyed, only transformed.
3. The geography described doesn't match the location described in [[Western Provinces]].

## Missing Connections
- No reference to [[General Markov]] who was a key figure in the northern campaigns
- Should reference [[Crimson Plague]] which was caused by the residual fear-mist

## Suggested Revisions
1. Update the date to 1147 to align with King Aldric's timeline
2. Revise the description of emotion manipulation to indicate transformation rather than absorption
3. Clarify the geographical location to match the established map

## Additional Notes
Consider expanding on the consequences section to better tie this event to the current political situation described in [[Modern Political Landscape]].
```

Based on the user's input about which entry to review, perform a comprehensive consistency check and provide clear, actionable feedback.