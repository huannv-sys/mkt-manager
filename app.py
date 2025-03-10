from flask import Flask, render_template, jsonify
import os
import git
import sys
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    # Analyze repository structure
    repo_analysis = analyze_repo()
    return render_template('index.html', repo_analysis=repo_analysis)

@app.route('/api/repo-analysis')
def get_repo_analysis():
    return jsonify(analyze_repo())

def analyze_repo():
    """Analyze the repository structure and return key information"""
    result = {
        "name": "mikrotik-msc",
        "description": "MikroTik Manager/Monitor System",
        "analysis_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "components": [],
        "installation": {
            "requirements": [],
            "compatible_os": ["Ubuntu 24.04"],
            "database": "PostgreSQL",
            "services": ["Backend (FastAPI)", "Frontend (React)", "Nginx", "PostgreSQL"]
        }
    }
    
    # Check for repository
    if not os.path.exists("mikrotik-msc"):
        return {
            "error": "Repository not found. Please ensure mikrotik-msc is cloned properly."
        }
    
    # Add key components
    result["components"] = [
        {
            "name": "Backup Manager",
            "file": "mikrotik_backup_manager.py",
            "description": "Manages device configuration backups"
        },
        {
            "name": "CAPsMAN Manager",
            "file": "mikrotik_capsman_manager.py",
            "description": "Manages Controlled Access Point system"
        },
        {
            "name": "Client Monitor",
            "file": "mikrotik_client_monitor.py",
            "description": "Monitors connected clients"
        },
        {
            "name": "Traffic Logger",
            "file": "mikrotik_traffic_logger.py",
            "description": "Logs and analyzes network traffic"
        },
        {
            "name": "Integrated Web Interface",
            "file": "mikrotik_integrated_web.py",
            "description": "Comprehensive web management interface"
        },
        {
            "name": "Network Master Control",
            "directory": "NetworkMasterControl",
            "description": "Core control system for network management"
        }
    ]
    
    # Add requirements
    if os.path.exists("mikrotik-msc/requirements.txt"):
        with open("mikrotik-msc/requirements.txt", "r") as f:
            requirements = f.readlines()
            result["installation"]["requirements"] = [
                req.strip() for req in requirements if req.strip() and not req.startswith("#")
            ]
    
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)