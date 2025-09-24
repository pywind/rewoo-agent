#!/bin/bash

# ReWOO Application Start Script

echo "Starting ReWOO Application..."


# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp config/env.example .env
    echo "Please edit .env file with your configuration (especially OPENAI_API_KEY)"
    read -p "Press enter to continue when ready..."
fi

# Start the application
echo "Starting API server..."
uv run run_dev.py


# Start the development server
echo "🌐 Starting Vite development server..."
cd web && npm run dev