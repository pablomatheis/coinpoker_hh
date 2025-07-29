#!/usr/bin/env python3
"""
Poker Metrics Calculator for Hero Player

This script analyzes poker hands and calculates comprehensive statistics for the hero player.
Includes financial metrics, VPIP, PFR, aggression, positional stats, and more.
"""

import json
import sys
import os
from typing import Dict, List, Tuple, Optional
from decimal import Decimal
from collections import defaultdict, Counter
import statistics

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import HERO_NAME

class PokerMetrics:
    def __init__(self, hero_name: str = HERO_NAME):
        self.hero_name = hero_name
        self.hands = []
        self.hero_hands = []  # Hands where hero participated
        
        # Financial metrics
        self.total_winnings = 0.0
        self.total_invested = 0.0
        self.total_rake_paid = 0.0
        self.net_result = 0.0
        
        # Hand counting
        self.total_hands = 0
        self.hands_played = 0  # Hero participated
        
        # Pre-flop metrics
        self.vpip_hands = 0  # Voluntarily put money in pot
        self.pfr_hands = 0   # Pre-flop raised
        self.three_bet_hands = 0
        self.fold_to_three_bet = 0
        self.three_bet_opportunities = 0
        
        # Post-flop metrics
        self.showdown_hands = 0
        self.showdown_won = 0
        self.cbet_opportunities = 0
        self.cbet_made = 0
        self.fold_to_cbet = 0
        self.faced_cbet = 0
        self.check_raise_opportunities = 0
        self.check_raise_made = 0
        
        # New postflop metrics
        self.fold_vs_cbet = 0  # FvCB - How often they fold when facing a CBet
        self.fold_vs_cbet_opportunities = 0
        self.turn_cbet_opportunities = 0  # Turn CBet % - How often they barrel on turn
        self.turn_cbet_made = 0
        self.fold_to_turn_cbet = 0  # Fold to Turn CBet - How often they fold to 2nd barrel
        self.fold_to_turn_cbet_opportunities = 0
        self.river_cbet_opportunities = 0  # River Bet % - Frequency of betting on river
        self.river_cbet_made = 0
        self.fold_to_river_bet = 0  # Fold to River Bet - Fold tendency on river
        self.fold_to_river_bet_opportunities = 0
        self.donk_bet_opportunities = 0  # Donk Bet % - Betting into the preflop raiser
        self.donk_bet_made = 0
        
        # Positional tracking
        self.position_stats = defaultdict(lambda: {
            'hands': 0, 'vpip': 0, 'pfr': 0, 'won': 0.0, 'invested': 0.0
        })
        
        # Street-specific metrics
        self.street_actions = {
            'preflop': {'bet': 0, 'raise': 0, 'call': 0, 'fold': 0, 'check': 0},
            'flop': {'bet': 0, 'raise': 0, 'call': 0, 'fold': 0, 'check': 0},
            'turn': {'bet': 0, 'raise': 0, 'call': 0, 'fold': 0, 'check': 0},
            'river': {'bet': 0, 'raise': 0, 'call': 0, 'fold': 0, 'check': 0}
        }
        
        # Stakes analysis
        self.stakes_stats = defaultdict(lambda: {
            'hands': 0, 'won': 0.0, 'invested': 0.0, 'net': 0.0
        })
        
        # Session tracking
        self.session_results = []
        
        # Player vs player tracking
        self.player_stats = defaultdict(lambda: {
            # Head-to-head results (from hero's perspective)
            'hero_net_vs_player': 0.0,
            'hands_against_hero': 0,
            
            # Player's poker metrics
            'total_hands': 0,
            'vpip_hands': 0,
            'pfr_hands': 0,
            'three_bet_hands': 0,
            'three_bet_opportunities': 0,
            'showdown_hands': 0,
            'showdown_won': 0,
            'cbet_opportunities': 0,
            'cbet_made': 0,
            
            # New postflop metrics
            'fold_vs_cbet': 0,
            'fold_vs_cbet_opportunities': 0,
            'turn_cbet_opportunities': 0,
            'turn_cbet_made': 0,
            'fold_to_turn_cbet': 0,
            'fold_to_turn_cbet_opportunities': 0,
            'river_cbet_opportunities': 0,
            'river_cbet_made': 0,
            'fold_to_river_bet': 0,
            'fold_to_river_bet_opportunities': 0,
            'donk_bet_opportunities': 0,
            'donk_bet_made': 0,
            
            'street_actions': {
                'preflop': {'bet': 0, 'raise': 0, 'call': 0, 'fold': 0, 'check': 0},
                'flop': {'bet': 0, 'raise': 0, 'call': 0, 'fold': 0, 'check': 0},
                'turn': {'bet': 0, 'raise': 0, 'call': 0, 'fold': 0, 'check': 0},
                'river': {'bet': 0, 'raise': 0, 'call': 0, 'fold': 0, 'check': 0}
            },
            'total_winnings': 0.0,
            'total_invested': 0.0
        })
    
    def load_hands(self, filename: str):
        """Load hands from JSON file"""
        with open(filename, 'r') as f:
            self.hands = json.load(f)
        
        self.total_hands = len(self.hands)
        print(f"Loaded {self.total_hands} hands from {filename}")
        
        # Filter hands where hero participated
        for hand in self.hands:
            hero_player = self._get_hero_player(hand)
            if hero_player:
                self.hero_hands.append((hand, hero_player))
        
        self.hands_played = len(self.hero_hands)
        print(f"Hero ({self.hero_name}) participated in {self.hands_played} hands")
    
    def _get_hero_player(self, hand: Dict) -> Optional[Dict]:
        """Get hero player data from hand"""
        for player in hand['players']:
            if player['name'] == self.hero_name:
                return player
        return None
    
    def _get_hero_actions(self, hand: Dict, street: Optional[str] = None) -> List[Dict]:
        """Get all hero actions, optionally filtered by street"""
        actions = []
        for action in hand['actions']:
            if action['player'] == self.hero_name:
                if street is None or action['street'] == street:
                    actions.append(action)
        return actions
    
    def _determine_position(self, hand: Dict, hero_player: Dict) -> str:
        """Determine hero's position relative to button"""
        num_players = len(hand['players'])
        button_seat = hand['button_seat']
        hero_seat = hero_player['seat']
        
        # Calculate position relative to button
        seats_after_button = (hero_seat - button_seat) % (num_players + 1)
        
        if num_players <= 6:  # 6-max
            positions = ['BTN', 'SB', 'BB', 'UTG', 'MP', 'CO']
        else:  # Full ring
            positions = ['BTN', 'SB', 'BB', 'UTG', 'UTG+1', 'MP', 'MP+1', 'CO']
        
        if seats_after_button == 0:
            return 'BTN'
        elif seats_after_button == 1:
            return 'SB'
        elif seats_after_button == 2:
            return 'BB'
        else:
            # For other positions, use the index
            pos_index = min(seats_after_button - 1, len(positions) - 1)
            return positions[pos_index] if pos_index < len(positions) else f"UTG+{pos_index-3}"
    
    def _is_preflop_raiser(self, hand: Dict) -> bool:
        """Check if hero was the pre-flop raiser"""
        preflop_actions = self._get_hero_actions(hand, 'preflop')
        for action in preflop_actions:
            if action['action'] in ['raise', 'bet', 'raise_all_in', 'bet_all_in']:
                return True
        return False
    
    def _went_to_showdown(self, hand: Dict) -> bool:
        """Check if hero went to showdown"""
        # Check if hero appeared in the showdown section
        showdown_players = hand.get('showdown_players', [])
        return self.hero_name in showdown_players
    
    def _calculate_vpip(self, hand: Dict) -> bool:
        """Check if hero voluntarily put money in pot (excluding blinds/antes) - PREFLOP ONLY
        
        Examples:
        - BB, SB calls, hero checks → NOT VPIP (no voluntary action)
        - SB calls the BB → IS VPIP (voluntary call beyond forced SB)  
        - Fold after posting blinds/antes only → NOT VPIP (no voluntary action)
        - Any call/bet/raise → IS VPIP (voluntary money contribution)
        """
        preflop_actions = self._get_hero_actions(hand, 'preflop')
        
        for action in preflop_actions:
            action_type = action['action']
            
            # Voluntary actions that count as VPIP (any money contribution beyond forced blinds/antes)
            if action_type in ['call', 'bet', 'raise', 'call_all_in', 'bet_all_in', 'raise_all_in']:
                return True
            
            # Forced actions and passive actions don't count as VPIP
            # ['small_blind', 'big_blind', 'ante', 'check', 'fold'] 
        
        return False
    
    def _is_three_bet(self, hand: Dict) -> Tuple[bool, bool]:
        """Check if hero made a 3-bet and if hero had 3-bet opportunity"""
        preflop_actions = [a for a in hand['actions'] if a['street'] == 'preflop']
        
        # Find first raise (2-bet)
        first_raise_found = False
        hero_three_bet = False
        hero_had_opportunity = False
        
        for action in preflop_actions:
            if action['action'] in ['raise', 'raise_all_in']:
                if not first_raise_found:
                    first_raise_found = True
                    continue
                
                # This is a 3-bet
                if action['player'] == self.hero_name:
                    hero_three_bet = True
                    break
            
            # Hero had opportunity to 3-bet if there was a raise before hero's turn
            if action['player'] == self.hero_name and first_raise_found:
                hero_had_opportunity = True
                
        return hero_three_bet, hero_had_opportunity
    
    def analyze_all_hands(self):
        """Analyze all hands for comprehensive metrics"""
        print(f"\nAnalyzing {len(self.hero_hands)} hands for {self.hero_name}...")
        
        for hand, hero_player in self.hero_hands:
            self._analyze_hand(hand, hero_player)
            self._analyze_opponents_in_hand(hand, hero_player)
        
        # Calculate session results (group by date)
        self._calculate_session_results()
    
    def _analyze_opponents_in_hand(self, hand: Dict, hero_player: Dict):
        """Analyze all opponent players in this hand"""
        
        for player in hand['players']:
            if player['name'] == self.hero_name:
                continue  # Skip hero
                
            player_name = player['name']
            
            # Track that this player played against hero
            self.player_stats[player_name]['hands_against_hero'] += 1
            self.player_stats[player_name]['total_hands'] += 1
            
            # Head-to-head calculation
            hero_won = hero_player['amount_won'] > 0
            player_won = player['amount_won'] > 0
            
            if hero_won:
                # Hero won, count opponent's investment as hero's win against them
                self.player_stats[player_name]['hero_net_vs_player'] += player['total_invested']
            elif player_won:
                # Opponent won, count hero's investment as hero's loss against them  
                self.player_stats[player_name]['hero_net_vs_player'] -= hero_player['total_invested']
            
            # Track opponent's financial metrics
            self.player_stats[player_name]['total_winnings'] += player['amount_won']
            self.player_stats[player_name]['total_invested'] += player['total_invested']
            
            # Calculate opponent's VPIP
            if self._calculate_vpip_for_player(hand, player_name):
                self.player_stats[player_name]['vpip_hands'] += 1
            
            # Calculate opponent's PFR
            if self._is_preflop_raiser_for_player(hand, player_name):
                self.player_stats[player_name]['pfr_hands'] += 1
            
            # 3-bet analysis for opponent
            made_three_bet, had_three_bet_opp = self._is_three_bet_for_player(hand, player_name)
            if made_three_bet:
                self.player_stats[player_name]['three_bet_hands'] += 1
            if had_three_bet_opp:
                self.player_stats[player_name]['three_bet_opportunities'] += 1
            
            # Showdown analysis for opponent
            if self._went_to_showdown_for_player(hand, player_name):
                self.player_stats[player_name]['showdown_hands'] += 1
                if player['amount_won'] > 0:
                    self.player_stats[player_name]['showdown_won'] += 1
            
            # C-bet analysis for opponent
            if self._is_preflop_raiser_for_player(hand, player_name):
                flop_actions = self._get_player_actions(hand, player_name, 'flop')
                if flop_actions:  # Player saw flop
                    self.player_stats[player_name]['cbet_opportunities'] += 1
                    if any(a['action'] in ['bet', 'bet_all_in'] for a in flop_actions):
                        self.player_stats[player_name]['cbet_made'] += 1
            
            # New postflop analysis for opponent
            # FvCB - Fold vs CBet
            folded_to_cbet, faced_cbet = self._analyze_fold_vs_cbet(hand, player_name)
            if faced_cbet:
                self.player_stats[player_name]['fold_vs_cbet_opportunities'] += 1
                if folded_to_cbet:
                    self.player_stats[player_name]['fold_vs_cbet'] += 1
            
            # Turn CBet %
            made_turn_cbet, had_turn_cbet_opp = self._analyze_turn_cbet(hand, player_name)
            if had_turn_cbet_opp:
                self.player_stats[player_name]['turn_cbet_opportunities'] += 1
                if made_turn_cbet:
                    self.player_stats[player_name]['turn_cbet_made'] += 1
            
            # Fold to Turn CBet
            folded_to_turn_cbet, faced_turn_cbet = self._analyze_fold_to_turn_cbet(hand, player_name)
            if faced_turn_cbet:
                self.player_stats[player_name]['fold_to_turn_cbet_opportunities'] += 1
                if folded_to_turn_cbet:
                    self.player_stats[player_name]['fold_to_turn_cbet'] += 1
            
            # River CBet %
            made_river_cbet, had_river_cbet_opp = self._analyze_river_cbet(hand, player_name)
            if had_river_cbet_opp:
                self.player_stats[player_name]['river_cbet_opportunities'] += 1
                if made_river_cbet:
                    self.player_stats[player_name]['river_cbet_made'] += 1
            
            # Fold to River Bet
            folded_to_river_bet, faced_river_bet = self._analyze_fold_to_river_bet(hand, player_name)
            if faced_river_bet:
                self.player_stats[player_name]['fold_to_river_bet_opportunities'] += 1
                if folded_to_river_bet:
                    self.player_stats[player_name]['fold_to_river_bet'] += 1
            
            # Donk Bet %
            made_donk_bet, had_donk_opp = self._analyze_donk_bet(hand, player_name)
            if had_donk_opp:
                self.player_stats[player_name]['donk_bet_opportunities'] += 1
                if made_donk_bet:
                    self.player_stats[player_name]['donk_bet_made'] += 1
            
            # Street-specific action counting for opponent
            player_actions = self._get_player_actions(hand, player_name)
            for action in player_actions:
                street = action['street']
                action_type = action['action']
                
                # Normalize action types
                if action_type in ['raise', 'raise_all_in']:
                    self.player_stats[player_name]['street_actions'][street]['raise'] += 1
                elif action_type in ['bet', 'bet_all_in']:
                    self.player_stats[player_name]['street_actions'][street]['bet'] += 1
                elif action_type in ['call', 'call_all_in']:
                    self.player_stats[player_name]['street_actions'][street]['call'] += 1
                elif action_type == 'fold':
                    self.player_stats[player_name]['street_actions'][street]['fold'] += 1
                elif action_type == 'check':
                    self.player_stats[player_name]['street_actions'][street]['check'] += 1
    
    def _get_player_actions(self, hand: Dict, player_name: str, street: Optional[str] = None) -> List[Dict]:
        """Get all actions for a specific player, optionally filtered by street"""
        actions = []
        for action in hand['actions']:
            if action['player'] == player_name:
                if street is None or action['street'] == street:
                    actions.append(action)
        return actions
    
    def _calculate_vpip_for_player(self, hand: Dict, player_name: str) -> bool:
        """Check if player voluntarily put money in pot (excluding blinds/antes) - PREFLOP ONLY"""
        preflop_actions = self._get_player_actions(hand, player_name, 'preflop')
        
        for action in preflop_actions:
            action_type = action['action']
            
            # Voluntary actions that count as VPIP (any money contribution beyond forced blinds/antes)
            if action_type in ['call', 'bet', 'raise', 'call_all_in', 'bet_all_in', 'raise_all_in']:
                return True
            
            # Forced actions and passive actions don't count as VPIP
            # ['small_blind', 'big_blind', 'ante', 'check', 'fold'] 
        
        return False
    
    def _is_preflop_raiser_for_player(self, hand: Dict, player_name: str) -> bool:
        """Check if player was the pre-flop raiser"""
        preflop_actions = self._get_player_actions(hand, player_name, 'preflop')
        for action in preflop_actions:
            if action['action'] in ['raise', 'bet', 'raise_all_in', 'bet_all_in']:
                return True
        return False
    
    def _went_to_showdown_for_player(self, hand: Dict, player_name: str) -> bool:
        """Check if player went to showdown"""
        # Check if player appeared in the showdown section
        showdown_players = hand.get('showdown_players', [])
        return player_name in showdown_players
    
    def _is_three_bet_for_player(self, hand: Dict, player_name: str) -> Tuple[bool, bool]:
        """Check if player made a 3-bet and if player had 3-bet opportunity"""
        preflop_actions = [a for a in hand['actions'] if a['street'] == 'preflop']
        
        # Find first raise (2-bet)
        first_raise_found = False
        player_three_bet = False
        player_had_opportunity = False
        
        for action in preflop_actions:
            if action['action'] in ['raise', 'raise_all_in']:
                if not first_raise_found:
                    first_raise_found = True
                    continue
                
                # This is a 3-bet
                if action['player'] == player_name:
                    player_three_bet = True
                    break
            
            # Player had opportunity to 3-bet if there was a raise before player's turn
            if action['player'] == player_name and first_raise_found:
                player_had_opportunity = True
                
        return player_three_bet, player_had_opportunity

    def _analyze_fold_vs_cbet(self, hand: Dict, player_name: str) -> Tuple[bool, bool]:
        """Analyze if player folded vs called on flop when facing aggression"""
        flop_actions = [a for a in hand['actions'] if a['street'] == 'flop' and a['player'] == player_name]
        
        for action in flop_actions:
            if action['action'] in ['fold', 'call', 'call_all_in']:
                folded = action['action'] == 'fold'
                faced_aggression = True  # If they folded or called, they faced aggression
                return folded, faced_aggression
        
        return False, False

    def _analyze_turn_cbet(self, hand: Dict, player_name: str) -> Tuple[bool, bool]:
        """Analyze if player made a turn bet when they had the opportunity to bet into empty aggression"""
        # Get all turn actions in order
        turn_actions = [a for a in hand['actions'] if a['street'] == 'turn']
        if not turn_actions:
            return False, False
        
        # Check if player saw the turn
        player_turn_actions = self._get_player_actions(hand, player_name, 'turn')
        if not player_turn_actions:
            return False, False
        
        # Check if player had opportunity to bet (no prior betting action on turn)
        had_opportunity = False
        turn_bet = False
        
        for action in turn_actions:
            if action['action'] in ['bet', 'bet_all_in', 'raise', 'raise_all_in']:
                # First aggressive action on turn
                if action['player'] == player_name:
                    # Player was first to act aggressively
                    if action['action'] in ['bet', 'bet_all_in']:  # Only count bets, not raises
                        turn_bet = True
                    had_opportunity = True
                break  # Someone acted aggressively, no more opportunities
            elif action['player'] == player_name:
                # Player had chance to bet but didn't (checked/called/folded)
                had_opportunity = True
                break
        
        return turn_bet, had_opportunity

    def _analyze_fold_to_turn_cbet(self, hand: Dict, player_name: str) -> Tuple[bool, bool]:
        """Analyze if player folded vs called on turn when facing aggression"""
        turn_actions = [a for a in hand['actions'] if a['street'] == 'turn' and a['player'] == player_name]
        
        for action in turn_actions:
            if action['action'] in ['fold', 'call', 'call_all_in']:
                folded = action['action'] == 'fold'
                faced_aggression = True  # If they folded or called, they faced aggression
                return folded, faced_aggression
        
        return False, False

    def _analyze_river_cbet(self, hand: Dict, player_name: str) -> Tuple[bool, bool]:
        """Analyze if player bet on river when they had the opportunity to bet into empty aggression"""
        # Get all river actions in order
        river_actions = [a for a in hand['actions'] if a['street'] == 'river']
        if not river_actions:
            return False, False
        
        # Check if player saw the river
        player_river_actions = self._get_player_actions(hand, player_name, 'river')
        if not player_river_actions:
            return False, False
        
        # Check if player had opportunity to bet (no prior betting action on river)
        had_opportunity = False
        river_bet = False
        
        for action in river_actions:
            if action['action'] in ['bet', 'bet_all_in', 'raise', 'raise_all_in']:
                # First aggressive action on river
                if action['player'] == player_name:
                    # Player was first to act aggressively
                    if action['action'] in ['bet', 'bet_all_in']:  # Only count bets, not raises
                        river_bet = True
                    had_opportunity = True
                break  # Someone acted aggressively, no more opportunities
            elif action['player'] == player_name:
                # Player had chance to bet but didn't (checked/called/folded)
                had_opportunity = True
                break
        
        return river_bet, had_opportunity

    def _analyze_fold_to_river_bet(self, hand: Dict, player_name: str) -> Tuple[bool, bool]:
        """Analyze if player folded vs called on river when facing aggression"""
        river_actions = [a for a in hand['actions'] if a['street'] == 'river' and a['player'] == player_name]
        
        for action in river_actions:
            if action['action'] in ['fold', 'call', 'call_all_in']:
                folded = action['action'] == 'fold'
                faced_aggression = True  # If they folded or called, they faced aggression
                return folded, faced_aggression
        
        return False, False

    def _analyze_donk_bet(self, hand: Dict, player_name: str) -> Tuple[bool, bool]:
        """Analyze if player made a donk bet (betting into preflop raiser)"""
        # Find preflop raiser
        preflop_raiser = None
        preflop_actions = [a for a in hand['actions'] if a['street'] == 'preflop']
        for action in preflop_actions:
            if action['action'] in ['raise', 'bet', 'raise_all_in', 'bet_all_in']:
                preflop_raiser = action['player']
                break
        
        if not preflop_raiser or preflop_raiser == player_name:
            return False, False
        
        # Check postflop streets for donk bets
        donk_bet_made = False
        had_donk_opportunity = False
        
        for street in ['flop', 'turn', 'river']:
            street_actions = [a for a in hand['actions'] if a['street'] == street]
            
            # Check if player had opportunity to donk bet (acted before preflop raiser)
            player_acted_first = False
            for action in street_actions:
                if action['player'] == player_name:
                    had_donk_opportunity = True
                    if action['action'] in ['bet', 'bet_all_in']:
                        donk_bet_made = True
                    player_acted_first = True
                    break
                elif action['player'] == preflop_raiser and not player_acted_first:
                    break
        
        return donk_bet_made, had_donk_opportunity
    
    def _analyze_hand(self, hand: Dict, hero_player: Dict):
        """Analyze a single hand"""
        
        # Financial tracking
        winnings = hero_player['amount_won']
        invested = hero_player['total_invested']
        net = hero_player['net_result']
        
        self.total_winnings += winnings
        self.total_invested += invested
        self.net_result += net
        
        # Rake calculation - only when hero wins money
        if winnings > 0:
            # Calculate rake proportional to winnings vs total pot
            total_winnings_all_players = sum(p['amount_won'] for p in hand['players'])
            if total_winnings_all_players > 0:
                hero_rake_share = (winnings / total_winnings_all_players) * hand['rake']
                self.total_rake_paid += hero_rake_share
        
        # Position analysis
        position = self._determine_position(hand, hero_player)
        self.position_stats[position]['hands'] += 1
        self.position_stats[position]['won'] += winnings
        self.position_stats[position]['invested'] += invested
        
        # Stakes analysis
        stakes = hand['stakes'].strip()
        self.stakes_stats[stakes]['hands'] += 1
        self.stakes_stats[stakes]['won'] += winnings
        self.stakes_stats[stakes]['invested'] += invested
        self.stakes_stats[stakes]['net'] += net
        
        # VPIP calculation
        if self._calculate_vpip(hand):
            self.vpip_hands += 1
            self.position_stats[position]['vpip'] += 1
        
        # PFR calculation
        if self._is_preflop_raiser(hand):
            self.pfr_hands += 1
            self.position_stats[position]['pfr'] += 1
        
        # 3-bet analysis
        made_three_bet, had_three_bet_opp = self._is_three_bet(hand)
        if made_three_bet:
            self.three_bet_hands += 1
        if had_three_bet_opp:
            self.three_bet_opportunities += 1
        
        # Showdown analysis
        if self._went_to_showdown(hand):
            self.showdown_hands += 1
            if winnings > 0:
                self.showdown_won += 1
        
        # C-bet analysis
        if self._is_preflop_raiser(hand):
            flop_actions = self._get_hero_actions(hand, 'flop')
            if flop_actions:  # Hero saw flop
                self.cbet_opportunities += 1
                if any(a['action'] in ['bet', 'bet_all_in'] for a in flop_actions):
                    self.cbet_made += 1
        
        # New postflop analysis for hero
        # FvCB - Fold vs CBet
        folded_to_cbet, faced_cbet = self._analyze_fold_vs_cbet(hand, self.hero_name)
        if faced_cbet:
            self.fold_vs_cbet_opportunities += 1
            if folded_to_cbet:
                self.fold_vs_cbet += 1
        
        # Turn CBet %
        made_turn_cbet, had_turn_cbet_opp = self._analyze_turn_cbet(hand, self.hero_name)
        if had_turn_cbet_opp:
            self.turn_cbet_opportunities += 1
            if made_turn_cbet:
                self.turn_cbet_made += 1
        
        # Fold to Turn CBet
        folded_to_turn_cbet, faced_turn_cbet = self._analyze_fold_to_turn_cbet(hand, self.hero_name)
        if faced_turn_cbet:
            self.fold_to_turn_cbet_opportunities += 1
            if folded_to_turn_cbet:
                self.fold_to_turn_cbet += 1
        
        # River CBet %
        made_river_cbet, had_river_cbet_opp = self._analyze_river_cbet(hand, self.hero_name)
        if had_river_cbet_opp:
            self.river_cbet_opportunities += 1
            if made_river_cbet:
                self.river_cbet_made += 1
        
        # Fold to River Bet
        folded_to_river_bet, faced_river_bet = self._analyze_fold_to_river_bet(hand, self.hero_name)
        if faced_river_bet:
            self.fold_to_river_bet_opportunities += 1
            if folded_to_river_bet:
                self.fold_to_river_bet += 1
        
        # Donk Bet %
        made_donk_bet, had_donk_opp = self._analyze_donk_bet(hand, self.hero_name)
        if had_donk_opp:
            self.donk_bet_opportunities += 1
            if made_donk_bet:
                self.donk_bet_made += 1
        
        # Street-specific action counting
        hero_actions = self._get_hero_actions(hand)
        for action in hero_actions:
            street = action['street']
            action_type = action['action']
            
            # Normalize action types
            if action_type in ['raise', 'raise_all_in']:
                self.street_actions[street]['raise'] += 1
            elif action_type in ['bet', 'bet_all_in']:
                self.street_actions[street]['bet'] += 1
            elif action_type in ['call', 'call_all_in']:
                self.street_actions[street]['call'] += 1
            elif action_type == 'fold':
                self.street_actions[street]['fold'] += 1
            elif action_type == 'check':
                self.street_actions[street]['check'] += 1
    
    def _calculate_session_results(self):
        """Calculate session-by-session results"""
        session_data = defaultdict(float)
        
        for hand, hero_player in self.hero_hands:
            # Extract date from timestamp
            date = hand['timestamp'].split()[0]  # Get date part
            session_data[date] += hero_player['net_result']
        
        self.session_results = [(date, result) for date, result in sorted(session_data.items())]
    
    def calculate_metrics(self) -> Dict:
        """Calculate all poker metrics"""
        if self.hands_played == 0:
            return {}
        
        # Basic percentages
        vpip_pct = (self.vpip_hands / self.hands_played) * 100
        pfr_pct = (self.pfr_hands / self.hands_played) * 100
        three_bet_pct = (self.three_bet_hands / max(1, self.three_bet_opportunities)) * 100
        
        # Showdown metrics
        showdown_pct = (self.showdown_hands / self.hands_played) * 100
        won_at_showdown_pct = (self.showdown_won / max(1, self.showdown_hands)) * 100
        
        # C-bet metrics
        cbet_pct = (self.cbet_made / max(1, self.cbet_opportunities)) * 100
        
        # New postflop metrics
        fold_vs_flop_bet_pct = (self.fold_vs_cbet / max(1, self.fold_vs_cbet_opportunities)) * 100
        turn_cbet_pct = (self.turn_cbet_made / max(1, self.turn_cbet_opportunities)) * 100
        fold_vs_turn_bet_pct = (self.fold_to_turn_cbet / max(1, self.fold_to_turn_cbet_opportunities)) * 100
        river_bet_pct = (self.river_cbet_made / max(1, self.river_cbet_opportunities)) * 100
        fold_vs_river_bet_pct = (self.fold_to_river_bet / max(1, self.fold_to_river_bet_opportunities)) * 100
        donk_bet_pct = (self.donk_bet_made / max(1, self.donk_bet_opportunities)) * 100
        
        # Aggression metrics
        total_aggressive = sum(self.street_actions[street]['bet'] + self.street_actions[street]['raise'] 
                              for street in self.street_actions)
        total_passive = sum(self.street_actions[street]['call'] + self.street_actions[street]['check'] 
                           for street in self.street_actions)
        aggression_factor = total_aggressive / max(1, total_passive)
        
        # AFq - Aggression Frequency (betting/raising vs calling)
        postflop_aggressive = sum(self.street_actions[street]['bet'] + self.street_actions[street]['raise'] 
                                for street in ['flop', 'turn', 'river'])
        postflop_calls = sum(self.street_actions[street]['call'] for street in ['flop', 'turn', 'river'])
        afq_pct = (postflop_aggressive / max(1, postflop_aggressive + postflop_calls)) * 100
        
        # Win rate metrics
        bb_per_100 = 0
        if self.hands_played > 0:
            # Extract big blind from most common stakes
            stakes_counts = Counter(hand['stakes'].strip() for hand, _ in self.hero_hands)
            most_common_stakes = stakes_counts.most_common(1)[0][0] if stakes_counts else "0.01/0.02"
            try:
                bb = float(most_common_stakes.split('/')[1])
                bb_per_100 = (self.net_result / (self.hands_played / 100)) / bb
            except:
                bb_per_100 = 0
        
        # Session metrics
        winning_sessions = len([r for _, r in self.session_results if r > 0])
        total_sessions = len(self.session_results)
        session_win_rate = (winning_sessions / max(1, total_sessions)) * 100
        
        # Best and worst sessions
        best_session = max((r for _, r in self.session_results), default=0)
        worst_session = min((r for _, r in self.session_results), default=0)
        
        return {
            # Financial metrics
            'total_hands_played': self.hands_played,
            'total_hands_in_db': self.total_hands,
            'net_result': round(self.net_result, 2),
            'total_winnings': round(self.total_winnings, 2),
            'total_invested': round(self.total_invested, 2),
            'total_rake_paid': round(self.total_rake_paid, 2),
            'bb_per_100_hands': round(bb_per_100, 2),
            'roi_percentage': round((self.net_result / max(1, self.total_invested)) * 100, 2),
            
            # Pre-flop metrics
            'vpip_percentage': round(vpip_pct, 1),
            'pfr_percentage': round(pfr_pct, 1),
            'three_bet_percentage': round(three_bet_pct, 1),
            'three_bet_opportunities': self.three_bet_opportunities,
            
            # Post-flop metrics
            'went_to_showdown_percentage': round(showdown_pct, 1),
            'won_at_showdown_percentage': round(won_at_showdown_pct, 1),
            'cbet_percentage': round(cbet_pct, 1),
            'cbet_opportunities': self.cbet_opportunities,
            
            # New postflop metrics
            'fold_vs_flop_bet_percentage': round(fold_vs_flop_bet_pct, 1),
            'fold_vs_flop_bet_opportunities': self.fold_vs_cbet_opportunities,
            'afq_percentage': round(afq_pct, 1),
            'turn_cbet_percentage': round(turn_cbet_pct, 1),
            'turn_cbet_opportunities': self.turn_cbet_opportunities,
            'fold_vs_turn_bet_percentage': round(fold_vs_turn_bet_pct, 1),
            'fold_vs_turn_bet_opportunities': self.fold_to_turn_cbet_opportunities,
            'river_cbet_percentage': round(river_bet_pct, 1),
            'river_cbet_opportunities': self.river_cbet_opportunities,
            'fold_vs_river_bet_percentage': round(fold_vs_river_bet_pct, 1),
            'fold_vs_river_bet_opportunities': self.fold_to_river_bet_opportunities,
            'donk_bet_percentage': round(donk_bet_pct, 1),
            'donk_bet_opportunities': self.donk_bet_opportunities,
            
            # Aggression metrics
            'aggression_factor': round(aggression_factor, 2),
            'total_aggressive_actions': total_aggressive,
            'total_passive_actions': total_passive,
            
            # Session metrics
            'total_sessions': total_sessions,
            'winning_sessions': winning_sessions,
            'session_win_rate_percentage': round(session_win_rate, 1),
            'best_session': round(best_session, 2),
            'worst_session': round(worst_session, 2),
            'average_session': round(statistics.mean([r for _, r in self.session_results]), 2) if self.session_results else 0,
        }
    
    def calculate_player_stats(self) -> Dict:
        """Calculate poker metrics for all opponents"""
        player_metrics = {}
        
        for player_name, stats in self.player_stats.items():
            if stats['total_hands'] == 0:
                continue  # Skip players with no hands
            
            # Basic percentages
            vpip_pct = (stats['vpip_hands'] / stats['total_hands']) * 100
            pfr_pct = (stats['pfr_hands'] / stats['total_hands']) * 100
            three_bet_pct = (stats['three_bet_hands'] / max(1, stats['three_bet_opportunities'])) * 100
            
            # Showdown metrics
            showdown_pct = (stats['showdown_hands'] / stats['total_hands']) * 100
            won_at_showdown_pct = (stats['showdown_won'] / max(1, stats['showdown_hands'])) * 100
            
            # C-bet metrics
            cbet_pct = (stats['cbet_made'] / max(1, stats['cbet_opportunities'])) * 100
            
            # New postflop metrics
            fold_vs_flop_bet_pct = (stats['fold_vs_cbet'] / max(1, stats['fold_vs_cbet_opportunities'])) * 100
            turn_cbet_pct = (stats['turn_cbet_made'] / max(1, stats['turn_cbet_opportunities'])) * 100
            fold_vs_turn_bet_pct = (stats['fold_to_turn_cbet'] / max(1, stats['fold_to_turn_cbet_opportunities'])) * 100
            river_bet_pct = (stats['river_cbet_made'] / max(1, stats['river_cbet_opportunities'])) * 100
            fold_vs_river_bet_pct = (stats['fold_to_river_bet'] / max(1, stats['fold_to_river_bet_opportunities'])) * 100
            donk_bet_pct = (stats['donk_bet_made'] / max(1, stats['donk_bet_opportunities'])) * 100
            
            # Aggression metrics
            total_aggressive = sum(stats['street_actions'][street]['bet'] + stats['street_actions'][street]['raise'] 
                                  for street in stats['street_actions'])
            total_passive = sum(stats['street_actions'][street]['call'] + stats['street_actions'][street]['check'] 
                               for street in stats['street_actions'])
            aggression_factor = total_aggressive / max(1, total_passive)
            
            # AFq - Aggression Frequency (betting/raising vs calling)
            postflop_aggressive = sum(stats['street_actions'][street]['bet'] + stats['street_actions'][street]['raise'] 
                                    for street in ['flop', 'turn', 'river'])
            postflop_calls = sum(stats['street_actions'][street]['call'] for street in ['flop', 'turn', 'river'])
            afq_pct = (postflop_aggressive / max(1, postflop_aggressive + postflop_calls)) * 100
            
            # Net result from hero's perspective
            net_result_vs_hero = stats['hero_net_vs_player']
            
            player_metrics[player_name] = {
                # Head-to-head results (from hero's perspective)
                'hero_net_vs_player': round(net_result_vs_hero, 2),
                'hands_against_hero': stats['hands_against_hero'],
                
                # Player's poker metrics
                'total_hands': stats['total_hands'],
                'total_winnings': round(stats['total_winnings'], 2),
                'total_invested': round(stats['total_invested'], 2),
                'net_result': round(stats['total_winnings'] - stats['total_invested'], 2),
                
                # Pre-flop metrics
                'vpip_percentage': round(vpip_pct, 1),
                'pfr_percentage': round(pfr_pct, 1),
                'three_bet_percentage': round(three_bet_pct, 1),
                'three_bet_opportunities': stats['three_bet_opportunities'],
                
                # Post-flop metrics
                'went_to_showdown_percentage': round(showdown_pct, 1),
                'won_at_showdown_percentage': round(won_at_showdown_pct, 1),
                'cbet_percentage': round(cbet_pct, 1),
                'cbet_opportunities': stats['cbet_opportunities'],
                
                # New postflop metrics
                'fold_vs_flop_bet_percentage': round(fold_vs_flop_bet_pct, 1),
                'fold_vs_flop_bet_opportunities': stats['fold_vs_cbet_opportunities'],
                'afq_percentage': round(afq_pct, 1),
                'turn_cbet_percentage': round(turn_cbet_pct, 1),
                'turn_cbet_opportunities': stats['turn_cbet_opportunities'],
                'fold_vs_turn_bet_percentage': round(fold_vs_turn_bet_pct, 1),
                'fold_vs_turn_bet_opportunities': stats['fold_to_turn_cbet_opportunities'],
                'river_cbet_percentage': round(river_bet_pct, 1),
                'river_cbet_opportunities': stats['river_cbet_opportunities'],
                'fold_vs_river_bet_percentage': round(fold_vs_river_bet_pct, 1),
                'fold_vs_river_bet_opportunities': stats['fold_to_river_bet_opportunities'],
                'donk_bet_percentage': round(donk_bet_pct, 1),
                'donk_bet_opportunities': stats['donk_bet_opportunities'],
                
                # Aggression metrics
                'aggression_factor': round(aggression_factor, 2),
                'total_aggressive_actions': total_aggressive,
                'total_passive_actions': total_passive,
            }
        
        return player_metrics
    
    def print_detailed_report(self):
        """Print comprehensive poker metrics report"""
        metrics = self.calculate_metrics()
        
        if not metrics:
            print(f"No hands found for {self.hero_name}")
            return
        
        print(f"\n" + "="*60)
        print(f"COMPREHENSIVE POKER METRICS FOR {self.hero_name.upper()}")
        print(f"="*60)
        
        # Financial Summary
        print(f"\n📊 FINANCIAL SUMMARY")
        print(f"   Total Hands Played: {metrics['total_hands_played']:,}")
        print(f"   Net Result: ${metrics['net_result']:,.2f}")
        print(f"   Total Winnings: ${metrics['total_winnings']:,.2f}")
        print(f"   Total Invested: ${metrics['total_invested']:,.2f}")
        print(f"   Total Rake Paid: ${metrics['total_rake_paid']:,.2f}")
        print(f"   ROI: {metrics['roi_percentage']:.1f}%")
        print(f"   BB/100 hands: {metrics['bb_per_100_hands']:.2f}")
        
        # Pre-flop Metrics
        print(f"\n🎯 PRE-FLOP METRICS")
        print(f"   VPIP: {metrics['vpip_percentage']:.1f}%")
        print(f"   PFR: {metrics['pfr_percentage']:.1f}%")
        print(f"   3-bet: {metrics['three_bet_percentage']:.1f}% ({self.three_bet_hands}/{metrics['three_bet_opportunities']})")
        
        # Post-flop Metrics
        print(f"\n🃏 POST-FLOP METRICS")
        print(f"   Went to Showdown: {metrics['went_to_showdown_percentage']:.1f}%")
        print(f"   Won at Showdown: {metrics['won_at_showdown_percentage']:.1f}% ({self.showdown_won}/{self.showdown_hands})")
        print(f"   C-bet: {metrics['cbet_percentage']:.1f}% ({self.cbet_made}/{metrics['cbet_opportunities']})")
        
        # New postflop metrics
        print(f"\n🔄 ADVANCED POST-FLOP METRICS")
        print(f"   Fold vs Flop Bet: {metrics['fold_vs_flop_bet_percentage']:.1f}% ({self.fold_vs_cbet}/{metrics['fold_vs_flop_bet_opportunities']})")
        print(f"   AFq (Aggression Frequency): {metrics['afq_percentage']:.1f}%")
        print(f"   Turn CBet: {metrics['turn_cbet_percentage']:.1f}% ({self.turn_cbet_made}/{metrics['turn_cbet_opportunities']})")
        print(f"   Fold vs Turn Bet: {metrics['fold_vs_turn_bet_percentage']:.1f}% ({self.fold_to_turn_cbet}/{metrics['fold_vs_turn_bet_opportunities']})")
        print(f"   River Bet: {metrics['river_cbet_percentage']:.1f}% ({self.river_cbet_made}/{metrics['river_cbet_opportunities']})")
        print(f"   Fold vs River Bet: {metrics['fold_vs_river_bet_percentage']:.1f}% ({self.fold_to_river_bet}/{metrics['fold_vs_river_bet_opportunities']})")
        print(f"   Donk Bet: {metrics['donk_bet_percentage']:.1f}% ({self.donk_bet_made}/{metrics['donk_bet_opportunities']})")
        
        # Aggression Metrics
        print(f"\n⚔️  AGGRESSION METRICS")
        print(f"   Aggression Factor: {metrics['aggression_factor']:.2f}")
        print(f"   Aggressive Actions: {metrics['total_aggressive_actions']}")
        print(f"   Passive Actions: {metrics['total_passive_actions']}")
        
        # Session Analysis
        print(f"\n📅 SESSION ANALYSIS")
        print(f"   Total Sessions: {metrics['total_sessions']}")
        print(f"   Winning Sessions: {metrics['winning_sessions']} ({metrics['session_win_rate_percentage']:.1f}%)")
        print(f"   Best Session: ${metrics['best_session']:,.2f}")
        print(f"   Worst Session: ${metrics['worst_session']:,.2f}")
        print(f"   Average Session: ${metrics['average_session']:,.2f}")
        
        # Positional Analysis
        print(f"\n📍 POSITIONAL ANALYSIS")
        for position in ['BTN', 'CO', 'MP', 'UTG', 'SB', 'BB']:
            stats = self.position_stats.get(position)
            if stats and stats['hands'] > 0:
                vpip_pct = (stats['vpip'] / stats['hands']) * 100
                pfr_pct = (stats['pfr'] / stats['hands']) * 100
                net = stats['won'] - stats['invested']
                print(f"   {position:3}: {stats['hands']:3} hands | VPIP: {vpip_pct:4.1f}% | PFR: {pfr_pct:4.1f}% | Net: ${net:+6.2f}")
        
        # Stakes Analysis  
        print(f"\n💰 STAKES BREAKDOWN")
        for stakes in sorted(self.stakes_stats.keys()):
            stats = self.stakes_stats[stakes]
            if stats['hands'] > 0:
                print(f"   {stakes:8}: {stats['hands']:3} hands | Net: ${stats['net']:+7.2f}")
        
        # Action Frequency by Street
        print(f"\n🎲 ACTION FREQUENCY BY STREET")
        for street in ['preflop', 'flop', 'turn', 'river']:
            actions = self.street_actions[street]
            total = sum(actions.values())
            if total > 0:
                print(f"   {street.upper():8}: Bet: {actions['bet']:3} | Raise: {actions['raise']:3} | Call: {actions['call']:3} | Fold: {actions['fold']:3} | Check: {actions['check']:3}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 poker_metrics.py <parsed_json_file> [hero_name] [--json]")
        print("  Default hero_name is 'pmatheis'")
        print("  Use --json flag to output metrics as JSON file instead of detailed report")
        sys.exit(1)
    
    filename = sys.argv[1]
    hero_name = HERO_NAME
    output_json = False
    
    # Parse arguments
    for arg in sys.argv[2:]:
        if arg == "--json":
            output_json = True
        elif not arg.startswith("--"):
            hero_name = arg
    
    print(f"Analyzing poker metrics for {hero_name}")
    
    metrics_calculator = PokerMetrics(hero_name)
    metrics_calculator.load_hands(filename)
    metrics_calculator.analyze_all_hands()
    
    if output_json:
        # Output metrics as JSON to file
        metrics = metrics_calculator.calculate_metrics()
        
        # Save hero stats as hero_stats.json in data folder
        hero_output_filename = f"data/{hero_name}_hero_stats.json"
        
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
    else:
        # Output detailed report
        metrics_calculator.print_detailed_report()

if __name__ == "__main__":
    main() 