import os
import tempfile
import shutil
from flask import Flask, render_template, request, jsonify
from utils.repo_analyzer import RepoAnalyzer

app = Flask(__name__)

# Repository URL to be analyzed
REPO_URL = "https://github.com/huannv-sys/mikrotik-msc.git"
REPO_NAME = "mikrotik-msc"

# Global variable to store analysis results
analysis_results = None

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_repo():
    """Clone and analyze the repository"""
    global analysis_results
    
    try:
        # Create a temporary directory for the repo
        temp_dir = tempfile.mkdtemp()
        
        # Initialize the repo analyzer
        analyzer = RepoAnalyzer(REPO_URL, temp_dir)
        
        # Clone the repository
        clone_success = analyzer.clone_repo()
        if not clone_success:
            return jsonify({"status": "error", "message": "Failed to clone repository"})
        
        # Analyze the repository
        repo_path = os.path.join(temp_dir, REPO_NAME)
        analysis_results = analyzer.analyze(repo_path)
        
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)
        
        return jsonify({"status": "success", "data": analysis_results})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/report')
def report():
    """Render the report page"""
    if analysis_results is None:
        return jsonify({"status": "error", "message": "No analysis results available. Please analyze the repository first."})
    
    return render_template('report.html', results=analysis_results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
