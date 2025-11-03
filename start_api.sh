#!/bin/bash

# GPSkilledGuardian API Startup Script

echo "Starting GPSkilledGuardian FastAPI Server..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Create necessary directories
mkdir -p data logs

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the FastAPI server
python -m api.main
