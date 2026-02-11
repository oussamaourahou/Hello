#!/bin/bash

# Production startup script for Render

# Create data directory if it doesn't exist
mkdir -p /opt/render/project/src/data

# Set database path to persistent disk
export DB_PATH="/opt/render/project/src/data/email_archive.db"

# Start the application
exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
