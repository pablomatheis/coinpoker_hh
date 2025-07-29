# Poker Hand History Analyzer

Comprehensive poker analysis tool that transforms CoinPoker hand history logs into detailed statistics, visualizations, and Excel reports. Now featuring a **web-based interface** for easy real-time analysis and tracking.

## Features

- **Web-Based Interface**: Modern browser-based UI for real-time analysis
- **Financial Tracking**: Precise profit/loss calculations with 99%+ accuracy
- **Multi-Player Analysis**: Analyze any player as the "hero" from the same hand history
- **Comprehensive Stats**: VPIP, PFR, aggression metrics, positional analysis, and more
- **Visual Reports**: Balance progression graphs and formatted Excel reports
- **Edge Case Handling**: All-ins, split pots, uncalled bets, side pots
- **Standalone Executables**: Run directly from the `dist/` folder without Python installation

## Quick Start

### Option 1: Use Pre-built Executables (Recommended)

**No Python installation required!** Simply run the executables from the `dist/` folder:

```bash
# Launch web-based tracker interface
./dist/run_web_tracker

# Run command-line analysis
./dist/run_analysis data/hand_log.txt [player_name]
```

After launching `run_web_tracker`, open your browser to `http://localhost:5000` to access the web interface.

### Option 2: Run from Source (Alternative)

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Launch Web Application
```bash
python3 run_web_tracker.py
```
Then open `http://localhost:5000` in your browser.

#### 3. Or Run Command-Line Analysis
```bash
# Analyze default player
python3 run_analysis.py data/hand_log.txt

# Analyze any other player
python3 run_analysis.py data/hand_log.txt GORILLAZ
python3 run_analysis.py data/hand_log.txt your_player_name
```

### Configuration (Optional)
Edit `config.py` to change the default player:
```python
DEFAULT_HERO_NAME = "your_preferred_player"
```

## Output Files

The analysis generates:
- **JSON files**: Detailed statistics and opponent data
- **PNG graph**: Balance progression over time
- **Excel report**: Multi-sheet comprehensive analysis

```
data/
├── {player}_hero_stats.json     # Player statistics
├── {player}_players_stats.json  # Opponent analysis  
├── {player}_balance_graph.png   # Balance chart
└── {player}_poker_stats.xlsx    # Excel report
```

## Requirements

### For Executables
- No requirements! Just run the executables in `dist/`

### For Source Code
- Python 3.7+
- pandas, openpyxl, matplotlib, numpy, flask (see requirements.txt)

## Individual Scripts (Advanced Users)

```bash
# Parse hand history (generates JSON)
python3 src/poker_hand_parser.py data/hand_log.txt

# Calculate metrics for specific player
python3 src/poker_metrics.py data/hand_log_parsed.json player_name --json

# Generate balance graph
python3 src/balance_graph.py data/hand_log_parsed.json player_name

# Create Excel report
python3 src/create_stats_excel.py data/player_hero_stats.json data/player_players_stats.json
```

## Supported Games

- ✅ Hold'em No Limit cash games
- ❌ Tournament hands (filtered out)
- ❌ PLO/Omaha hands (filtered out)

---

**Ready to analyze!** Use the web interface at `http://localhost:5000` after running `./dist/run_web_tracker` or place your hand history file in `data/` and run the analysis. 