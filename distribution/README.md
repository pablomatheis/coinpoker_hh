# Poker Analysis Tools - Distribution Package

This package contains standalone executables for poker hand analysis and web-based tracking.

## 📦 Contents

### 🌐 Web Tracker (`poker_web_tracker/`)
- **Executable**: `poker_web_tracker`
- **Purpose**: Web-based interface for viewing poker statistics
- **Required Files**: `templates/`, `static/`, `data/` folders (included)

### 📊 Analysis Pipeline (`poker_analysis/`)
- **Executable**: `poker_analysis`
- **Purpose**: Command-line tool for analyzing poker hand logs
- **Sample Data**: `sample_data/hand_log.txt` (example input file)

## 🚀 Quick Start

### Web Tracker
1. Navigate to the `poker_web_tracker/` folder
2. Run: `./poker_web_tracker`
3. Open browser to: `http://localhost:8080`
4. Upload JSON stats files to view player data

### Analysis Pipeline
1. Navigate to the `poker_analysis/` folder
2. Run: `./poker_analysis <hand_log_file> [hero_name]`
3. Example: `./poker_analysis sample_data/hand_log.txt john_doe`

## 📋 System Requirements

- **macOS**: 10.15+ (Catalina or newer)
- **Architecture**: Apple Silicon (arm64) or Intel (x86_64)
- **Memory**: 1GB+ available RAM
- **Storage**: 1GB+ free space

## 🔧 Troubleshooting

### Web Tracker Issues
- **Port in use**: If port 8080 is busy, stop other services or modify the app
- **Missing templates**: Ensure `templates/` and `static/` folders are present
- **Permission denied**: Run `chmod +x poker_web_tracker`

### Analysis Issues
- **Slow startup**: First run may take time due to font cache building
- **Permission denied**: Run `chmod +x poker_analysis`
- **No output files**: Ensure write permissions in current directory

## 📊 Generated Files (Analysis)

When you run the analysis pipeline, it creates:
- `<filename>_parsed.json` - Structured hand data
- `data/<hero>_hero_stats.json` - Hero statistics
- `data/<hero>_players_stats.json` - Opponent statistics  
- `data/<hero>_balance_graph.png` - Balance progression graph
- `data/<hero>_poker_stats.xlsx` - Comprehensive Excel report

## 🌐 Web Interface Features

- **Player Search**: Find specific opponents quickly
- **Statistics View**: VPIP, PFR, aggression factors, and more
- **File Upload**: Load new analysis results via JSON upload
- **Responsive Design**: Works on desktop and mobile browsers

## 💡 Tips

1. **First Time**: The analysis executable may take 30+ seconds to start initially
2. **Large Files**: Analysis of 10,000+ hands may take several minutes
3. **Web Access**: The web tracker is accessible from other devices on your network
4. **Data Backup**: Copy generated JSON files to preserve analysis results

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all required files are present
3. Ensure executables have proper permissions

## 🔄 Version Info

- **Built**: $(date)
- **Python**: 3.12.3
- **PyInstaller**: 6.14.2
- **Platform**: macOS arm64