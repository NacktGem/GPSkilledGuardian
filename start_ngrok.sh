#!/bin/bash

# GPSkilledGuardian Ngrok Tunnel Script

echo "Starting ngrok tunnel for webhook testing..."

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "Error: ngrok is not installed!"
    echo "Please install ngrok from https://ngrok.com/download"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Load ngrok auth token from .env
source .env

if [ -z "$NGROK_AUTH_TOKEN" ]; then
    echo "Error: NGROK_AUTH_TOKEN not set in .env file!"
    exit 1
fi

# Set ngrok auth token
ngrok config add-authtoken $NGROK_AUTH_TOKEN

# Get API port from .env or use default
API_PORT=${API_PORT:-8000}

# Start ngrok tunnel
if [ -z "$NGROK_DOMAIN" ]; then
    # Use random domain
    echo "Starting ngrok tunnel on port $API_PORT..."
    ngrok http $API_PORT
else
    # Use custom domain
    echo "Starting ngrok tunnel on port $API_PORT with domain $NGROK_DOMAIN..."
    ngrok http --domain=$NGROK_DOMAIN $API_PORT
fi
