#!/usr/bin/env python3
"""
Landscaping Management System - Main Entry Point

This script starts the main application.
"""
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main entry point for the application."""
    print("Starting Landscaping Management System...")
    print(f"Project root: {project_root}")
    
    # Check if database exists, if not initialize it
    db_path = project_root / "landscaping.db"
    if not db_path.exists():
        print("Database not found, initializing...")
        from database import init_db
        init_db()
        print("Database initialized successfully!")
    
    # Start the Streamlit app
    import subprocess
    import webbrowser
    import time
    
    # Open the browser after a short delay
    def open_browser():
        time.sleep(2)  # Wait for Streamlit to start
        webbrowser.open("http://localhost:8501")
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.start()
    
    # Run Streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port=8501"])

if __name__ == "__main__":
    main()