"""
Utility functions for RAG Document Assistant
Provides helper functions for logging, text processing, and common operations
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any
import os


def setup_logger(name: str = "rag_assistant", log_file: str = "logs/rag_assistant.log") -> logging.Logger:
    """
    Configure and return a logger instance
    
    Args:
        name: Logger name
        log_file: Path to log file
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def generate_document_id() -> str:
    """
    Generate a unique identifier for documents using UUID
    
    Returns:
        Unique document ID string
    """
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format
    
    Returns:
        Current timestamp string
    """
    return datetime.now().isoformat()


def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing extra whitespace
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace and newlines
    text = ' '.join(text.split())
    return text.strip()


def format_source_citation(chunk: Dict[str, Any], index: int) -> str:
    """
    Format a retrieved chunk for display as a source citation
    
    Args:
        chunk: Retrieved chunk with metadata
        index: Chunk index for numbering
        
    Returns:
        Formatted citation string
    """
    metadata = chunk.get('metadata', {})
    source = metadata.get('source', 'Unknown')
    page = metadata.get('page', 'N/A')
    
    return f"[{index + 1}] Source: {source} (Page {page})"


def calculate_token_count(text: str, chars_per_token: int = 4) -> int:
    """
    Estimate token count from text (rough approximation)
    
    Args:
        text: Input text
        chars_per_token: Average characters per token (default: 4)
        
    Returns:
        Estimated token count
    """
    return len(text) // chars_per_token


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to maximum length with ellipsis
    
    Args:
        text: Input text
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + "..."


def validate_api_key(api_key: str) -> bool:
    """
    Validate if API key is present and not empty
    
    Args:
        api_key: API key string
        
    Returns:
        True if valid, False otherwise
    """
    return bool(api_key and api_key.strip() and api_key != "your_api_key_here")


def format_chat_message(role: str, content: str, timestamp: str = None) -> Dict[str, str]:
    """
    Format a chat message with metadata
    
    Args:
        role: Message role (user/assistant)
        content: Message content
        timestamp: Optional timestamp
        
    Returns:
        Formatted message dictionary
    """
    message = {
        "role": role,
        "content": content,
        "timestamp": timestamp or get_timestamp()
    }
    return message


def merge_metadata(base_metadata: Dict, additional_metadata: Dict) -> Dict:
    """
    Merge two metadata dictionaries
    
    Args:
        base_metadata: Base metadata dictionary
        additional_metadata: Additional metadata to merge
        
    Returns:
        Merged metadata dictionary
    """
    merged = base_metadata.copy()
    merged.update(additional_metadata)
    return merged


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if division by zero
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
        
    Returns:
        Division result or default
    """
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default
