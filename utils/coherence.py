#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Coherence utilities for the Vibe Worldbuilding MCP.
These functions help analyze and maintain logical consistency across entries.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import json

def extract_references(content: str) -> List[str]:
    """Extract all wiki-style references from content."""
    return re.findall(r'\[\[(.*?)\]\]', content)

def find_missing_references(world_dir: Path) -> Dict[str, List[str]]:
    """
    Find all references that don't have corresponding entries.
    
    Returns:
        Dict mapping entry paths to lists of missing references
    """
    entries_dir = world_dir / "entries"
    all_entries = set()
    references_by_file = {}
    missing_references = {}
    
    # First pass: collect all entries
    for entry_type in ["people", "places", "events", "artifacts", "concepts"]:
        type_dir = entries_dir / entry_type
        if not type_dir.exists():
            continue
            
        for entry_file in type_dir.glob("*.md"):
            all_entries.add(entry_file.stem)
    
    # Second pass: check references
    for entry_type in ["people", "places", "events", "artifacts", "concepts"]:
        type_dir = entries_dir / entry_type
        if not type_dir.exists():
            continue
            
        for entry_file in type_dir.glob("*.md"):
            with open(entry_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            references = extract_references(content)
            file_path = str(entry_file.relative_to(world_dir))
            references_by_file[file_path] = references
            
            # Check for missing references
            missing = [ref for ref in references if ref not in all_entries]
            if missing:
                missing_references[file_path] = missing
    
    return missing_references

def find_orphaned_entries(world_dir: Path) -> List[str]:
    """
    Find entries that aren't referenced by any other entry.
    
    Returns:
        List of orphaned entry paths
    """
    entries_dir = world_dir / "entries"
    all_entries = {}
    all_references = set()
    
    # Collect all entries and their paths
    for entry_type in ["people", "places", "events", "artifacts", "concepts"]:
        type_dir = entries_dir / entry_type
        if not type_dir.exists():
            continue
            
        for entry_file in type_dir.glob("*.md"):
            entry_name = entry_file.stem
            file_path = str(entry_file.relative_to(world_dir))
            all_entries[entry_name] = file_path
    
    # Collect all references
    for entry_type in ["people", "places", "events", "artifacts", "concepts"]:
        type_dir = entries_dir / entry_type
        if not type_dir.exists():
            continue
            
        for entry_file in type_dir.glob("*.md"):
            with open(entry_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            references = extract_references(content)
            all_references.update(references)
    
    # Find entries not referenced by any other
    orphaned = []
    for entry_name, file_path in all_entries.items():
        if entry_name not in all_references:
            orphaned.append(file_path)
    
    return orphaned

def check_timeline_consistency(world_dir: Path) -> List[str]:
    """
    Check for timeline inconsistencies in event entries.
    
    Returns:
        List of inconsistency descriptions
    """
    events_dir = world_dir / "entries" / "events"
    if not events_dir.exists():
        return []
    
    inconsistencies = []
    event_years = {}
    
    # Extract years from event entries
    for event_file in events_dir.glob("*.md"):
        event_name = event_file.stem.replace("_", " ")
        with open(event_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to extract a year from the content
        year_match = re.search(r'(?:year|date)[:\s]+(\d+)', content, re.IGNORECASE)
        if year_match:
            year = int(year_match.group(1))
            event_years[event_name] = year
        
        # Check for references to other events
        references = extract_references(content)
        for ref in references:
            if ref in event_years:
                # Check if there's a "before" or "after" relationship mentioned
                before_match = re.search(rf'(?:before|prior to|earlier than)[^.]*\[\[{ref}\]\]', content, re.IGNORECASE)
                after_match = re.search(rf'(?:after|following|later than)[^.]*\[\[{ref}\]\]', content, re.IGNORECASE)
                
                if before_match and year >= event_years[ref]:
                    inconsistencies.append(f"Timeline inconsistency: {event_name} ({year}) is described as before {ref} ({event_years[ref]})")
                
                if after_match and year <= event_years[ref]:
                    inconsistencies.append(f"Timeline inconsistency: {event_name} ({year}) is described as after {ref} ({event_years[ref]})")
    
    return inconsistencies

def suggest_connections(world_dir: Path, entry_path: str, max_suggestions: int = 5) -> List[str]:
    """
    Suggest potential connections for an entry based on content similarity.
    
    Args:
        world_dir: Path to the world directory
        entry_path: Path to the entry (relative to world_dir)
        max_suggestions: Maximum number of suggestions to return
        
    Returns:
        List of suggested entry names for connection
    """
    full_entry_path = world_dir / entry_path
    if not full_entry_path.exists():
        return []
    
    # Read the target entry
    with open(full_entry_path, 'r', encoding='utf-8') as f:
        target_content = f.read()
    
    # Extract meaningful keywords
    # This is a very simple implementation - a more sophisticated approach would use NLP
    keywords = set()
    for match in re.finditer(r'\b[A-Z][a-z]{3,}\b', target_content):
        keywords.add(match.group(0).lower())
    
    # Add any specific terms from section titles
    section_titles = re.findall(r'## (.+)', target_content)
    for title in section_titles:
        for word in title.split():
            if len(word) > 3:
                keywords.add(word.lower())
    
    # Score other entries based on keyword matches
    entries_dir = world_dir / "entries"
    scores = {}
    
    for entry_type in ["people", "places", "events", "artifacts", "concepts"]:
        type_dir = entries_dir / entry_type
        if not type_dir.exists():
            continue
            
        for entry_file in type_dir.glob("*.md"):
            # Skip the target entry
            if str(entry_file.relative_to(world_dir)) == entry_path:
                continue
                
            entry_name = entry_file.stem
            with open(entry_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count keyword matches
            score = 0
            for keyword in keywords:
                score += len(re.findall(rf'\b{re.escape(keyword)}\b', content.lower()))
            
            if score > 0: