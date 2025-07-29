#!/usr/bin/env python3
"""
Poker Table Tracker - Dynamic Player Management GUI

A dynamic GUI for tracking up to 12 players' stats during live poker games.
Starts with one player and allows adding more players dynamically.
Shows key metrics with scrolling support for overflow stats.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import sys
from typing import Dict, List, Optional

class ScrollablePlayerStatsPanel:
    """Individual player stats display panel with scrolling"""
    
    def __init__(self, parent, seat_number: int, on_player_change=None, on_remove=None):
        self.parent = parent
        self.seat_number = seat_number
        self.on_player_change = on_player_change
        self.on_remove = on_remove
        self.current_player = None
        
        # Create main frame
        self.frame = ttk.LabelFrame(parent, text=f"Player {seat_number}", padding="5")
        
        # Player selection
        self.player_var = tk.StringVar()
        self.player_var.trace('w', self._on_player_selected)
        self.all_players = []
        
        self.player_combo = ttk.Combobox(
            self.frame, 
            textvariable=self.player_var,
            state="normal",
            width=15
        )
        self.player_combo.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        
        # Bind typing events for filtering
        self.player_combo.bind('<KeyRelease>', self._on_keyrelease)
        self.player_combo.bind('<Button-1>', self._on_click)
        self.player_combo.bind('<FocusIn>', self._on_focus_in)
        self.player_combo.bind('<KeyPress>', self._on_keypress)
        
        # Create scrollable frame for stats
        self.canvas = tk.Canvas(self.frame, height=200, highlightthickness=0)
        self.v_scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Make scrollable frame expand to fill canvas width
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Grid the canvas and scrollbars
        self.canvas.grid(row=1, column=0, sticky="nsew", pady=(0, 5))
        self.v_scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 5))
        self.h_scrollbar.grid(row=2, column=0, sticky="ew")
        
        # Stats display
        self.stats_labels = {}
        self.stats_values = {}
        
        stats_to_show = [
            ("Hands", "hands_against_hero"),
            ("VPIP", "vpip_percentage"),
            ("PFR", "pfr_percentage"),
            ("3-Bet", "three_bet_percentage"),
            ("Agg Factor", "aggression_factor"),
            ("Showdown", "went_to_showdown_percentage"),
            ("SD Win", "won_at_showdown_percentage"),
            ("C-Bet", "cbet_percentage"),
            ("Fold vs Flop", "fold_vs_flop_bet_percentage"),
            ("AFq", "afq_percentage"),
            ("Turn CBet", "turn_cbet_percentage"),
            ("Fold vs Turn", "fold_vs_turn_bet_percentage"),
            ("River Bet", "river_cbet_percentage"),
            ("Fold vs River", "fold_vs_river_bet_percentage"),
            ("Donk Bet", "donk_bet_percentage"),
            ("vs Hero", "hero_net_vs_player")
        ]
        
        for i, (label, key) in enumerate(stats_to_show):
            row = i
            
            # Label
            self.stats_labels[key] = ttk.Label(self.scrollable_frame, text=f"{label}:")
            self.stats_labels[key].grid(row=row, column=0, sticky="w", padx=(0, 10))
            
            # Value
            self.stats_values[key] = ttk.Label(self.scrollable_frame, text="--", foreground="black")
            self.stats_values[key].grid(row=row, column=1, sticky="e")
        
        # Configure scrollable frame grid weights
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=0)  # Value column shouldn't expand
        
        # Control buttons frame
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        
        # Clear button
        self.clear_btn = ttk.Button(
            buttons_frame, 
            text="Clear", 
            command=self.clear_player,
            width=8
        )
        self.clear_btn.grid(row=0, column=0, padx=(0, 5))
        
        # Remove button (only show if seat_number > 1)
        if seat_number > 1:
            self.remove_btn = ttk.Button(
                buttons_frame, 
                text="Remove", 
                command=self._remove_player,
                width=8
            )
            self.remove_btn.grid(row=0, column=1)
        
        # Configure main frame grid weights
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=0)  # Vertical scrollbar column
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=0)  # Horizontal scrollbar row
        
        # Enable mouse wheel scrolling
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _on_canvas_configure(self, event):
        """Handle canvas resize to make scrollable frame fill available width"""
        canvas_width = event.width
        # Only set width if frame is smaller than canvas to prevent horizontal scrolling when not needed
        frame_width = self.scrollable_frame.winfo_reqwidth()
        if frame_width < canvas_width:
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
    def _remove_player(self):
        """Remove this player panel"""
        if self.on_remove:
            self.on_remove(self.seat_number)
        
    def set_players_list(self, players: List[str]):
        """Update the list of available players"""
        self.all_players = sorted(players)
        self.player_combo['values'] = [""] + self.all_players
        
    def _on_player_selected(self, *args):
        """Handle player selection"""
        player_name = self.player_var.get()
        if player_name and player_name in self.all_players and self.on_player_change:
            self.on_player_change(self.seat_number, player_name)
    
    def _on_keyrelease(self, event):
        """Handle key release events for filtering"""
        typed_text = self.player_var.get().lower()
        
        if not typed_text:
            # Show all players if nothing typed
            self.player_combo['values'] = [""] + self.all_players
        else:
            # Filter players - prioritize those that start with typed text
            starts_with = [p for p in self.all_players if p.lower().startswith(typed_text)]
            contains = [p for p in self.all_players if typed_text in p.lower() and not p.lower().startswith(typed_text)]
            filtered_players = starts_with + contains
            self.player_combo['values'] = filtered_players
            
            # Show dropdown if there are filtered results
            if filtered_players:
                self.player_combo.event_generate('<Down>')
                self.player_combo.after(1, lambda: self.player_combo.focus_set())
    
    def _on_click(self, event):
        """Handle click events on combobox"""
        # Reset to show all players when clicked
        if not self.player_var.get():
            self.player_combo['values'] = [""] + self.all_players
    
    def _on_focus_in(self, event):
        """Handle focus events"""
        # Make sure we can type when focused
        self.player_combo.focus_set()
    
    def _on_keypress(self, event):
        """Handle key press events"""
        # Ensure dropdown updates will show when typing starts
        self.player_combo.after(1, self._update_dropdown)
    
    def _update_dropdown(self):
        """Update dropdown contents"""
        typed_text = self.player_var.get().lower()
        if typed_text:
            starts_with = [p for p in self.all_players if p.lower().startswith(typed_text)]
            contains = [p for p in self.all_players if typed_text in p.lower() and not p.lower().startswith(typed_text)]
            filtered_players = starts_with + contains
            self.player_combo['values'] = filtered_players
    
    def update_stats(self, player_data: Optional[Dict]):
        """Update displayed stats for the selected player"""
        if not player_data:
            # Clear all stats
            for key, label in self.stats_values.items():
                label.config(text="--", foreground="black")
            self.current_player = None
            return
        
        self.current_player = player_data
        
        # Update each stat
        for key, label in self.stats_values.items():
            if key in player_data:
                value = player_data[key]
                
                if key == "hands_against_hero":
                    text = f"{value:,}"
                    color = "green" if value >= 50 else "orange" if value >= 20 else "red"
                elif key == "vpip_percentage":
                    text = f"{value:.1f}%"
                    if value < 16:
                        color = "#40a9ff"  # lighter blue
                    elif value <= 28:
                        color = "green"
                    else:
                        color = "red"
                elif key == "pfr_percentage":
                    text = f"{value:.1f}%"
                    if value < 14:
                        color = "#40a9ff"
                    elif value <= 25:
                        color = "green"
                    else:
                        color = "red"
                elif key == "three_bet_percentage":
                    text = f"{value:.1f}%"
                    if value < 4:
                        color = "#40a9ff"
                    elif value <= 8:
                        color = "green"
                    else:
                        color = "red"
                elif key == "cbet_percentage":
                    text = f"{value:.1f}%"
                    if value < 50:
                        color = "#40a9ff"
                    elif value <= 75:
                        color = "green"
                    else:
                        color = "red"
                elif key == "went_to_showdown_percentage":
                    text = f"{value:.1f}%"
                    if value < 20:
                        color = "#40a9ff"
                    elif value <= 30:
                        color = "green"
                    else:
                        color = "red"
                elif key == "won_at_showdown_percentage":
                    text = f"{value:.1f}%"
                    if value < 45:
                        color = "#40a9ff"
                    elif value <= 65:
                        color = "green"
                    else:
                        color = "red"
                elif key == "fold_vs_flop_bet_percentage":
                    text = f"{value:.1f}%"
                    if value < 40:
                        color = "#40a9ff"
                    elif value <= 60:
                        color = "green"
                    else:
                        color = "red"
                elif key == "fold_vs_turn_bet_percentage":
                    text = f"{value:.1f}%"
                    if value < 35:
                        color = "#40a9ff"
                    elif value <= 55:
                        color = "green"
                    else:
                        color = "red"
                elif key == "fold_vs_river_bet_percentage":
                    text = f"{value:.1f}%"
                    if value < 30:
                        color = "#40a9ff"
                    elif value <= 50:
                        color = "green"
                    else:
                        color = "red"
                elif key == "turn_cbet_percentage":
                    text = f"{value:.1f}%"
                    if value < 35:
                        color = "#40a9ff"
                    elif value <= 65:
                        color = "green"
                    else:
                        color = "red"
                elif key == "river_cbet_percentage":
                    text = f"{value:.1f}%"
                    if value < 30:
                        color = "#40a9ff"
                    elif value <= 60:
                        color = "green"
                    else:
                        color = "red"
                elif key == "donk_bet_percentage":
                    text = f"{value:.1f}%"
                    color = "red" if value > 15 else "green" if value <= 5 else "orange"
                elif key == "afq_percentage":
                    text = f"{value:.1f}%"
                    if value < 50:
                        color = "#40a9ff"
                    elif value <= 70:
                        color = "green"
                    else:
                        color = "red"
                elif key == "aggression_factor":
                    text = f"{value:.2f}"
                    color = "green" if value > 1.0 else "orange" if value > 0.5 else "red"
                elif key == "hero_net_vs_player":
                    text = f"${value:.2f}"
                    color = "green" if value > 0 else "red" if value < 0 else "black"
                else:
                    text = str(value)
                    color = "black"
                
                label.config(text=text, foreground=color)
            else:
                label.config(text="--", foreground="black")
    
    def clear_player(self):
        """Clear the selected player"""
        self.player_var.set("")
        self.update_stats(None)
    
    def get_player_name(self) -> str:
        """Get the currently selected player name"""
        return self.player_var.get()

class DynamicPokerTableTracker:
    """Main application class with dynamic player management"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dynamic Poker Table Tracker")
        self.root.geometry("1200x800")
        
        # Data
        self.players_stats = {}
        self.hero_stats = {}
        self.selected_players = {}  # seat_number -> player_name
        self.player_panels = {}  # seat_number -> panel
        self.next_seat_number = 1
        self.max_players = 12
        
        # Create UI
        self.create_ui()
        
        # Start with one player
        self.add_player()
        
        # Try to load default data
        self.load_default_data()
        
    def create_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure root grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title and controls
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="Dynamic Poker Table Tracker", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, sticky="w")
        
        # Control buttons
        controls_frame = ttk.Frame(title_frame)
        controls_frame.grid(row=0, column=1, sticky="e")
        
        ttk.Button(controls_frame, text="Add Player", command=self.add_player).grid(row=0, column=0, padx=5)
        ttk.Button(controls_frame, text="Load Stats", command=self.load_stats_file).grid(row=0, column=1, padx=5)
        ttk.Button(controls_frame, text="Clear All", command=self.clear_all_players).grid(row=0, column=2, padx=5)
        ttk.Button(controls_frame, text="Always On Top", command=self.toggle_always_on_top).grid(row=0, column=3, padx=5)
        
        title_frame.columnconfigure(1, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Load your player stats to begin")
        status_label = ttk.Label(title_frame, textvariable=self.status_var, foreground="gray")
        status_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Scrollable frame for players
        self.players_canvas = tk.Canvas(main_frame, highlightthickness=0)
        self.players_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.players_canvas.yview)
        self.players_frame = ttk.Frame(self.players_canvas)
        
        self.players_frame.bind(
            "<Configure>",
            lambda e: self.players_canvas.configure(scrollregion=self.players_canvas.bbox("all"))
        )
        
        self.players_canvas_window = self.players_canvas.create_window((0, 0), window=self.players_frame, anchor="nw")
        self.players_canvas.configure(yscrollcommand=self.players_scrollbar.set)
        
        # Make players frame expand to fill canvas width
        self.players_canvas.bind('<Configure>', self._on_players_canvas_configure)
        
        # Grid the players canvas and scrollbar
        self.players_canvas.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.players_scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 10))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Hero stats summary (bottom)
        self.create_hero_summary(main_frame)
        
        # Enable mouse wheel scrolling
        self.players_canvas.bind("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling for players canvas"""
        self.players_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _on_players_canvas_configure(self, event):
        """Handle canvas resize to make players frame fill available width"""
        canvas_width = event.width
        self.players_canvas.itemconfig(self.players_canvas_window, width=canvas_width)
        
    def create_hero_summary(self, parent):
        """Create hero stats summary panel"""
        hero_frame = ttk.LabelFrame(parent, text="Your Stats Summary", padding="5")
        hero_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        self.hero_labels = {}
        hero_stats = [
            ("Hands", "total_hands_played"),
            ("Net", "net_result"),
            ("ROI", "roi_percentage"),
            ("VPIP", "vpip_percentage"),
            ("PFR", "pfr_percentage"),
            ("3-Bet", "three_bet_percentage"),
            ("Agg Factor", "aggression_factor")
        ]
        
        for i, (label, key) in enumerate(hero_stats):
            ttk.Label(hero_frame, text=f"{label}:").grid(row=0, column=i*2, sticky="w", padx=(0, 5))
            self.hero_labels[key] = ttk.Label(hero_frame, text="--", foreground="black", font=("Arial", 9, "bold"))
            self.hero_labels[key].grid(row=0, column=i*2+1, sticky="w", padx=(0, 15))
    
    def add_player(self):
        """Add a new player panel"""
        if len(self.player_panels) >= self.max_players:
            messagebox.showwarning("Warning", f"Maximum {self.max_players} players allowed")
            return
        
        seat_number = self.next_seat_number
        self.next_seat_number += 1
        
        panel = ScrollablePlayerStatsPanel(
            self.players_frame,
            seat_number=seat_number,
            on_player_change=self.on_player_change,
            on_remove=self.remove_player
        )
        
        self.player_panels[seat_number] = panel
        
        # Set players list if we have data
        if self.players_stats:
            player_names = list(self.players_stats.keys())
            panel.set_players_list(player_names)
        
        # Update layout
        self.update_layout()
        
        self.status_var.set(f"Added Player {seat_number} - {len(self.player_panels)} players active")
    
    def remove_player(self, seat_number: int):
        """Remove a player panel"""
        if seat_number in self.player_panels:
            # Clear selection if exists
            if seat_number in self.selected_players:
                del self.selected_players[seat_number]
            
            # Destroy the panel
            self.player_panels[seat_number].frame.destroy()
            del self.player_panels[seat_number]
            
            # Update layout
            self.update_layout()
            
            self.status_var.set(f"Removed Player {seat_number} - {len(self.player_panels)} players active")
    
    def update_layout(self):
        """Update the dynamic layout based on number of players"""
        num_players = len(self.player_panels)
        
        if num_players == 0:
            return
        
        # Clear existing grid
        for widget in self.players_frame.winfo_children():
            widget.grid_forget()
        
        # Determine grid configuration
        if num_players == 1:
            cols = 1
        elif num_players <= 4:
            cols = 2
        elif num_players <= 9:
            cols = 3
        else:
            cols = 4
        
        # Grid the panels
        sorted_panels = sorted(self.player_panels.items())
        for i, (seat_num, panel) in enumerate(sorted_panels):
            row = i // cols
            col = i % cols
            panel.frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        
        # Reset all grid weights first
        for i in range(10):  # Reset up to 10 columns (more than max needed)
            self.players_frame.columnconfigure(i, weight=0)
        for i in range(10):  # Reset up to 10 rows
            self.players_frame.rowconfigure(i, weight=0)
        
        # Configure grid weights for current layout
        for i in range(cols):
            self.players_frame.columnconfigure(i, weight=1)
        
        rows = (num_players + cols - 1) // cols
        for i in range(rows):
            self.players_frame.rowconfigure(i, weight=1)
    
    def load_default_data(self):
        """Try to load default data files"""
        try:
            # Try to load from default location
            hero_file = "data/pmatheis_hero_stats.json"
            players_file = "data/pmatheis_players_stats.json"
            
            with open(hero_file, 'r') as f:
                self.hero_stats = json.load(f)
            
            with open(players_file, 'r') as f:
                self.players_stats = json.load(f)
            
            self.update_ui_after_load()
            self.status_var.set(f"Loaded {len(self.players_stats)} players from default files")
            
        except FileNotFoundError:
            self.status_var.set("No default data found - please load your stats files")
        except Exception as e:
            self.status_var.set(f"Error loading default data: {str(e)}")
    
    def load_stats_file(self):
        """Load player stats file"""
        filename = filedialog.askopenfilename(
            title="Select Player Stats JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            if 'total_hands_played' in data:
                # This is a hero stats file
                self.hero_stats = data
                self.status_var.set("Hero stats loaded")
            else:
                # This is a players stats file
                self.players_stats = data
                self.status_var.set(f"Loaded {len(self.players_stats)} players")
            
            self.update_ui_after_load()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def update_ui_after_load(self):
        """Update UI after loading data"""
        # Update player lists in all panels
        player_names = list(self.players_stats.keys())
        for panel in self.player_panels.values():
            panel.set_players_list(player_names)
        
        # Update hero stats
        if self.hero_stats:
            for key, label in self.hero_labels.items():
                if key in self.hero_stats:
                    value = self.hero_stats[key]
                    if key == "total_hands_played":
                        text = f"{value:,}"
                    elif key == "net_result":
                        text = f"${value:.2f}"
                        label.config(foreground="green" if value > 0 else "red" if value < 0 else "black")
                    elif "percentage" in key:
                        text = f"{value:.1f}%"
                    else:
                        text = f"{value:.2f}"
                    
                    label.config(text=text)
    
    def on_player_change(self, seat_number: int, player_name: str):
        """Handle player selection change"""
        if not player_name:
            if seat_number in self.selected_players:
                del self.selected_players[seat_number]
            self.player_panels[seat_number].update_stats(None)
            return
        
        # Check if player is already selected in another seat
        for seat, name in self.selected_players.items():
            if name == player_name and seat != seat_number:
                messagebox.showwarning("Warning", f"{player_name} is already selected in Player {seat}")
                self.player_panels[seat_number].clear_player()
                return
        
        # Update selection
        self.selected_players[seat_number] = player_name
        
        # Get player stats
        player_data = self.players_stats.get(player_name)
        if player_data:
            self.player_panels[seat_number].update_stats(player_data)
            hands = player_data.get('hands_against_hero', 0)
            self.status_var.set(f"Selected {player_name} ({hands} hands)")
        else:
            self.status_var.set(f"No data found for {player_name}")
    
    def clear_all_players(self):
        """Clear all selected players"""
        for panel in self.player_panels.values():
            panel.clear_player()
        self.selected_players.clear()
        self.status_var.set("All players cleared")
    
    def toggle_always_on_top(self):
        """Toggle always on top window state"""
        current_state = self.root.attributes('-topmost')
        self.root.attributes('-topmost', not current_state)
        state_text = "ON" if not current_state else "OFF"
        self.status_var.set(f"Always on top: {state_text}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    app = DynamicPokerTableTracker()
    app.run()

if __name__ == "__main__":
    main() 