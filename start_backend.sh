#!/bin/bash

# Start the FastAPI backend server

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Load environment variables from .env if it exists
# Use Python's dotenv to properly handle all .env file formats
if [ -f ".env" ]; then
    # Export variables using Python's dotenv (handles spaces, comments, etc.)
    export $(python3 -c "
import sys
from dotenv import dotenv_values
try:
    env_vars = dotenv_values('.env')
    for key, value in env_vars.items():
        if value is not None:
            print(f'{key}={value}', end=' ')
except Exception as e:
    sys.exit(1)
" 2>/dev/null)
fi

# Start the server
echo "Starting SHAED Order ELT Backend API..."
echo "API will be available at: http://localhost:${API_PORT:-8000}"
echo "API Documentation: http://localhost:${API_PORT:-8000}/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn backend.main:app --reload --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000}

