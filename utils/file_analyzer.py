import os
import re
from .language_detector import detect_language

def analyze_file_content(file_path):
    """Analyze the content of a file
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        dict: Analysis results with purpose and functions
    """
    language = detect_language(file_path)
    
    # Default return structure
    result = {
        "purpose": "Unknown purpose",
        "functions": []
    }
    
    # Skip binary files or very large files
    if not os.path.isfile(file_path) or os.path.getsize(file_path) > 1024 * 1024:
        return result
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Determine file purpose
            result["purpose"] = determine_file_purpose(file_path, content, language)
            
            # Extract functions based on language
            if language == "Python":
                result["functions"] = extract_python_functions(content)
            elif language == "JavaScript":
                result["functions"] = extract_javascript_functions(content)
            elif language == "RouterOS Script":
                result["functions"] = extract_routeros_functions(content)
            
    except Exception as e:
        # If there's an error reading the file, return default result
        print(f"Error analyzing {file_path}: {e}")
    
    return result

def determine_file_purpose(file_path, content, language):
    """Determine the purpose of a file
    
    Args:
        file_path (str): Path to the file
        content (str): Content of the file
        language (str): Programming language of the file
        
    Returns:
        str: Purpose of the file
    """
    filename = os.path.basename(file_path)
    
    # Check for common file types
    if filename == "README.md":
        return "Repository documentation and overview"
    elif filename == "requirements.txt":
        return "Python package dependencies"
    elif filename == "setup.py":
        return "Python package installation script"
    elif filename.endswith(".rsc"):
        return "MikroTik RouterOS script for router configuration"
    
    # Look for docstrings or comments at the beginning of the file
    first_lines = content.split("\n")[:20]  # Look at first 20 lines
    
    # Python docstring
    if language == "Python":
        docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if docstring_match:
            docstring = docstring_match.group(1).strip()
            if docstring:
                # Return first sentence or up to 100 chars
                first_sentence = re.split(r'\.(?:\s|$)', docstring)[0].strip()
                return first_sentence[:100] + ("..." if len(first_sentence) > 100 else "")
    
    # Check for comments at the beginning
    comment_starts = {
        "Python": "#",
        "JavaScript": "//",
        "HTML": "<!--",
        "CSS": "/*",
        "RouterOS Script": "#"
    }
    
    comment_char = comment_starts.get(language, "#")
    
    # Look for comments at the top of the file
    comment_lines = []
    for line in first_lines:
        line = line.strip()
        if line.startswith(comment_char):
            # Remove comment character and strip whitespace
            comment_line = line[len(comment_char):].strip()
            if comment_line:
                comment_lines.append(comment_line)
        elif not line:
            # Skip empty lines
            continue
        else:
            # Stop at first non-comment, non-empty line
            break
    
    if comment_lines:
        # Join comment lines and truncate if necessary
        comment_text = " ".join(comment_lines)
        return comment_text[:100] + ("..." if len(comment_text) > 100 else "")
    
    # Fallback: Determine purpose based on file content and name
    if "api" in filename.lower():
        return "API interaction with MikroTik devices"
    elif "config" in filename.lower():
        return "Configuration management"
    elif "util" in filename.lower() or "helper" in filename.lower():
        return "Utility functions and helpers"
    elif "test" in filename.lower():
        return "Test cases and testing utilities"
    elif "interface" in filename.lower() or "ui" in filename.lower():
        return "User interface components"
    elif "model" in filename.lower() or "schema" in filename.lower():
        return "Data models and schemas"
    elif "script" in filename.lower():
        return "Automation scripts"
    
    # Based on language
    language_purposes = {
        "Python": "Python script for automation or API interaction",
        "JavaScript": "Client-side scripting for web interface",
        "HTML": "Web interface template",
        "CSS": "Styling for web interface",
        "RouterOS Script": "MikroTik RouterOS configuration script",
        "Markdown": "Documentation",
        "Shell": "Shell script for system automation"
    }
    
    return language_purposes.get(language, f"{language} code file")

def extract_python_functions(content):
    """Extract functions from Python code
    
    Args:
        content (str): Python code content
        
    Returns:
        list: Extracted functions with name and description
    """
    functions = []
    
    # Regular expression to match Python function definitions
    function_pattern = r'def\s+([a-zA-Z0-9_]+)\s*\((.*?)\):(.*?)(?=\n\S|\Z)'
    
    for match in re.finditer(function_pattern, content, re.DOTALL):
        func_name = match.group(1)
        parameters = match.group(2)
        body = match.group(3).strip()
        
        # Skip private methods (starting with underscore)
        if func_name.startswith('_') and not func_name.startswith('__'):
            continue
        
        # Extract docstring if present
        docstring_match = re.search(r'"""(.*?)"""', body, re.DOTALL)
        description = ""
        
        if docstring_match:
            docstring = docstring_match.group(1).strip()
            # Get first sentence or first 100 chars
            first_sentence = re.split(r'\.(?:\s|$)', docstring)[0].strip()
            description = first_sentence[:100] + ("..." if len(first_sentence) > 100 else "")
        else:
            # If no docstring, use first non-empty line of function body
            for line in body.split("\n"):
                line = line.strip()
                if line and not line.startswith('#'):
                    description = f"Implementation: {line[:50]}..."
                    break
            
            if not description:
                description = f"Function with parameters: {parameters}"
        
        functions.append({
            "name": func_name,
            "description": description
        })
    
    return functions

def extract_javascript_functions(content):
    """Extract functions from JavaScript code
    
    Args:
        content (str): JavaScript code content
        
    Returns:
        list: Extracted functions with name and description
    """
    functions = []
    
    # Regular expressions to match different JavaScript function styles
    patterns = [
        # Regular function: function name(params) { ... }
        r'function\s+([a-zA-Z0-9_$]+)\s*\((.*?)\)\s*{(.*?)(?=\n\}|\Z)',
        
        # Arrow function with name: const name = (params) => { ... }
        r'(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*(?:\(.*?\)|[a-zA-Z0-9_$]+)\s*=>\s*{(.*?)(?=\n\}|\Z)',
        
        # Method in object or class: name(params) { ... }
        r'([a-zA-Z0-9_$]+)\s*\((.*?)\)\s*{(.*?)(?=\n\s*\}|\Z)'
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, content, re.DOTALL):
            if len(match.groups()) >= 2:
                func_name = match.group(1)
                
                # Skip functions starting with underscore (private by convention)
                if func_name.startswith('_'):
                    continue
                
                # Get function body (might be in different group positions)
                body = match.group(len(match.groups()))
                
                # Look for comments before function
                func_pos = match.start()
                before_func = content[:func_pos].strip()
                
                comment_match = re.search(r'\/\*\*(.*?)\*\/', before_func, re.DOTALL)
                if comment_match:
                    comment = comment_match.group(1).strip()
                    description = ' '.join([line.strip().lstrip('*') for line in comment.split('\n')])
                    description = description[:100] + ("..." if len(description) > 100 else "")
                else:
                    # Look for single-line comments
                    lines = before_func.split('\n')
                    comment_lines = []
                    
                    for line in reversed(lines):
                        line = line.strip()
                        if line.startswith('//'):
                            comment_lines.insert(0, line[2:].strip())
                        elif line:
                            break
                    
                    if comment_lines:
                        description = ' '.join(comment_lines)
                        description = description[:100] + ("..." if len(description) > 100 else "")
                    else:
                        # If no comments, use first line of function body
                        body_lines = [line.strip() for line in body.split('\n') if line.strip()]
                        if body_lines:
                            description = f"Implementation: {body_lines[0][:50]}..."
                        else:
                            description = "JavaScript function"
                
                functions.append({
                    "name": func_name,
                    "description": description
                })
    
    return functions

def extract_routeros_functions(content):
    """Extract functions or sections from RouterOS scripts
    
    Args:
        content (str): RouterOS script content
        
    Returns:
        list: Extracted sections with name and description
    """
    functions = []
    
    # Look for labeled sections or loops in RouterOS scripts
    section_patterns = [
        # :label=name
        r':label=([a-zA-Z0-9_.-]+)',
        
        # foreach pattern
        r'foreach\s+([^\s]+)\s+in=([^\s]+)\s+do=({.*?})'
    ]
    
    for pattern in section_patterns:
        for match in re.finditer(pattern, content, re.DOTALL):
            section_name = match.group(1)
            
            # Find comment before this section
            section_pos = match.start()
            content_before = content[:section_pos].strip()
            lines_before = content_before.split('\n')
            
            comment_lines = []
            for line in reversed(lines_before):
                line = line.strip()
                if line.startswith('#'):
                    comment_lines.insert(0, line[1:].strip())
                elif line:
                    break
            
            if comment_lines:
                description = ' '.join(comment_lines)
                description = description[:100] + ("..." if len(description) > 100 else "")
            else:
                # Look at the line containing the section
                section_line = match.group(0)
                description = f"RouterOS script section: {section_line[:50]}..."
            
            functions.append({
                "name": section_name,
                "description": description
            })
    
    # Look for function-like constructs (do={...})
    do_pattern = r'do=({.*?})'
    position = 0
    section_count = 1
    
    for match in re.finditer(do_pattern, content, re.DOTALL):
        # Create a name based on the position in the file
        section_name = f"Script Section {section_count}"
        section_count += 1
        
        # Extract the content of the do block
        do_block = match.group(1)
        description = f"RouterOS script block: {do_block[:50]}..."
        
        functions.append({
            "name": section_name,
            "description": description
        })
    
    return functions
