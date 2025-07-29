#!/usr/bin/env python3
"""
Financial Balance Validator for Parsed Poker Hands

This script validates that all hands in the parsed JSON file are financially balanced.
A balanced hand means: total_contributions + rake = total_winnings (sum to zero)
"""

import json
import sys
from typing import List, Dict

def validate_hand_balance(hand: Dict) -> Dict:
    """Validate financial balance for a single hand"""
    
    # Calculate totals from players
    total_contributions = sum(player['total_invested'] for player in hand['players'])
    total_winnings = sum(player['amount_won'] for player in hand['players'])
    rake = hand['rake']
    
    # Calculate balance (should be close to 0)
    balance = total_winnings + rake - total_contributions
    
    # Check if balanced (allowing small rounding errors)
    is_balanced = abs(balance) < 0.005
    
    return {
        'hand_id': hand['hand_id'],
        'total_contributions': total_contributions,
        'total_winnings': total_winnings,
        'rake': rake,
        'balance': balance,
        'is_balanced': is_balanced,
        'expected_pot': total_contributions,
        'actual_pot': hand['total_pot'],
        'pot_matches': abs(hand['total_pot'] - total_contributions) < 0.005
    }

def analyze_financial_summary(hand: Dict) -> Dict:
    """Analyze the financial_summary section if it exists"""
    if 'financial_summary' not in hand:
        return None
    
    fs = hand['financial_summary']
    
    # Sum contributions (should be negative)
    contrib_sum = sum(fs['player_contributions'].values())
    
    # Sum winnings (should be positive)
    winnings_sum = sum(fs['player_winnings'].values())
    
    # Total should sum to zero: contributions (negative) + winnings (positive) + rake = 0
    total_sum = contrib_sum + winnings_sum + fs['rake']
    
    return {
        'contributions_sum': contrib_sum,
        'winnings_sum': winnings_sum,
        'rake': fs['rake'],
        'total_sum': total_sum,
        'financial_summary_balanced': abs(total_sum) < 0.005,
        'matches_flag': fs.get('is_balanced', False)
    }

def validate_all_hands(filename: str) -> None:
    """Validate all hands in the JSON file"""
    
    print(f"Loading hands from: {filename}")
    
    try:
        with open(filename, 'r') as f:
            hands = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filename}: {e}")
        return
    
    print(f"Loaded {len(hands)} hands")
    print("=" * 60)
    
    balanced_count = 0
    unbalanced_hands = []
    
    for i, hand in enumerate(hands):
        validation = validate_hand_balance(hand)
        fs_analysis = analyze_financial_summary(hand)
        
        if validation['is_balanced']:
            balanced_count += 1
        else:
            unbalanced_hands.append({
                'index': i,
                'validation': validation,
                'fs_analysis': fs_analysis
            })
    
    # Print summary
    print(f"BALANCE VALIDATION SUMMARY")
    print(f"Total hands: {len(hands)}")
    print(f"Balanced hands: {balanced_count}")
    print(f"Unbalanced hands: {len(unbalanced_hands)}")
    print(f"Balance rate: {balanced_count/len(hands)*100:.1f}%")
    print()
    
    # Show details for unbalanced hands
    if unbalanced_hands:
        print(f"UNBALANCED HANDS DETAILS (showing first 10):")
        print("-" * 60)
        
        for i, uh in enumerate(unbalanced_hands[:10]):
            val = uh['validation']
            fs = uh['fs_analysis']
            
            print(f"Hand #{uh['index']+1} (ID: {val['hand_id']})")
            print(f"  Contributions: {val['total_contributions']:.4f}")
            print(f"  Winnings: {val['total_winnings']:.4f}")
            print(f"  Rake: {val['rake']:.4f}")
            print(f"  Balance: {val['balance']:.6f}")
            print(f"  Expected pot: {val['expected_pot']:.4f}")
            print(f"  Actual pot: {val['actual_pot']:.4f}")
            print(f"  Pot matches: {val['pot_matches']}")
            
            if fs:
                print(f"  Financial Summary:")
                print(f"    Contrib sum: {fs['contributions_sum']:.4f}")
                print(f"    Winnings sum: {fs['winnings_sum']:.4f}")
                print(f"    Total sum: {fs['total_sum']:.6f}")
                print(f"    FS balanced: {fs['financial_summary_balanced']}")
                print(f"    Flag matches: {fs['matches_flag']}")
            print()
    
    # Additional statistics
    if unbalanced_hands:
        balances = [uh['validation']['balance'] for uh in unbalanced_hands]
        max_imbalance = max(abs(b) for b in balances)
        avg_imbalance = sum(abs(b) for b in balances) / len(balances)
        
        print(f"IMBALANCE STATISTICS:")
        print(f"  Maximum imbalance: {max_imbalance:.6f}")
        print(f"  Average imbalance: {avg_imbalance:.6f}")
        print(f"  Imbalances > 0.01: {sum(1 for b in balances if abs(b) > 0.01)}")
        print(f"  Imbalances > 0.1: {sum(1 for b in balances if abs(b) > 0.1)}")

def validate_specific_hand(filename: str, hand_id: str) -> None:
    """Validate a specific hand by ID"""
    
    with open(filename, 'r') as f:
        hands = json.load(f)
    
    target_hand = None
    for hand in hands:
        if hand['hand_id'] == hand_id:
            target_hand = hand
            break
    
    if not target_hand:
        print(f"Hand ID {hand_id} not found")
        return
    
    print(f"DETAILED ANALYSIS FOR HAND {hand_id}")
    print("=" * 50)
    
    validation = validate_hand_balance(target_hand)
    fs_analysis = analyze_financial_summary(target_hand)
    
    # Show player details
    print("PLAYER DETAILS:")
    for player in target_hand['players']:
        if player['total_invested'] > 0 or player['amount_won'] > 0:
            print(f"  {player['name']}: invested={player['total_invested']}, won={player['amount_won']}, net={player['net_result']}")
    
    print(f"\nVALIDATION:")
    for key, value in validation.items():
        print(f"  {key}: {value}")
    
    if fs_analysis:
        print(f"\nFINANCIAL SUMMARY ANALYSIS:")
        for key, value in fs_analysis.items():
            print(f"  {key}: {value}")
    
    # Show actions
    print(f"\nACTIONS:")
    for action in target_hand['actions']:
        if action['amount'] > 0:
            print(f"  {action['player']}: {action['action']} {action['amount']} ({action['street']})")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_balance.py <parsed_json_file> [hand_id]")
        print("  If hand_id is provided, analyzes that specific hand")
        print("  Otherwise, validates all hands")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    if len(sys.argv) == 3:
        hand_id = sys.argv[2]
        validate_specific_hand(filename, hand_id)
    else:
        validate_all_hands(filename)

if __name__ == "__main__":
    main() 