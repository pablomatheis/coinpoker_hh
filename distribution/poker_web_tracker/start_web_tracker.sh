#!/bin/bash

# Poker Web Tracker Startup Script

echo "🌐 Starting Poker Web Tracker..."
echo "================================"

# Check if executable exists
if [ ! -f "./poker_web_tracker" ]; then
    echo "❌ Error: poker_web_tracker executable not found!"
    echo "Make sure you're in the correct directory."
    exit 1
fi

# Check if required folders exist
if [ ! -d "./templates" ]; then
    echo "❌ Error: templates/ folder not found!"
    echo "The web tracker requires templates/ and static/ folders."
    exit 1
fi

if [ ! -d "./static" ]; then
    echo "❌ Error: static/ folder not found!"
    echo "The web tracker requires templates/ and static/ folders."
    exit 1
fi

# Create data folder if it doesn't exist
mkdir -p data

# Make executable if needed
chmod +x poker_web_tracker

echo "✅ All requirements checked"
echo "🚀 Starting web server..."
echo ""
echo "📱 Access the web interface at:"
echo "   http://localhost:8080"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the web tracker
./poker_web_tracker