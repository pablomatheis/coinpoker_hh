#!/usr/bin/env python3
"""
Poker Hand History Parser

Transforms CoinPoker hand history logs into structured JSON format with detailed financial tracking.
Filters out tournament hands and PLO/Omaha hands.
Handles edge cases like all-ins, uncalled bets, side pots, and multiple winners.
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from decimal import Decimal
import sys

@dataclass
class PlayerAction:
    """Represents a single player action during a hand"""
    player: str
    action: str  # fold, call, bet, raise, check, all-in
    amount: Decimal
    total_invested_this_street: Decimal
    street: str  # preflop, flop, turn, river

@dataclass
class Player:
    """Represents a player in the hand"""
    name: str
    seat: int
    starting_stack: Decimal
    position: str  # button, small_blind, big_blind, utg, etc.
    hole_cards: Optional[str] = None
    final_hand: Optional[str] = None
    amount_won: Decimal = Decimal('0')
    total_invested: Decimal = Decimal('0')
    net_result: Decimal = Decimal('0')  # amount_won - total_invested

@dataclass
class HandSummary:
    """Complete hand information with financial tracking"""
    hand_id: str
    game_type: str
    stakes: str
    table_name: str
    timestamp: str
    button_seat: int
    players: List[Player]
    actions: List[PlayerAction]
    board: List[str]
    total_pot: Decimal
    rake: Decimal
    winners: List[str]
    showdown_players: List[str] = field(default_factory=list)  # Players who appeared in showdown section
    is_tournament: bool = False
    is_plo: bool = False

class PokerHandParser:
    def __init__(self):
        self.current_hand = None
        self.players = {}
        self.actions = []
        self.current_street = "preflop"
        self.player_investments = {}  # Track total investment per player per street
        
    def parse_file(self, filename: str) -> List[HandSummary]:
        """Parse entire hand history file"""
        hands = []
        current_hand_lines = []
        
        # Statistics tracking
        self.total_hands_parsed = 0
        self.cancelled_hands = 0
        self.tournament_hands = 0
        self.plo_hands = 0
        
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if line.startswith('CoinPoker Hand #'):
                    # Process previous hand if exists
                    if current_hand_lines:
                        hand = self.parse_hand(current_hand_lines)
                        if hand:
                            self.total_hands_parsed += 1
                            
                            # Track filtering reasons
                            if hand.is_tournament:
                                self.tournament_hands += 1
                            elif hand.is_plo:
                                self.plo_hands += 1
                            elif self._is_cancelled_hand(hand):
                                self.cancelled_hands += 1
                            elif self._should_include_hand(hand):
                                hands.append(hand)
                    
                    # Start new hand
                    current_hand_lines = [line]
                    self._reset_parser()
                elif current_hand_lines:
                    current_hand_lines.append(line)
            
            # Process last hand
            if current_hand_lines:
                hand = self.parse_hand(current_hand_lines)
                if hand:
                    self.total_hands_parsed += 1
                    
                    # Track filtering reasons
                    if hand.is_tournament:
                        self.tournament_hands += 1
                    elif hand.is_plo:
                        self.plo_hands += 1
                    elif self._is_cancelled_hand(hand):
                        self.cancelled_hands += 1
                    elif self._should_include_hand(hand):
                        hands.append(hand)
        
        return hands
    
    def _should_include_hand(self, hand: HandSummary) -> bool:
        """Filter out tournament hands, PLO/Omaha hands, and cancelled hands"""
        if hand.is_tournament or hand.is_plo:
            return False
        
        # Filter out cancelled hands
        if self._is_cancelled_hand(hand):
            return False
        
        # Only include Hold'em No Limit cash games
        return "Hold'em No Limit" in hand.game_type
    
    def _reset_parser(self):
        """Reset parser state for new hand"""
        self.current_hand = None
        self.players = {}
        self.actions = []
        self.current_street = "preflop"
        self.player_investments = {}
    
    def parse_hand(self, lines: List[str]) -> Optional[HandSummary]:
        """Parse a single hand from list of lines"""
        if not lines:
            return None
            
        try:
            # Parse header
            header_info = self._parse_header(lines[0])
            if not header_info:
                return None
            
            hand_id, game_type, stakes, timestamp = header_info
            
            # Check if this is a tournament or PLO hand
            is_tournament = "Tournament" in game_type
            is_plo = "PLO" in game_type or "Omaha" in game_type
            
            # Parse table info and button
            table_name, button_seat = self._parse_table_info(lines[1])
            
            # Parse players
            seat_line_start = 2
            while seat_line_start < len(lines) and lines[seat_line_start].startswith('Seat '):
                self._parse_player_seat(lines[seat_line_start])
                seat_line_start += 1
            
            # Parse blinds and actions
            for i in range(seat_line_start, len(lines)):
                line = lines[i]
                self._parse_line(line)
            
            # Calculate final financial results
            self._calculate_financial_results()
            
            # Create hand summary
            hand = HandSummary(
                hand_id=hand_id,
                game_type=game_type,
                stakes=stakes,
                table_name=table_name,
                timestamp=timestamp,
                button_seat=button_seat,
                players=list(self.players.values()),
                actions=self.actions,
                board=self._extract_board_from_lines(lines),
                total_pot=self._extract_total_pot(lines),
                rake=self._extract_rake(lines),
                winners=self._extract_winners(lines),
                showdown_players=self._extract_showdown_players(lines),
                is_tournament=is_tournament,
                is_plo=is_plo
            )
            
            return hand
            
        except Exception as e:
            print(f"Error parsing hand: {e}")
            if len(lines) > 0:
                print(f"  Hand ID: {lines[0][:50] if lines[0] else 'Unknown'}")
            return None
    
    def _parse_header(self, line: str) -> Optional[Tuple[str, str, str, str]]:
        """Parse hand header line"""
        # CoinPoker Hand #195885587: Hold'em No Limit (0.01/0.02 ) 2025/01/23 20:15:54 GMT
        pattern = r"CoinPoker Hand #(\d+): (.+?) \((.+?)\) (.+)"
        match = re.match(pattern, line)
        if match:
            return match.group(1), match.group(2), match.group(3), match.group(4)
        return None
    
    def _parse_table_info(self, line: str) -> Tuple[str, int]:
        """Parse table name and button position"""
        # Table 'NL ₮2 I' 7-max Seat #7 is the button
        pattern = r"Table '(.+?)' .+? Seat #(\d+) is the button"
        match = re.match(pattern, line)
        if match:
            return match.group(1), int(match.group(2))
        return "Unknown", 1
    
    def _parse_player_seat(self, line: str):
        """Parse player seat information"""
        # Seat 1: pmatheis (1.19 in chips)
        pattern = r"Seat (\d+): (.+?) \((.+?) in chips\)"
        match = re.match(pattern, line)
        if match:
            try:
                seat = int(match.group(1))
                name = match.group(2).strip()
                stack_str = match.group(3).strip()
                stack = Decimal(stack_str)
                
                # Determine position (will be refined based on button position)
                position = f"seat_{seat}"
                
                player = Player(
                    name=name,
                    seat=seat,
                    starting_stack=stack,
                    position=position
                )
                
                self.players[name] = player
                self.player_investments[name] = {
                    'preflop': Decimal('0'),
                    'flop': Decimal('0'),
                    'turn': Decimal('0'),
                    'river': Decimal('0'),
                    'total': Decimal('0')
                }
            except (ValueError, IndexError) as e:
                print(f"Error parsing player seat '{line}': {e}")
    
    def _parse_line(self, line: str):
        """Parse individual action lines"""
        line = line.strip()
        
        # Update current street
        if line.startswith('*** HOLE CARDS ***'):
            self.current_street = "preflop"
        elif line.startswith('*** FLOP ***'):
            self.current_street = "flop"
        elif line.startswith('*** TURN ***'):
            self.current_street = "turn"
        elif line.startswith('*** RIVER ***'):
            self.current_street = "river"
        elif line.startswith('*** SHOW DOWN ***'):
            self.current_street = "showdown"
        
        # Parse player actions
        self._parse_player_action(line)
        
        # Parse dealt cards
        self._parse_dealt_cards(line)
        
        # Parse winnings
        self._parse_winnings(line)
        
        # Parse uncalled bets
        self._parse_uncalled_bet(line)
    
    def _parse_player_action(self, line: str):
        """Parse player betting actions"""
        patterns = [
            # Player: posts small blind (dead) 0.01
            (r"(.+?): posts small blind \(dead\) (.+)", "small_blind_dead"),
            # Player: posts big blind 0.05 (also handles dead big blinds)
            (r"(.+?): posts big blind (.+)", "big_blind"),
            # Player: posts small blind 0.01
            (r"(.+?): posts small blind (.+)", "small_blind"),
            # Player: posts straddle 0.04
            (r"(.+?): posts straddle (.+)", "straddle"),
            # Player: posts the ante 0.04
            (r"(.+?): posts the ante (.+)", "ante"),
            # Player: folds
            (r"(.+?): folds", "fold"),
            # Player: checks
            (r"(.+?): checks", "check"),
            # Player: calls 0.16 and is all-in (MOVED UP - must come before regular calls)
            (r"(.+?): calls (.+?) and is all-in", "call_all_in"),
            # Player: bets 1.37 and is all-in (MOVED UP - must come before regular bets)
            (r"(.+?): bets (.+?) and is all-in", "bet_all_in"),
            # Player: raises 0.55 and is all-in (MOVED UP - must come before regular raises)
            (r"(.+?): raises (.+?) and is all-in", "raise_all_in"),
            # Player: calls 0.02
            (r"(.+?): calls (.+?)$", "call"),
            # Player: bets 0.08
            (r"(.+?): bets (.+?)$", "bet"),
            # Player: raises 0.02 to 0.04
            (r"(.+?): raises (.+?) to (.+)", "raise"),
        ]
        
        for pattern, action_type in patterns:
            match = re.match(pattern, line)
            if match:
                player_name = match.group(1)
                
                if player_name not in self.players:
                    return
                
                amount = Decimal('0')
                total_invested = self.player_investments[player_name][self.current_street]
                
                try:
                    if action_type in ["fold", "check"]:
                        amount = Decimal('0')
                        total_invested = self.player_investments[player_name][self.current_street]
                    elif action_type == "ante":
                        # Antes are automatically deducted and added to pot, but don't count in betting action calculations
                        amount_str = match.group(2).strip()
                        amount = Decimal(amount_str)
                        # Keep total_invested_this_street unchanged - antes don't affect betting calculations
                        total_invested = self.player_investments[player_name][self.current_street]
                        # Still add to player's overall total_invested for balance purposes (they did lose this money)
                        self.player_investments[player_name]['total'] += amount
                    elif action_type in ["small_blind", "small_blind_dead", "big_blind", "straddle", "call", "bet", "call_all_in", "bet_all_in"]:
                        amount_str = match.group(2).strip()
                        amount = Decimal(amount_str)
                        total_invested = self.player_investments[player_name][self.current_street] + amount
                    elif action_type == "raise":
                        # For raises with "to", the amount is the ADDITIONAL amount, total is the final amount
                        additional_amount_str = match.group(2).strip()
                        total_amount_str = match.group(3).strip()
                        additional_amount = Decimal(additional_amount_str)
                        total_invested = Decimal(total_amount_str)
                        # The actual amount invested is the total amount for this street
                        amount = total_invested - self.player_investments[player_name][self.current_street]
                    elif action_type == "raise_all_in":
                        # For all-in raises without "to", the amount is the ADDITIONAL amount
                        # We need to calculate the total by adding to current investment
                        additional_amount_str = match.group(2).strip()
                        amount = Decimal(additional_amount_str)
                        total_invested = self.player_investments[player_name][self.current_street] + amount
                    else:
                        amount = Decimal('0')
                        total_invested = self.player_investments[player_name][self.current_street]
                    
                    # Update player investments (except for antes which are handled separately)
                    if amount > 0 and action_type != "ante":
                        self.player_investments[player_name][self.current_street] = total_invested
                        self.player_investments[player_name]['total'] += amount
                    
                    # Record action
                    action = PlayerAction(
                        player=player_name,
                        action=action_type,
                        amount=amount,
                        total_invested_this_street=total_invested,
                        street=self.current_street
                    )
                    
                    self.actions.append(action)
                    break
                    
                except (ValueError, IndexError) as e:
                    print(f"Error parsing action '{line}': {e}")
                    if "decimal" in str(e).lower() or "conversion" in str(e).lower():
                        print(f"  Problematic amount string: '{match.group(2) if len(match.groups()) > 1 else 'N/A'}'")
                    continue
    
    def _parse_dealt_cards(self, line: str):
        """Parse dealt cards to hero"""
        # Dealt to pmatheis [7c Kh]
        pattern = r"Dealt to (.+?) \[(.+?)\]"
        match = re.match(pattern, line)
        if match:
            player_name = match.group(1)
            cards = match.group(2)
            if player_name in self.players:
                self.players[player_name].hole_cards = cards
    
    def _parse_winnings(self, line: str):
        """Parse player winnings"""
        patterns = [
            # Player collected 1.27 from pot
            r"(.+?) collected (.+?) from pot",
            # Player collected 0.23 from side-pot 1
            r"(.+?) collected (.+?) from side-pot",
            # Player collected 0.23 from side-pot 1
            r"(.+?) collected (.+?) from side pot",
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                try:
                    player_name = match.group(1).strip()
                    amount_str = match.group(2).strip()
                    amount = Decimal(amount_str)
                    if player_name in self.players:
                        self.players[player_name].amount_won += amount
                        break
                except (ValueError, IndexError) as e:
                    print(f"Error parsing winnings '{line}': {e}")
    
    def _parse_uncalled_bet(self, line: str):
        """Parse uncalled bet returns"""
        # Uncalled bet (0.12) returned to Xh7CX
        pattern = r"Uncalled bet \((.+?)\) returned to (.+)"
        match = re.match(pattern, line)
        if match:
            try:
                amount_str = match.group(1).strip()
                amount = Decimal(amount_str)
                player_name = match.group(2).strip()
                
                if player_name in self.players:
                    # Subtract uncalled bet from player's total investment
                    self.player_investments[player_name]['total'] -= amount
            except (ValueError, IndexError) as e:
                print(f"Error parsing uncalled bet '{line}': {e}")
    
    def _calculate_financial_results(self):
        """Calculate final financial results for all players"""
        for player_name, player in self.players.items():
            player.total_invested = self.player_investments[player_name]['total']
            player.net_result = player.amount_won - player.total_invested
    
    def _extract_board_from_lines(self, lines: List[str]) -> List[str]:
        """Extract board cards from hand lines"""
        board = []
        for line in lines:
            if "Board [" in line:
                pattern = r"Board \[ (.+?) \]"
                match = re.search(pattern, line)
                if match:
                    board_str = match.group(1)
                    board = board_str.split()
                    break
        return board
    
    def _extract_total_pot(self, lines: List[str]) -> Decimal:
        """Extract total pot from summary"""
        for line in lines:
            if "Total pot" in line:
                pattern = r"Total pot (.+?) \|"
                match = re.search(pattern, line)
                if match:
                    try:
                        pot_str = match.group(1).strip()
                        return Decimal(pot_str)
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing total pot '{line}': {e}")
        return Decimal('0')
    
    def _extract_rake(self, lines: List[str]) -> Decimal:
        """Extract rake from summary"""
        for line in lines:
            if "Rake" in line:
                pattern = r"Rake (.+)"
                match = re.search(pattern, line)
                if match:
                    try:
                        rake_str = match.group(1).strip()
                        return Decimal(rake_str)
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing rake '{line}': {e}")
        return Decimal('0')
    
    def _extract_winners(self, lines: List[str]) -> List[str]:
        """Extract winners from summary"""
        winners = []
        for line in lines:
            if " and won (" in line:
                pattern = r"Seat \d+: (.+?) .*? and won \("
                match = re.search(pattern, line)
                if match:
                    winners.append(match.group(1))
            elif " collected (" in line and "Seat " in line:
                pattern = r"Seat \d+: (.+?) .*? collected \("
                match = re.search(pattern, line)
                if match:
                    winners.append(match.group(1))
        return winners

    def _extract_showdown_players(self, lines: List[str]) -> List[str]:
        """Extract players who appeared in the showdown section"""
        showdown_players = []
        in_showdown = False
        
        for line in lines:
            if "*** SHOW DOWN ***" in line:
                in_showdown = True
                continue
            
            if in_showdown:
                # Stop when we reach the next section or summary
                if line.startswith("***") or line.startswith("Total pot") or line.startswith("Seat "):
                    break
                
                # Parse "Player: shows [cards]" format
                if ": shows [" in line:
                    pattern = r"(.+?): shows \["
                    match = re.match(pattern, line)
                    if match:
                        player_name = match.group(1).strip()
                        showdown_players.append(player_name)
                
                # Parse "Player: mucks hand" format
                elif ": mucks hand" in line:
                    pattern = r"(.+?): mucks hand"
                    match = re.match(pattern, line)
                    if match:
                        player_name = match.group(1).strip()
                        showdown_players.append(player_name)
        
        return showdown_players

    def _is_cancelled_hand(self, hand: HandSummary) -> bool:
        """Check if hand was cancelled (only blinds posted, no winner)"""
        # If total winnings is 0 and there are contributions, it's likely cancelled
        total_winnings = sum(player.amount_won for player in hand.players)
        total_contributions = sum(player.total_invested for player in hand.players)
        
        # Cancelled if no winnings but there were contributions
        if total_winnings == 0 and total_contributions > 0:
            return True
            
        # Also check if only blind actions occurred
        non_blind_actions = [a for a in hand.actions if a.action not in ['small_blind', 'big_blind', 'straddle', 'ante']]
        if len(non_blind_actions) == 0 and total_winnings == 0:
            return True
            
        return False

def convert_decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_decimal_to_float(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_to_float(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return convert_decimal_to_float(asdict(obj))
    else:
        return obj

def main():
    if len(sys.argv) != 2:
        print("Usage: python poker_hand_parser.py <hand_log_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    parser = PokerHandParser()
    
    print(f"Parsing hand history file: {filename}")
    hands = parser.parse_file(filename)
    
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
    output_filename = filename.replace('.txt', '_parsed.json')
    with open(output_filename, 'w') as f:
        json.dump(hands_data, f, indent=2)
    
    print(f"Output written to: {output_filename}")
    
    # Print summary statistics
    balanced_hands = sum(1 for hand in hands_data if hand['financial_summary']['is_balanced'])
    print(f"Financial balance validation: {balanced_hands}/{len(hands_data)} hands balanced")

if __name__ == "__main__":
    main() 