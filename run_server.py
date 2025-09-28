#!/usr/bin/env python3
"""
Backend Server Runner
This script ensures the server runs from the correct directory with proper configuration.
"""
import os
import sys
import uvicorn
from pathlib import Path

def main():
    # Ensure we're in the correct directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Add current directory to Python path
    sys.path.insert(0, str(backend_dir))
    
    print("🚀 Starting AI Stock Backend Server...")
    print(f"📁 Working Directory: {os.getcwd()}")
    print(f"🌐 Server URL: http://127.0.0.1:8000")
    print(f"📊 Health Check: http://127.0.0.1:8000/health")
    print("Press Ctrl+C to stop the server")
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
