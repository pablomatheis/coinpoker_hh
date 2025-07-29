# Poker Hand History Analyzer

Comprehensive poker analysis tool that transforms CoinPoker hand history logs into detailed statistics, visualizations, and Excel reports.

## Features

- **Financial Tracking**: Precise profit/loss calculations with 99%+ accuracy
- **Multi-Player Analysis**: Analyze any player as the "hero" from the same hand history
- **Comprehensive Stats**: VPIP, PFR, aggression metrics, positional analysis, and more
- **Visual Reports**: Balance progression graphs and formatted Excel reports
- **Edge Case Handling**: All-ins, split pots, uncalled bets, side pots

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Analysis
```bash
# Analyze default player (pmatheis)
python3 run_analysis.py data/hand_log.txt

# Analyze any other player
python3 run_analysis.py data/hand_log.txt GORILLAZ
python3 run_analysis.py data/hand_log.txt your_player_name
```

### 3. Change Default Player (Optional)
Edit `config.py`:
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

- Python 3.7+
- pandas, openpyxl, matplotlib, numpy (see requirements.txt)

## Individual Scripts

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

**Ready to analyze!** Place your hand history file in `data/` and run the analysis. 