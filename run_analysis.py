#!/usr/bin/env python3
"""
Main Poker Analysis Pipeline Runner

This script runs the complete poker analysis pipeline for any hero player.
Usage: python3 run_analysis.py <hand_log_file> [hero_name]

Example: python3 run_analysis.py data/hand_log.txt john_doe
"""

import sys
import subprocess
import os
from config import HERO_NAME

def run_command(command, description):
    """Run a command and print its description"""
    print(f"\n🔄 {description}...")
    print(f"Command: {' '.join(command)}")
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} completed successfully!")
        if result.stdout.strip():
            print("Output:")
            print(result.stdout)
    else:
        print(f"❌ {description} failed!")
        print("Error:")
        print(result.stderr)
        return False
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_analysis.py <hand_log_file> [hero_name]")
        print(f"  Default hero_name is '{HERO_NAME}'")
        print("\nThis script will:")
        print("  1. Parse hand history into JSON")
        print("  2. Calculate hero and player statistics")
        print("  3. Generate balance progression graph")
        print("  4. Create comprehensive Excel report")
        sys.exit(1)
    
    hand_log_file = sys.argv[1]
    hero_name = sys.argv[2] if len(sys.argv) > 2 else HERO_NAME
    
    # Verify input file exists
    if not os.path.exists(hand_log_file):
        print(f"❌ Error: Hand log file '{hand_log_file}' not found!")
        sys.exit(1)
    
    print(f"🎯 Starting poker analysis pipeline for hero: {hero_name}")
    print(f"📁 Input file: {hand_log_file}")
    
    # Determine output files
    base_name = os.path.splitext(hand_log_file)[0]
    parsed_json = f"{base_name}_parsed.json"
    hero_stats_json = f"data/{hero_name}_hero_stats.json"
    players_stats_json = f"data/{hero_name}_players_stats.json"
    balance_graph_png = f"data/{hero_name}_balance_graph.png"
    excel_file = f"data/{hero_name}_poker_stats.xlsx"
    
    # Step 1: Parse hand history
    if not run_command([
        "python3", "src/poker_hand_parser.py", hand_log_file
    ], "Parsing hand history"):
        return
    
    # Step 2: Calculate metrics
    if not run_command([
        "python3", "src/poker_metrics.py", parsed_json, hero_name, "--json"
    ], f"Calculating poker metrics for {hero_name}"):
        return
    
    # Step 3: Generate balance graph
    if not run_command([
        "python3", "src/balance_graph.py", parsed_json, hero_name
    ], f"Generating balance graph for {hero_name}"):
        return
    
    # Step 4: Create Excel report
    if not run_command([
        "python3", "src/create_stats_excel.py", hero_stats_json, players_stats_json, hero_name
    ], f"Creating Excel report for {hero_name}"):
        return
    
    print(f"\n🎉 Analysis pipeline completed successfully for {hero_name}!")
    print(f"\n📊 Generated files:")
    print(f"   • {parsed_json} - Structured hand data")
    print(f"   • {hero_stats_json} - Hero statistics")
    print(f"   • {players_stats_json} - Opponent statistics")
    print(f"   • {balance_graph_png} - Balance progression graph")
    print(f"   • {excel_file} - Comprehensive Excel report")
    
    print(f"\n💡 To analyze a different player:")
    print(f"   python3 run_analysis.py {hand_log_file} <other_hero_name>")

if __name__ == "__main__":
    main() 