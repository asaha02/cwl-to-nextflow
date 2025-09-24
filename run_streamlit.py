#!/usr/bin/env python3
"""
Streamlit App Launcher

This script launches the CWL to Nextflow Migration Toolkit Streamlit app.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} found")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
        print("✅ Streamlit installed")
    
    try:
        import yaml
        print("✅ PyYAML found")
    except ImportError:
        print("❌ PyYAML not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
        print("✅ PyYAML installed")
    
    try:
        import jinja2
        print("✅ Jinja2 found")
    except ImportError:
        print("❌ Jinja2 not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "jinja2"])
        print("✅ Jinja2 installed")

def main():
    """Main function to launch Streamlit app."""
    print("🚀 Starting CWL to Nextflow Migration Toolkit Streamlit App")
    print("=" * 60)
    
    # Check dependencies
    print("Checking dependencies...")
    check_dependencies()
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    app_file = script_dir / "streamlit_app.py"
    
    if not app_file.exists():
        print(f"❌ Streamlit app file not found: {app_file}")
        sys.exit(1)
    
    print(f"✅ Found app file: {app_file}")
    
    # Launch Streamlit
    print("\n🌐 Launching Streamlit app...")
    print("The app will open in your default web browser.")
    print("If it doesn't open automatically, go to: http://localhost:8501")
    print("\nPress Ctrl+C to stop the app.")
    print("=" * 60)
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(app_file),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped by user")
    except Exception as e:
        print(f"❌ Error launching Streamlit app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
