"""
Claude AI client for accessing Anthropic's API.
"""
import anthropic
import os
from app.config import settings


def get_claude_client() -> anthropic.Anthropic:
    """
    Get configured Claude API client.
    
    Returns:
        Anthropic client instance
        
    Raises:
        FileNotFoundError: If .anthropickey file not found
        ValueError: If API key is empty
    """
    # Try reading from .anthropickey file first
    key_file = ".anthropickey"
    api_key = None
    
    if os.path.exists(key_file):
        with open(key_file, "r") as f:
            api_key = f.read().strip()
    
    # Fall back to environment variable
    if not api_key:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
    
    if not api_key:
        raise ValueError(
            "Anthropic API key not found. "
            "Create .anthropickey file or set ANTHROPIC_API_KEY environment variable."
        )
    
    return anthropic.Anthropic(api_key=api_key)





