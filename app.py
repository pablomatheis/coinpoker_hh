#!/usr/bin/env python3
"""
Web-based Poker Table Tracker - Flask Backend

A web-based dynamic tracker for up to 12 players' stats during live poker games.
Cross-platform compatible and accessible from any browser.
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import json
import os
from typing import Dict, List, Optional

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global data storage
players_stats = {}
hero_stats = {}

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/api/players', methods=['GET'])
def get_players():
    """Get list of all available players"""
    return jsonify({
        'players': sorted(list(players_stats.keys())),
        'count': len(players_stats)
    })

@app.route('/api/player/<player_name>', methods=['GET'])
def get_player_stats(player_name):
    """Get stats for a specific player"""
    if player_name in players_stats:
        return jsonify({
            'player': player_name,
            'stats': players_stats[player_name]
        })
    else:
        return jsonify({'error': f'Player {player_name} not found'}), 404

@app.route('/api/hero', methods=['GET'])
def get_hero_stats():
    """Get hero stats"""
    return jsonify({
        'hero_stats': hero_stats
    })

@app.route('/api/load_players', methods=['POST'])
def load_players_stats():
    """Load players stats from uploaded JSON file"""
    global players_stats
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.endswith('.json'):
        try:
            data = json.loads(file.read())
            
            # Check if this is a hero stats file or players stats file
            if 'total_hands_played' in data:
                return jsonify({'error': 'This is a hero stats file. Use the hero stats upload instead.'}), 400
            
            players_stats = data
            return jsonify({
                'message': f'Successfully loaded {len(players_stats)} players',
                'players': sorted(list(players_stats.keys())),
                'count': len(players_stats)
            })
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON file'}), 400
        except Exception as e:
            return jsonify({'error': f'Error loading file: {str(e)}'}), 500
    
    return jsonify({'error': 'Please upload a valid JSON file'}), 400

@app.route('/api/load_hero', methods=['POST'])
def load_hero_stats():
    """Load hero stats from uploaded JSON file"""
    global hero_stats
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.endswith('.json'):
        try:
            data = json.loads(file.read())
            
            # Check if this is a hero stats file
            if 'total_hands_played' not in data:
                return jsonify({'error': 'This does not appear to be a hero stats file.'}), 400
            
            hero_stats = data
            return jsonify({
                'message': 'Hero stats loaded successfully',
                'hero_stats': hero_stats
            })
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON file'}), 400
        except Exception as e:
            return jsonify({'error': f'Error loading file: {str(e)}'}), 500
    
    return jsonify({'error': 'Please upload a valid JSON file'}), 400

@app.route('/api/load_default', methods=['POST'])
def load_default_data():
    """Load default data files if they exist"""
    global players_stats, hero_stats
    
    try:
        # Try to load from default location
        hero_file = "data/pmatheis_hero_stats.json"
        players_file = "data/pmatheis_players_stats.json"
        
        messages = []
        
        if os.path.exists(hero_file):
            with open(hero_file, 'r') as f:
                hero_stats = json.load(f)
            messages.append("Hero stats loaded from default file")
        
        if os.path.exists(players_file):
            with open(players_file, 'r') as f:
                players_stats = json.load(f)
            messages.append(f"Loaded {len(players_stats)} players from default file")
        
        if messages:
            return jsonify({
                'message': '. '.join(messages),
                'players': sorted(list(players_stats.keys())),
                'hero_stats': hero_stats,
                'players_count': len(players_stats)
            })
        else:
            return jsonify({'error': 'No default data files found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Error loading default data: {str(e)}'}), 500

@app.route('/api/search_players', methods=['GET'])
def search_players():
    """Search players by name"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({'players': sorted(list(players_stats.keys()))})
    
    # Filter players - prioritize those that start with query
    all_players = list(players_stats.keys())
    starts_with = [p for p in all_players if p.lower().startswith(query)]
    contains = [p for p in all_players if query in p.lower() and not p.lower().startswith(query)]
    filtered_players = starts_with + contains
    
    return jsonify({'players': filtered_players})

def load_startup_data():
    """Try to load default data on startup"""
    global players_stats, hero_stats
    
    try:
        hero_file = "data/pmatheis_hero_stats.json"
        players_file = "data/pmatheis_players_stats.json"
        
        if os.path.exists(hero_file):
            with open(hero_file, 'r') as f:
                hero_stats = json.load(f)
            print(f"Loaded hero stats from {hero_file}")
        
        if os.path.exists(players_file):
            with open(players_file, 'r') as f:
                players_stats = json.load(f)
            print(f"Loaded {len(players_stats)} players from {players_file}")
            
    except Exception as e:
        print(f"Could not load default data: {e}")

if __name__ == '__main__':
    # Load default data on startup
    load_startup_data()
    
    # Run the Flask app
    app.run(debug=False, host='0.0.0.0', port=8080) 