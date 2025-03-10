import os
import subprocess
import datetime
import shutil
from collections import defaultdict
import glob
from .language_detector import detect_language
from .file_analyzer import analyze_file_content

class RepoAnalyzer:
    """Class to analyze a GitHub repository"""
    
    def __init__(self, repo_url, temp_dir):
        """Initialize the analyzer with repository URL and temp directory
        
        Args:
            repo_url (str): URL of the GitHub repository
            temp_dir (str): Temporary directory to clone the repo
        """
        self.repo_url = repo_url
        self.temp_dir = temp_dir
        self.repo_name = repo_url.split("/")[-1].replace(".git", "")
    
    def clone_repo(self):
        """Clone the repository to the temporary directory
        
        Returns:
            bool: True if cloning was successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "clone", self.repo_url],
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    
    def analyze(self, repo_path):
        """Analyze the repository and return results
        
        Args:
            repo_path (str): Path to the cloned repository
            
        Returns:
            dict: Analysis results
        """
        results = {
            "repo_info": self._get_repo_info(),
            "stats": self._calculate_stats(repo_path),
            "directory_structure": self._get_directory_structure(repo_path),
            "languages": self._detect_languages(repo_path),
            "key_files": self._analyze_key_files(repo_path),
            "key_components": self._identify_key_components(repo_path),
            "dependencies": self._analyze_dependencies(repo_path),
            "implementation_roadmap": self._generate_implementation_roadmap(),
            "analysis_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "conclusion": self._generate_conclusion()
        }
        
        return results
    
    def _get_repo_info(self):
        """Get basic repository information
        
        Returns:
            dict: Repository information
        """
        # In a real-world scenario, we might query GitHub API for more info
        return {
            "name": self.repo_name,
            "url": self.repo_url,
            "purpose": "A MikroTik router management and scripting collection tool"
        }
    
    def _calculate_stats(self, repo_path):
        """Calculate statistics for the repository
        
        Args:
            repo_path (str): Path to the cloned repository
            
        Returns:
            dict: Repository statistics
        """
        total_files = 0
        total_size = 0
        
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
                
            total_files += len(files)
            
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
        
        # Format total size
        if total_size < 1024:
            size_formatted = f"{total_size} bytes"
        elif total_size < 1024 * 1024:
            size_formatted = f"{total_size / 1024:.1f} KB"
        else:
            size_formatted = f"{total_size / (1024 * 1024):.1f} MB"
        
        return {
            "total_files": total_files,
            "total_size": total_size,
            "total_size_formatted": size_formatted
        }
    
    def _get_directory_structure(self, repo_path):
        """Generate a text representation of the directory structure
        
        Args:
            repo_path (str): Path to the cloned repository
            
        Returns:
            str: Text representation of the directory structure
        """
        result = []
        
        def _generate_tree(path, prefix=""):
            items = sorted(os.listdir(path))
            
            # Skip .git directory
            if '.git' in items:
                items.remove('.git')
            
            for i, item in enumerate(items):
                item_path = os.path.join(path, item)
                is_last = i == len(items) - 1
                
                # Add the item to the result
                if is_last:
                    result.append(f"{prefix}└── {item}")
                    new_prefix = f"{prefix}    "
                else:
                    result.append(f"{prefix}├── {item}")
                    new_prefix = f"{prefix}│   "
                
                # Recursively process directory
                if os.path.isdir(item_path):
                    _generate_tree(item_path, new_prefix)
        
        # Start generating the tree
        result.append(self.repo_name)
        _generate_tree(repo_path, "")
        
        return "\n".join(result)
    
    def _detect_languages(self, repo_path):
        """Detect programming languages used in the repository
        
        Args:
            repo_path (str): Path to the cloned repository
            
        Returns:
            list: Languages used in the repository
        """
        language_counts = defaultdict(int)
        total_files = 0
        
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
                
            for file in files:
                file_path = os.path.join(root, file)
                language = detect_language(file_path)
                
                if language:
                    language_counts[language] += 1
                    total_files += 1
        
        # Convert to list and calculate percentages
        languages = []
        for lang, count in sorted(language_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_files) * 100 if total_files > 0 else 0
            languages.append({
                "name": lang,
                "files": count,
                "percentage": round(percentage, 1)
            })
        
        return languages
    
    def _analyze_key_files(self, repo_path):
        """Analyze key files in the repository
        
        Args:
            repo_path (str): Path to the cloned repository
            
        Returns:
            list: Key files analysis
        """
        key_files = []
        
        # Define patterns to identify key files
        patterns = [
            os.path.join(repo_path, "*.py"),
            os.path.join(repo_path, "**", "*.py"),
            os.path.join(repo_path, "*.md"),
            os.path.join(repo_path, "*.txt"),
            os.path.join(repo_path, "*.rsc"),
            os.path.join(repo_path, "*.html"),
            os.path.join(repo_path, "*.js"),
            os.path.join(repo_path, "*.css")
        ]
        
        # Find all files matching patterns
        all_files = []
        for pattern in patterns:
            all_files.extend(glob.glob(pattern, recursive=True))
        
        # Remove duplicates
        all_files = list(set(all_files))
        
        # Analyze most important files
        for file_path in all_files:
            # Skip large files
            if os.path.getsize(file_path) > 1024 * 1024:  # Skip files larger than 1MB
                continue
                
            relative_path = os.path.relpath(file_path, repo_path)
            
            # Skip files in .git directory
            if relative_path.startswith('.git'):
                continue
            
            # Analyze file content
            analysis = analyze_file_content(file_path)
            
            # Format file size
            size = os.path.getsize(file_path)
            if size < 1024:
                size_formatted = f"{size} bytes"
            elif size < 1024 * 1024:
                size_formatted = f"{size / 1024:.1f} KB"
            else:
                size_formatted = f"{size / (1024 * 1024):.1f} MB"
            
            key_files.append({
                "path": relative_path,
                "language": detect_language(file_path),
                "size_formatted": size_formatted,
                "purpose": analysis["purpose"],
                "functions": analysis["functions"]
            })
        
        # Sort by importance and limit to top files
        key_files = sorted(key_files, key=lambda x: len(x["functions"]), reverse=True)[:10]
        
        return key_files
    
    def _identify_key_components(self, repo_path):
        """Identify key components in the repository
        
        Args:
            repo_path (str): Path to the cloned repository
            
        Returns:
            list: Key components
        """
        # For a more accurate analysis in a real-world scenario,
        # we would need to understand the repo better
        key_components = []
        
        # Check for core components based on common directories and files
        for component_name, patterns in [
            ("Core Scripts", ["*.rsc", "scripts/*.rsc"]),
            ("Documentation", ["*.md", "docs/*.md", "README.md"]),
            ("Configuration", ["*.conf", "config/*.conf", "*.cfg"]),
            ("Web Interface", ["*.html", "*.js", "*.css"]),
            ("MikroTik API", ["api*.py", "*api*.py"]),
            ("Utilities", ["utils/*.py", "helpers/*.py"])
        ]:
            component_files = []
            
            for pattern in patterns:
                # Transform pattern into absolute path
                abs_pattern = os.path.join(repo_path, pattern)
                # Find matching files
                matching_files = glob.glob(abs_pattern, recursive=True)
                # Convert to relative paths
                rel_files = [os.path.relpath(f, repo_path) for f in matching_files]
                # Add to component files
                component_files.extend(rel_files)
            
            # Remove duplicates
            component_files = list(set(component_files))
            
            # Add component if files were found
            if component_files:
                key_components.append({
                    "name": component_name,
                    "files": component_files,
                    "description": self._generate_component_description(component_name, component_files)
                })
        
        return key_components
    
    def _generate_component_description(self, component_name, files):
        """Generate a description for a component
        
        Args:
            component_name (str): Name of the component
            files (list): Files in the component
            
        Returns:
            str: Description of the component
        """
        descriptions = {
            "Core Scripts": "Contains MikroTik RouterOS script files (.rsc) that provide core functionality for router management.",
            "Documentation": "Contains documentation files explaining the usage and features of the repository.",
            "Configuration": "Contains configuration files for setting up and customizing the system.",
            "Web Interface": "Provides a web-based interface for interacting with MikroTik routers.",
            "MikroTik API": "Implements API functionality for communicating with MikroTik routers programmatically.",
            "Utilities": "Helper functions and utility scripts that support the main functionality."
        }
        
        return descriptions.get(component_name, "A collection of files related to MikroTik router management.")
    
    def _analyze_dependencies(self, repo_path):
        """Analyze dependencies used in the repository
        
        Args:
            repo_path (str): Path to the cloned repository
            
        Returns:
            list: Dependencies
        """
        dependencies = []
        
        # Check for Python requirements.txt
        req_path = os.path.join(repo_path, "requirements.txt")
        if os.path.exists(req_path):
            with open(req_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        dep_name = line.split("==")[0] if "==" in line else line
                        dependencies.append({
                            "name": dep_name,
                            "type": "Python Package",
                            "purpose": self._get_dependency_purpose(dep_name),
                            "required": True
                        })
        
        # Check Python files for import statements
        python_imports = set()
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
                
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Simple parsing for imports
                        import_lines = [line.strip() for line in content.split("\n") 
                                       if line.strip().startswith(("import ", "from "))]
                        
                        for line in import_lines:
                            if line.startswith("import "):
                                module = line[7:].split(" as ")[0].split(",")[0].strip()
                                python_imports.add(module)
                            elif line.startswith("from "):
                                module = line[5:].split(" import")[0].strip()
                                python_imports.add(module.split(".")[0])
        
        # Filter out standard library modules
        std_lib_modules = [
            "os", "sys", "time", "datetime", "re", "math", "random", 
            "json", "csv", "pickle", "collections", "subprocess", "shutil",
            "glob", "tempfile", "traceback", "itertools", "functools"
        ]
        
        for module in python_imports:
            if module not in std_lib_modules and not any(d["name"] == module for d in dependencies):
                dependencies.append({
                    "name": module,
                    "type": "Python Package",
                    "purpose": self._get_dependency_purpose(module),
                    "required": True
                })
        
        return dependencies
    
    def _get_dependency_purpose(self, dep_name):
        """Get the purpose of a dependency
        
        Args:
            dep_name (str): Name of the dependency
            
        Returns:
            str: Purpose of the dependency
        """
        purposes = {
            "flask": "Web framework for building the interface",
            "requests": "HTTP library for making API requests",
            "paramiko": "SSH client for connecting to MikroTik devices",
            "librouteros": "Python API implementation for MikroTik RouterOS",
            "pyyaml": "YAML parser for configuration files",
            "jinja2": "Templating engine for generating scripts",
            "netmiko": "Multi-vendor SSH client for network devices",
            "pysnmp": "SNMP library for monitoring MikroTik devices",
            "click": "Command-line interface creation kit",
            "cryptography": "Cryptography library for secure communications",
            "schedule": "Job scheduling for Python",
            "pandas": "Data analysis and manipulation library",
            "matplotlib": "Plotting library for visualization",
            "pytest": "Testing framework",
            "sqlalchemy": "SQL toolkit and ORM",
            "django": "Web framework",
            "pymongo": "MongoDB client"
        }
        
        return purposes.get(dep_name, f"Support library for {dep_name.replace('_', ' ')} functionality")
    
    def _generate_implementation_roadmap(self):
        """Generate an implementation roadmap for using the repository
        
        Returns:
            list: Implementation roadmap steps
        """
        return [
            {
                "title": "Setup Environment",
                "description": "Clone the repository and install necessary dependencies. Ensure Python and required packages are installed."
            },
            {
                "title": "Configure MikroTik Devices",
                "description": "Ensure your MikroTik devices are accessible via API or SSH. Configure IP addresses and credentials."
            },
            {
                "title": "Review Documentation",
                "description": "Read the repository documentation to understand available scripts and features."
            },
            {
                "title": "Customize Configuration",
                "description": "Modify configuration files to match your network environment and requirements."
            },
            {
                "title": "Test Basic Scripts",
                "description": "Run basic scripts to ensure connectivity and functionality with your MikroTik devices."
            },
            {
                "title": "Implement Monitoring",
                "description": "Set up monitoring scripts to track router performance and status."
            },
            {
                "title": "Schedule Automation",
                "description": "Configure automation scripts to run on schedule for maintenance tasks."
            },
            {
                "title": "Extend Functionality",
                "description": "Develop additional scripts or modify existing ones to meet specific requirements."
            }
        ]
    
    def _generate_conclusion(self):
        """Generate a conclusion about the repository
        
        Returns:
            str: Conclusion
        """
        return """
        The mikrotik-msc repository appears to be a collection of tools, scripts, and utilities for managing and automating MikroTik router configurations. 
        It likely provides both command-line and potentially web-based interfaces for interacting with MikroTik devices through their API.
        
        The repository contains various RouterOS scripts (.rsc files) that can be uploaded directly to MikroTik devices, as well as Python utilities
        for programmatic interaction with routers. This combination allows for both direct configuration via scripts and remote management via API.
        
        For organizations with MikroTik infrastructure, this repository could serve as a valuable tool for standardizing configurations, 
        automating routine tasks, and implementing consistent network policies across multiple devices.
        
        To begin using this repository, users should follow the implementation roadmap, starting with setting up the environment
        and configuring their MikroTik devices for remote access.
        """
