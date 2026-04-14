#!/usr/bin/env python3
"""
Setup script for RAG-Based Intelligent Document Assistant
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    print(f"Python version {sys.version_info.major}.{sys.version_info.minor} OK")

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        # Try uv first (recommended)
        subprocess.run(["uv", "sync"], check=True)
        print("Dependencies installed successfully with uv")
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Fallback to pip
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("Dependencies installed successfully with pip")
        except subprocess.CalledProcessError:
            print("Error: Failed to install dependencies")
            sys.exit(1)

def setup_environment():
    """Set up environment configuration"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from template...")
        env_file.write_text(env_example.read_text())
        print("Please edit .env file and add your Groq API key")
        return False
    elif env_file.exists():
        print("Environment file exists")
        # Check if API key is set
        env_content = env_file.read_text()
        if "your_groq_api_key_here" in env_content:
            print("Warning: Please update your Groq API key in .env file")
            return False
        else:
            print("API key appears to be configured")
            return True
    else:
        print("Error: Neither .env nor .env.example found")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["uploads", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Directory {directory} ready")

def main():
    """Main setup function"""
    print("=== RAG-Based Intelligent Document Assistant Setup ===\n")
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    # Setup environment
    env_ready = setup_environment()
    
    print("\n=== Setup Complete ===")
    print("To run the application:")
    print("  uv run uvicorn main:app --reload")
    print("  or")
    print("  python main.py")
    print("\nThen open http://localhost:8000 in your browser")
    
    if not env_ready:
        print("\nIMPORTANT: Don't forget to configure your Groq API key in .env file!")

if __name__ == "__main__":
    main()
