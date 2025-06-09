"""Content parsing and analysis utilities.

This module provides utilities for parsing markdown content, extracting
metadata, and analyzing text for worldbuilding purposes.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re


def extract_markdown_title(content: str) -> Optional[str]:
    """Extract the main title from markdown content.
    
    Args:
        content: Markdown content
        
    Returns:
        Title text, or None if no title found
    """
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return None


def extract_description_lines(content: str, max_lines: int = 3) -> List[str]:
    """Extract description lines from markdown content.
    
    Args:
        content: Markdown content
        max_lines: Maximum number of description lines to extract
        
    Returns:
        List of description lines
    """
    lines = content.split('\n')
    description_lines = []
    
    for line in lines:
        stripped = line.strip()
        # Skip empty lines, headers, and frontmatter
        if (stripped and 
            not stripped.startswith('#') and 
            not stripped.startswith('---') and
            not stripped.startswith('*')):
            description_lines.append(stripped)
            if len(description_lines) >= max_lines:
                break
    
    return description_lines


def extract_frontmatter(content: str) -> Tuple[Dict[str, str], str]:
    """Extract YAML frontmatter from markdown content.
    
    Args:
        content: Markdown content
        
    Returns:
        Tuple of (frontmatter_dict, content_without_frontmatter)
    """
    lines = content.split('\n')
    frontmatter = {}
    content_start = 0
    
    if lines and lines[0].strip() == '---':
        # Look for closing frontmatter delimiter
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                content_start = i + 1
                break
            elif ':' in line:
                # Parse simple key: value pairs
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip().strip('"\'')
    
    remaining_content = '\n'.join(lines[content_start:])
    return frontmatter, remaining_content


def extract_taxonomy_description(content: str) -> Optional[str]:
    """Extract the description section from a taxonomy overview.
    
    Args:
        content: Taxonomy overview content
        
    Returns:
        Description text, or None if not found
    """
    lines = content.split('\n')
    in_description = False
    description_lines = []
    
    for line in lines:
        if line.strip() == "## Description":
            in_description = True
            continue
        elif line.startswith("## ") and in_description:
            break
        elif in_description and line.strip():
            description_lines.append(line.strip())
    
    return " ".join(description_lines) if description_lines else None


def find_potential_references(content: str) -> List[str]:
    """Find potential entity references in content.
    
    This is a simple heuristic that looks for capitalized words/phrases
    that might be proper nouns or entity names.
    
    Args:
        content: Text content to analyze
        
    Returns:
        List of potential entity references
    """
    # Remove markdown formatting
    text = re.sub(r'[#*_`]', '', content)
    
    # Find capitalized words/phrases
    # Look for sequences of capitalized words
    potential_refs = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    
    # Filter out common words and short single words
    common_words = {
        'The', 'This', 'That', 'These', 'Those', 'And', 'But', 'Or', 'For',
        'In', 'On', 'At', 'To', 'From', 'With', 'By', 'As', 'Of', 'About',
        'Through', 'During', 'Before', 'After', 'Above', 'Below', 'Up', 'Down',
        'Out', 'Off', 'Over', 'Under', 'Again', 'Further', 'Then', 'Once',
        'Here', 'There', 'When', 'Where', 'Why', 'How', 'All', 'Any', 'Both',
        'Each', 'Few', 'More', 'Most', 'Other', 'Some', 'Such', 'No', 'Nor',
        'Not', 'Only', 'Own', 'Same', 'So', 'Than', 'Too', 'Very', 'Can',
        'Will', 'Just', 'Should', 'Now', 'Entry', 'Overview', 'Description',
        'History', 'Context', 'Relationships', 'Impact', 'Required', 'Optional'
    }
    
    filtered_refs = []
    for ref in potential_refs:
        # Skip single short words and common words
        if len(ref) > 3 and ref not in common_words:
            # Skip if it's just a single common word
            words = ref.split()
            if len(words) == 1 and ref in common_words:
                continue
            filtered_refs.append(ref)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_refs = []
    for ref in filtered_refs:
        if ref not in seen:
            seen.add(ref)
            unique_refs.append(ref)
    
    return unique_refs


def analyze_content_complexity(content: str) -> Dict[str, int]:
    """Analyze the complexity and structure of content.
    
    Args:
        content: Text content to analyze
        
    Returns:
        Dictionary with complexity metrics
    """
    lines = content.split('\n')
    
    metrics = {
        'word_count': len(content.split()),
        'line_count': len([line for line in lines if line.strip()]),
        'paragraph_count': len([line for line in lines if line.strip() and not line.startswith('#')]),
        'header_count': len([line for line in lines if line.startswith('#')]),
        'potential_references': len(find_potential_references(content))
    }
    
    return metrics


def extract_section_content(content: str, section_title: str) -> Optional[str]:
    """Extract content from a specific markdown section.
    
    Args:
        content: Markdown content
        section_title: Title of the section to extract (without #)
        
    Returns:
        Section content, or None if section not found
    """
    lines = content.split('\n')
    in_section = False
    section_lines = []
    
    # Look for the section header (any level)
    section_pattern = re.compile(r'^#+\s*' + re.escape(section_title) + r'\s*$', re.IGNORECASE)
    
    for line in lines:
        if section_pattern.match(line):
            in_section = True
            continue
        elif line.startswith('#') and in_section:
            # Hit another section, stop collecting
            break
        elif in_section and line.strip():
            section_lines.append(line)
    
    return '\n'.join(section_lines).strip() if section_lines else None


def generate_content_summary(content: str, max_length: int = 150) -> str:
    """Generate a brief summary of content.
    
    Args:
        content: Text content to summarize
        max_length: Maximum length of summary
        
    Returns:
        Brief summary text
    """
    # Remove markdown formatting
    text = re.sub(r'[#*_`]', '', content)
    
    # Get first few sentences
    sentences = re.split(r'[.!?]+', text)
    summary = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and len(summary + sentence) < max_length:
            if summary:
                summary += ". "
            summary += sentence
        else:
            break
    
    if len(summary) >= max_length:
        summary = summary[:max_length-3] + "..."
    
    return summary


def add_frontmatter_to_content(content: str, frontmatter: Dict[str, str]) -> str:
    """Add YAML frontmatter to markdown content.
    
    Args:
        content: Existing markdown content
        frontmatter: Dictionary of frontmatter key-value pairs
        
    Returns:
        Content with frontmatter prepended
    """
    # Check if content already has frontmatter
    existing_frontmatter, main_content = extract_frontmatter(content)
    
    # Merge frontmatter, with new values taking precedence
    merged_frontmatter = {**existing_frontmatter, **frontmatter}
    
    # Build frontmatter block
    frontmatter_lines = ["---"]
    for key, value in merged_frontmatter.items():
        # Properly escape YAML values
        if isinstance(value, str):
            # Check if value needs quoting (contains special YAML characters)
            needs_quoting = any(char in value for char in ['"', "'", ':', '\n', '\r', '\t', '#', '&', '*', '!', '|', '>', '%', '@', '`', '[', ']', '{', '}'])
            
            if needs_quoting or value.strip() != value:  # Also quote if has leading/trailing whitespace
                # Use double quotes and escape internal double quotes
                escaped_value = value.replace('\\', '\\\\').replace('"', '\\"')
                frontmatter_lines.append(f'{key}: "{escaped_value}"')
            else:
                frontmatter_lines.append(f"{key}: {value}")
        else:
            frontmatter_lines.append(f"{key}: {value}")
    frontmatter_lines.append("---")
    
    # Combine frontmatter with content
    return "\n".join(frontmatter_lines) + "\n\n" + main_content


def extract_description_from_content(content: str, max_words: int = 100) -> str:
    """Extract a description from content for frontmatter.
    
    Args:
        content: Markdown content
        max_words: Maximum words in description
        
    Returns:
        Concise description suitable for frontmatter
    """
    # Remove existing frontmatter
    _, main_content = extract_frontmatter(content)
    
    # Look for overview section first
    overview = extract_section_content(main_content, "Overview")
    if overview:
        text = overview
    else:
        # Use content after the title
        lines = main_content.split('\n')
        content_lines = []
        
        for line in lines[1:]:  # Skip title
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                content_lines.append(stripped)
            elif content_lines:  # Stop at next header if we have content
                break
        
        text = " ".join(content_lines)
    
    # Clean up markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'`(.*?)`', r'\1', text)        # Code
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Links
    text = re.sub(r'#{1,6}\s*', '', text)         # Headers
    
    # Get first N words
    words = text.split()
    if len(words) > max_words:
        words = words[:max_words]
        description = " ".join(words) + "..."
    else:
        description = " ".join(words)
    
    return description.strip()


def validate_markdown_structure(content: str) -> Dict[str, bool]:
    """Validate the structure of markdown content.
    
    Args:
        content: Markdown content to validate
        
    Returns:
        Dictionary with validation results
    """
    lines = content.split('\n')
    
    validation = {
        'has_title': any(line.startswith('# ') for line in lines),
        'has_content': len([line for line in lines if line.strip() and not line.startswith('#')]) > 0,
        'proper_frontmatter': False,
        'balanced_formatting': True  # Could check for balanced markdown formatting
    }
    
    # Check for proper frontmatter structure
    if lines and lines[0].strip() == '---':
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                validation['proper_frontmatter'] = True
                break
    
    return validation