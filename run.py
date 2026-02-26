"""
Veryfyn Tracking System - Runner Script

Simple entry point to launch the Streamlit application.

Usage:
    python run.py
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit application."""
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tracking_app", "app.py")
    
    print("Starting Veryfyn Tracking System...")
    print(f"Running: streamlit run {app_path}")
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

if __name__ == "__main__":
    main()