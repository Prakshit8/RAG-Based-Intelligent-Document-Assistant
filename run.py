#!/usr/bin/env python3
"""
RAG-Based Intelligent Document Assistant
Main entry point for the application
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

if __name__ == "__main__":
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if API key is set
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        print("ERROR: GROQ_API_KEY is not set or is using placeholder value.")
        print("Please set your Groq API key in the .env file:")
        print("1. Get an API key from https://console.groq.com/keys")
        print("2. Update your .env file with the actual API key")
        sys.exit(1)
    
    print("Starting RAG-Based Intelligent Document Assistant...")
    print("Web Interface: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    
    # Run the FastAPI application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        app_dir=str(backend_path)
    )
