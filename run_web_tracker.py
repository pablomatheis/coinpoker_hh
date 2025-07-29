#!/usr/bin/env python3
"""
Run script for the Web-based Poker Table Tracker

This script launches the Flask web application for tracking poker players.
Access the application in your browser at http://localhost:5000
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def check_requirements():
    """Check if Flask is installed"""
    try:
        import flask
        print(f"✓ Flask {flask.__version__} is installed")
        return True
    except ImportError:
        print("✗ Flask is not installed")
        print("Please install it by running: pip install flask>=3.0.0")
        print("Or install all requirements: pip install -r requirements.txt")
        return False

def launch_web_tracker():
    """Launch the web-based poker tracker"""
    print("=" * 60)
    print("🃏 POKER TABLE TRACKER - WEB VERSION")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("Error: app.py not found. Please run this script from the coinpoker_hh directory.")
        return False
    
    # Check if Flask is installed
    if not check_requirements():
        return False
    
    # Check if data files exist
    data_dir = Path('data')
    if data_dir.exists():
        hero_file = data_dir / 'pmatheis_hero_stats.json'
        players_file = data_dir / 'pmatheis_players_stats.json'
        
        if hero_file.exists():
            print(f"✓ Found hero stats: {hero_file}")
        else:
            print(f"ℹ  Hero stats not found: {hero_file}")
        
        if players_file.exists():
            print(f"✓ Found players stats: {players_file}")
        else:
            print(f"ℹ  Players stats not found: {players_file}")
    else:
        print("ℹ  Data directory not found - you can upload files through the web interface")
    
    print("\n🚀 Starting web server...")
    print("📱 The application will be available at: http://localhost:8080")
    print("💡 The server will automatically try to open your browser")
    print("🔄 Auto-reload is enabled for development")
    print("\n⚠️  Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Launch the Flask app
    try:
        # Import and run the app
        from app import app, load_startup_data
        
        # Load default data
        load_startup_data()
        
        # Try to open browser (only in main process, not reloader process)
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            try:
                webbrowser.open('http://localhost:8080')
            except Exception:
                pass  # Browser opening is optional
        
        # Run the Flask app
        app.run(
            debug=True,
            host='0.0.0.0',
            port=8080,
            use_reloader=True
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return False

if __name__ == "__main__":
    success = launch_web_tracker()
    if not success:
        sys.exit(1) 