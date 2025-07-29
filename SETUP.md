# Quick Setup Guide

## Prerequisites
- **Python 3.7+** (required for dataclasses support)
- pip (Python package installer)

## Installation

### 1. Clone or Download Project
```bash
# If using git
git clone <your-repo-url>
cd coinpoker_hh

# Or download and extract the project files
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- `pandas` - Data manipulation and analysis
- `openpyxl` - Excel file creation and formatting
- `matplotlib` - Plotting and visualization
- `numpy` - Numerical computing

### 3. Verify Installation
```bash
python3 -c "import pandas, openpyxl, matplotlib, numpy; print('✅ All packages installed successfully!')"
```

## Quick Start

### Analyze Your Default Player (pmatheis)
```bash
python3 run_analysis.py data/hand_log.txt
```

### Analyze Any Other Player
```bash
python3 run_analysis.py data/hand_log.txt GORILLAZ
python3 run_analysis.py data/hand_log.txt your_player_name
```

### Change Default Player
Edit `config.py`:
```python
DEFAULT_HERO_NAME = "your_preferred_player"
```

## Output Files
The analysis generates:
- `data/{player}_hero_stats.json` - Player statistics
- `data/{player}_players_stats.json` - Opponent analysis
- `data/{player}_balance_graph.png` - Balance progression chart
- `data/{player}_poker_stats.xlsx` - Comprehensive Excel report

## Troubleshooting

### Python Version Issues
```bash
# Check Python version (must be 3.7+)
python3 --version

# If too old, install newer Python version
```

### Missing Packages
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt

# Or install individually
pip install pandas openpyxl matplotlib numpy
```

### Import Errors
```bash
# Make sure you're in the project root directory
cd /path/to/coinpoker_hh

# Run from root directory
python3 run_analysis.py data/hand_log.txt
```

## File Structure
```
coinpoker_hh/
├── config.py                    # Configuration settings
├── run_analysis.py              # Main pipeline script  
├── requirements.txt             # Python dependencies
├── src/                         # Source code
│   ├── poker_hand_parser.py
│   ├── poker_metrics.py
│   ├── balance_graph.py
│   └── create_stats_excel.py
└── data/                        # Input/output files
    ├── hand_log.txt            # Your raw hand history
    └── [generated files]       # Analysis outputs
```

## Ready to Analyze!
Once setup is complete, you can analyze any player's poker performance with a single command! 