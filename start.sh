#!/bin/bash

# Rose Bot Start Script
# Usage: ./start.sh

echo "🌹 Starting Rose Bot..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating from template..."
    cp .env.example .env
    echo "Please edit .env with your bot token and owner ID"
    exit 1
fi

# Install/update dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Start the bot
echo "🚀 Launching Rose Bot..."
python -m bot
