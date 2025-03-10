import os

def detect_language(file_path):
    """Detect the programming language of a file based on its extension and content
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Detected programming language, or None if unable to detect
    """
    # Get file extension
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()
    
    # Map file extensions to languages
    extension_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.html': 'HTML',
        '.css': 'CSS',
        '.rsc': 'RouterOS Script',
        '.md': 'Markdown',
        '.txt': 'Text',
        '.sh': 'Shell',
        '.bash': 'Shell',
        '.json': 'JSON',
        '.xml': 'XML',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.toml': 'TOML',
        '.ini': 'INI',
        '.cfg': 'Configuration',
        '.conf': 'Configuration'
    }
    
    # Check if extension is in map
    language = extension_map.get(extension)
    
    # If language is not determined by extension, try to detect from content
    if not language and os.path.exists(file_path) and os.path.getsize(file_path) < 1024 * 1024:  # Skip files larger than 1MB
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1024)  # Read first 1KB of the file
                
                # Check for common syntax patterns
                if content.strip().startswith('#!/usr/bin/env python') or 'import ' in content or 'from ' in content and ' import ' in content:
                    language = 'Python'
                elif content.strip().startswith('#!/bin/bash') or content.strip().startswith('#!/bin/sh'):
                    language = 'Shell'
                elif '<!DOCTYPE html>' in content or '<html' in content:
                    language = 'HTML'
                elif 'function ' in content or 'const ' in content or 'let ' in content or 'var ' in content or '=>' in content:
                    language = 'JavaScript'
                elif ':global ' in content or ':local ' in content or '/ip ' in content:
                    language = 'RouterOS Script'
        except:
            # If unable to read file, return unknown
            pass
    
    # If still not determined, use a generic fallback based on extension
    if not language:
        if extension:
            # Use the extension without the dot as a fallback
            language = extension[1:].upper()
        else:
            language = 'Unknown'
            
    return language
