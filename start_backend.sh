#!/bin/bash

# Start the FastAPI backend server

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Load environment variables from .env if it exists
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start the server
echo "Starting SHAED Order ELT Backend API..."
echo "API will be available at: http://localhost:${API_PORT:-8000}"
echo "API Documentation: http://localhost:${API_PORT:-8000}/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn backend.main:app --reload --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000}

