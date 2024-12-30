import os
from dotenv import load_dotenv
from pathlib import Path

def load_config():
    """Load configuration from environment variables"""
    # Try to load from .env file if it exists
    env_path = Path('.') / '.env'
    load_dotenv(env_path)
    
    # Get required configuration
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        raise ValueError(
            "GOOGLE_API_KEY environment variable is required. "
            "Please set it in your .env file or environment."
        )
    
    return {
        'google_api_key': google_api_key,
        'temperature': float(os.getenv('TEMPERATURE', '0.3')),
        'model_name': os.getenv('MODEL_NAME', 'gemini-pro')
    }