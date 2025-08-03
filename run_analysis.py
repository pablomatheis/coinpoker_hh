#!/usr/bin/env python3
"""
Main Poker Analysis Pipeline Runner

This script runs the complete poker analysis pipeline for any hero player.
Calls modules directly for better performance and executable compatibility.
Usage: python3 run_analysis.py <hand_log_file> [hero_name]

Example: python3 run_analysis.py data/hand_log.txt john_doe
"""

import sys
import os
import json
from config import HERO_NAME

# Import modules directly
from src.poker_hand_parser import PokerHandParser, convert_decimal_to_float
from src.poker_metrics import PokerMetrics
from src.balance_graph import BalanceGrapher
from src.create_stats_excel import StatsExcelGenerator

def run_step(step_func, description, *args, **kwargs):
    """Run a step and handle any errors"""
    print(f"\n🔄 {description}...")
    
    try:
        result = step_func(*args, **kwargs)
        print(f"✅ {description} completed successfully!")
        return True, result
    except Exception as e:
        print(f"❌ {description} failed!")
        print(f"Error: {str(e)}")
        return False, None

def parse_hand_history(hand_log_file):
    """Parse hand history file into JSON"""
    parser = PokerHandParser()
    
    print(f"Parsing hand history file: {hand_log_file}")
    hands = parser.parse_file(hand_log_file)
    
    print(f"Parsed {parser.total_hands_parsed} total hands")
    print(f"Filtered out: {parser.tournament_hands} tournament, {parser.plo_hands} PLO/Omaha, {parser.cancelled_hands} cancelled")
    print(f"Included {len(hands)} hands for analysis")
    
    # Convert to JSON-serializable format
    hands_data = []
    for hand in hands:
        hand_dict = convert_decimal_to_float(hand)
        
        # Validate financial balance (should sum to 0)
        total_player_results = sum(player['net_result'] for player in hand_dict['players'])
        rake = hand_dict['rake']
        
        # Add financial summary
        hand_dict['financial_summary'] = {
            'player_contributions': {player['name']: -player['total_invested'] for player in hand_dict['players']},
            'player_winnings': {player['name']: player['amount_won'] for player in hand_dict['players'] if player['amount_won'] > 0},
            'rake': rake,
            'balance_check': total_player_results + rake,  # Should be close to 0
            'is_balanced': abs(total_player_results + rake) < 0.005  # Allow for small rounding errors
        }
        
        hands_data.append(hand_dict)
    
    # Output JSON
    output_filename = hand_log_file.replace('.txt', '_parsed.json')
    with open(output_filename, 'w') as f:
        json.dump(hands_data, f, indent=2)
    
    print(f"Output written to: {output_filename}")
    
    # Print summary statistics
    balanced_hands = sum(1 for hand in hands_data if hand['financial_summary']['is_balanced'])
    print(f"Financial balance validation: {balanced_hands}/{len(hands_data)} hands balanced")
    
    return output_filename

def calculate_metrics(parsed_json_file, hero_name):
    """Calculate poker metrics and output JSON files"""
    print(f"Analyzing poker metrics for {hero_name}")
    
    metrics_calculator = PokerMetrics(hero_name)
    metrics_calculator.load_hands(parsed_json_file)
    metrics_calculator.analyze_all_hands()
    
    # Output metrics as JSON
    metrics = metrics_calculator.calculate_metrics()
    
    # Save hero stats as hero_stats.json in data folder
    hero_output_filename = f"data/{hero_name}_hero_stats.json"
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    with open(hero_output_filename, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\nHero metrics saved to: {hero_output_filename}")
    print(f"Total hands analyzed: {metrics['total_hands_played']}")
    print(f"Net result: ${metrics['net_result']:.2f}")
    print(f"VPIP: {metrics['vpip_percentage']:.1f}% | PFR: {metrics['pfr_percentage']:.1f}%")
    
    # Calculate and save player stats
    player_metrics = metrics_calculator.calculate_player_stats()
    
    # Sort players by number of hands against hero (most frequent opponents first)
    sorted_players = dict(sorted(player_metrics.items(), 
                               key=lambda x: x[1]['hands_against_hero'], 
                               reverse=True))
    
    players_output_filename = f"data/{hero_name}_players_stats.json"
    
    with open(players_output_filename, 'w') as f:
        json.dump(sorted_players, f, indent=2)
    
    print(f"Player stats saved to: {players_output_filename}")
    print(f"Analyzed {len(sorted_players)} opponents")
    
    # Show top 5 most frequent opponents
    if sorted_players:
        print("\nTop 5 Most Frequent Opponents:")
        for i, (player_name, stats) in enumerate(list(sorted_players.items())[:5]):
            net_vs = stats['hero_net_vs_player']
            hands = stats['hands_against_hero']
            vpip = stats['vpip_percentage']
            pfr = stats['pfr_percentage']
            print(f"  {i+1}. {player_name}: {hands} hands | Net: ${net_vs:+.2f} | VPIP: {vpip:.1f}% | PFR: {pfr:.1f}%")
    
    return hero_output_filename, players_output_filename

def create_balance_graph(parsed_json_file, hero_name):
    """Create balance progression graph"""
    print(f"Creating balance graph for {hero_name}")
    
    grapher = BalanceGrapher(hero_name)
    grapher.load_hands(parsed_json_file)
    grapher.calculate_balance_progression()
    grapher.create_balance_graph()
    grapher.print_balance_summary()
    
    return f"data/{hero_name}_balance_graph.png"

def create_excel_report(hero_stats_file, players_stats_file, hero_name):
    """Create comprehensive Excel report"""
    print(f"Creating Excel stats file for {hero_name}")
    
    generator = StatsExcelGenerator(hero_name)
    generator.load_data(hero_stats_file, players_stats_file)
    output_file = generator.create_excel_file()
    
    print(f"\nExcel file created successfully!")
    print(f"File contains the following sheets:")
    print("  - Hero Overview: Key performance metrics")
    print("  - Hero Details: Complete statistics table")
    print("  - Top Players Analysis: Players with 50+ hands")
    print("  - All Players: Complete opponent database")
    print("  - Profitability Analysis: Best and worst matchups")
    
    return output_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_analysis_standalone.py <hand_log_file> [hero_name]")
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
    
    # Step 1: Parse hand history
    success, parsed_json = run_step(parse_hand_history, "Parsing hand history", hand_log_file)
    if not success:
        return
    
    # Step 2: Calculate metrics
    success, metrics_files = run_step(calculate_metrics, f"Calculating poker metrics for {hero_name}", parsed_json, hero_name)
    if not success:
        return
    
    hero_stats_json, players_stats_json = metrics_files
    
    # Step 3: Generate balance graph
    success, balance_graph_png = run_step(create_balance_graph, f"Generating balance graph for {hero_name}", parsed_json, hero_name)
    if not success:
        return
    
    # Step 4: Create Excel report
    success, excel_file = run_step(create_excel_report, f"Creating Excel report for {hero_name}", hero_stats_json, players_stats_json, hero_name)
    if not success:
        return
    
    print(f"\n🎉 Analysis pipeline completed successfully for {hero_name}!")
    print(f"\n📊 Generated files:")
    print(f"   • {parsed_json} - Structured hand data")
    print(f"   • {hero_stats_json} - Hero statistics")
    print(f"   • {players_stats_json} - Opponent statistics")
    print(f"   • {balance_graph_png} - Balance progression graph")
    print(f"   • {excel_file} - Comprehensive Excel report")
    
    print(f"\n💡 To analyze a different player:")
    print(f"   python3 run_analysis_standalone.py {hand_log_file} <other_hero_name>")

if __name__ == "__main__":
    main()