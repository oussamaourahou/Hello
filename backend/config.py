"""
Configuration module for the application
"""
import os
from pathlib import Path

# Database configuration
DB_PATH = os.getenv('DB_PATH', 'email_archive.db')

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
PHOTOROOM_API_KEY = os.getenv('PHOTOROOM_API_KEY', '')

# Server Configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8000))

# CORS Configuration (for production, specify allowed origins)
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

# Data directory for persistent storage
DATA_DIR = os.getenv('DATA_DIR', str(Path(__file__).parent.parent))

def ensure_data_dir():
    """Ensure data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)
    return DATA_DIR
