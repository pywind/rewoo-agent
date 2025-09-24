#!/bin/bash

# Navigate to web directory
cd "$(dirname "$0")"

echo "🚀 Starting ReWOO Web Application..."


# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "🌐 Starting Vite development server..."
npm run dev