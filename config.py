#!/usr/bin/env python3
"""
Configuration file for poker analysis pipeline
"""

# Default hero name - change this to analyze different players
DEFAULT_HERO_NAME = "pmatheis"

# You can also set this via environment variable
import os
HERO_NAME = os.environ.get('POKER_HERO_NAME', DEFAULT_HERO_NAME) 