#!/bin/bash

# GPSkilledGuardian Bot Startup Script

echo "Starting GPSkilledGuardian Discord Bot..."

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

# Start the Discord bot
python -m bot.main
