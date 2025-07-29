#!/usr/bin/env python3
"""
Quick start script for Rush Gaming CI Web Interface
"""

import os
import sys
from pathlib import Path

def main():
    print("🚀 Starting Rush Gaming CI Web Interface...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("web_app.py").exists():
        print("❌ Error: web_app.py not found. Please run this from the project root directory.")
        sys.exit(1)
    
    # Check if templates directory exists
    if not Path("templates").exists():
        print("❌ Error: templates directory not found. Please ensure all files are present.")
        sys.exit(1)
    
    # Set environment variables for development
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')
    
    try:
        # Import and run the web app
        from web_app import app
        
        print("✅ Web interface loaded successfully!")
        print("📊 Dashboard: http://localhost:5000")
        print("📋 Briefs: http://localhost:5000/briefs")
        print("⚙️  Config: http://localhost:5000/config")
        print("=" * 50)
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Run the app
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 