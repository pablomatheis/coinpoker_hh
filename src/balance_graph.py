#!/usr/bin/env python3
"""
Poker Balance Graph Generator

This script creates a graph showing the hero's cumulative net result balance over time/hands.
Shows the running profit/loss throughout all sessions.
"""

import json
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from typing import List, Tuple
import numpy as np

class BalanceGrapher:
    def __init__(self, hero_name: str = "pmatheis"):
        self.hero_name = hero_name
        self.hands = []
        self.hero_hands = []
        self.balance_data = []  # (hand_number, cumulative_balance, timestamp)
        
    def load_hands(self, filename: str):
        """Load hands from JSON file"""
        with open(filename, 'r') as f:
            self.hands = json.load(f)
        
        print(f"Loaded {len(self.hands)} hands from {filename}")
        
        # Filter and sort hands where hero participated
        hero_hand_data = []
        for i, hand in enumerate(self.hands):
            hero_player = self._get_hero_player(hand)
            if hero_player:
                hero_hand_data.append((i, hand, hero_player))
        
        # Sort by timestamp to ensure chronological order
        hero_hand_data.sort(key=lambda x: self._parse_timestamp(x[1]['timestamp']))
        self.hero_hands = hero_hand_data
        
        print(f"Hero ({self.hero_name}) participated in {len(self.hero_hands)} hands")
    
    def _get_hero_player(self, hand: dict) -> dict:
        """Get hero player data from hand"""
        for player in hand['players']:
            if player['name'] == self.hero_name:
                return player
        return None
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime object"""
        try:
            # Format: "2025/01/23 20:15:54 GMT"
            date_part = timestamp_str.replace(" GMT", "")
            return datetime.strptime(date_part, "%Y/%m/%d %H:%M:%S")
        except:
            # Fallback if parsing fails
            return datetime.now()
    
    def calculate_balance_progression(self):
        """Calculate cumulative balance over time"""
        cumulative_balance = 0.0
        self.balance_data = []
        
        for hand_index, (original_index, hand, hero_player) in enumerate(self.hero_hands):
            net_result = hero_player['net_result']
            cumulative_balance += net_result
            
            timestamp = self._parse_timestamp(hand['timestamp'])
            
            self.balance_data.append((
                hand_index + 1,  # Hand number (1-indexed)
                cumulative_balance,
                timestamp,
                hand['hand_id'],
                net_result
            ))
    
    def create_balance_graph(self, output_filename: str = None):
        """Create and save balance progression graph"""
        if not self.balance_data:
            print("No balance data to graph. Run calculate_balance_progression() first.")
            return
        
        # Extract data for plotting
        hand_numbers = [data[0] for data in self.balance_data]
        balances = [data[1] for data in self.balance_data]
        timestamps = [data[2] for data in self.balance_data]
        
        # Create the plot
        plt.figure(figsize=(14, 8))
        
        # Main balance line
        plt.plot(hand_numbers, balances, linewidth=2, color='#2E86AB', alpha=0.8)
        
        # Fill areas for profit/loss
        plt.fill_between(hand_numbers, balances, 0, 
                        where=[b >= 0 for b in balances], 
                        color='green', alpha=0.3, label='Profit')
        plt.fill_between(hand_numbers, balances, 0, 
                        where=[b < 0 for b in balances], 
                        color='red', alpha=0.3, label='Loss')
        
        # Add zero line
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=0.8)
        
        # Formatting
        plt.title(f'{self.hero_name.upper()} - Cumulative Balance Progression', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Hand Number', fontsize=12)
        plt.ylabel('Cumulative Balance ($)', fontsize=12)
        
        # Grid
        plt.grid(True, alpha=0.3)
        
        # Format y-axis as currency
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.2f}'))
        
        # Add some statistics as text
        final_balance = balances[-1] if balances else 0
        max_balance = max(balances) if balances else 0
        min_balance = min(balances) if balances else 0
        total_hands = len(balances)
        
        stats_text = f"""Final Balance: ${final_balance:.2f}
Max Balance: ${max_balance:.2f}
Min Balance: ${min_balance:.2f}
Total Hands: {total_hands:,}"""
        
        plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Legend
        plt.legend(loc='upper right')
        
        # Tight layout
        plt.tight_layout()
        
        # Save the graph
        if output_filename is None:
            output_filename = f"data/{self.hero_name}_balance_graph.png"
        
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        print(f"Balance graph saved to: {output_filename}")
    
    def print_balance_summary(self):
        """Print summary statistics"""
        if not self.balance_data:
            return
        
        balances = [data[1] for data in self.balance_data]
        
        print(f"\n" + "="*50)
        print(f"BALANCE PROGRESSION SUMMARY FOR {self.hero_name.upper()}")
        print(f"="*50)
        
        print(f"Starting Balance: $0.00")
        print(f"Final Balance: ${balances[-1]:.2f}")
        print(f"Maximum Balance: ${max(balances):.2f}")
        print(f"Minimum Balance: ${min(balances):.2f}")
        print(f"Total Hands: {len(balances):,}")
        
        # Calculate some streaks
        winning_streaks = []
        losing_streaks = []
        current_streak = 0
        last_balance = 0
        
        for _, balance, _, _, net_result in self.balance_data:
            if net_result > 0:
                if current_streak >= 0:
                    current_streak += 1
                else:
                    if current_streak < 0:
                        losing_streaks.append(abs(current_streak))
                    current_streak = 1
            elif net_result < 0:
                if current_streak <= 0:
                    current_streak -= 1
                else:
                    if current_streak > 0:
                        winning_streaks.append(current_streak)
                    current_streak = -1
            # net_result == 0 doesn't change streak
        
        # Add final streak
        if current_streak > 0:
            winning_streaks.append(current_streak)
        elif current_streak < 0:
            losing_streaks.append(abs(current_streak))
        
        if winning_streaks:
            print(f"Longest Winning Streak: {max(winning_streaks)} hands")
        if losing_streaks:
            print(f"Longest Losing Streak: {max(losing_streaks)} hands")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 balance_graph.py <parsed_json_file> [hero_name]")
        print("  Default hero_name is 'pmatheis'")
        print("  Creates PNG balance graph")
        sys.exit(1)
    
    filename = sys.argv[1]
    hero_name = sys.argv[2] if len(sys.argv) > 2 else "pmatheis"
    
    print(f"Creating balance graph for {hero_name}")
    
    grapher = BalanceGrapher(hero_name)
    grapher.load_hands(filename)
    grapher.calculate_balance_progression()
    grapher.create_balance_graph()
    grapher.print_balance_summary()

if __name__ == "__main__":
    main() 