#!/bin/bash

# Sample Analysis Script

echo "📊 Poker Analysis Pipeline - Sample Run"
echo "======================================="

# Check if executable exists
if [ ! -f "./poker_analysis" ]; then
    echo "❌ Error: poker_analysis executable not found!"
    echo "Make sure you're in the correct directory."
    exit 1
fi

# Check if sample data exists
if [ ! -f "./sample_data/hand_log.txt" ]; then
    echo "❌ Error: sample_data/hand_log.txt not found!"
    echo "Please provide a hand log file to analyze."
    echo ""
    echo "Usage: ./poker_analysis <hand_log_file> [hero_name]"
    echo "Example: ./poker_analysis my_hands.txt alice_poker"
    exit 1
fi

# Make executable if needed
chmod +x poker_analysis

echo "✅ Found sample data file"
echo "🎯 Running analysis on sample_data/hand_log.txt"
echo ""
echo "⏳ This may take a few minutes..."
echo "📈 Progress will be shown below:"
echo ""

# Create data folder if it doesn't exist
mkdir -p data

# Run the analysis
./poker_analysis sample_data/hand_log.txt pmatheis

echo ""
echo "🎉 Analysis complete! Check the 'data/' folder for results."