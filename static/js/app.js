/**
 * Poker Table Tracker - Web Application JavaScript
 * 
 * Handles dynamic player management, file uploads, stats display,
 * and real-time updates via Flask API.
 */

class PokerTableTracker {
    constructor() {
        this.players = [];
        this.heroStats = {};
        this.selectedPlayers = new Map(); // seatNumber -> playerName
        this.playerPanels = new Map(); // seatNumber -> panel element
        this.nextSeatNumber = 1;
        this.maxPlayers = 12;
        this.alwaysOnTop = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.addPlayer(); // Start with one player
        this.loadDefaultData();
    }
    
    setupEventListeners() {
        // Control buttons
        document.getElementById('addPlayerBtn').addEventListener('click', () => this.addPlayer());
        document.getElementById('loadDefaultBtn').addEventListener('click', () => this.loadDefaultData());
        document.getElementById('clearAllBtn').addEventListener('click', () => this.clearAllPlayers());
        document.getElementById('alwaysOnTopBtn').addEventListener('click', () => this.toggleAlwaysOnTop());
        
        // File uploads
        document.getElementById('playersFile').addEventListener('change', (e) => this.handlePlayersFileUpload(e));
        document.getElementById('heroFile').addEventListener('change', (e) => this.handleHeroFileUpload(e));
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => this.handleOutsideClick(e));
    }
    
    async addPlayer() {
        if (this.playerPanels.size >= this.maxPlayers) {
            this.showStatus(`Maximum ${this.maxPlayers} players allowed`, 'error');
            return;
        }
        
        const seatNumber = this.nextSeatNumber++;
        const panel = this.createPlayerPanel(seatNumber);
        
        this.playerPanels.set(seatNumber, panel);
        
        // Add to grid with animation
        const playersGrid = document.getElementById('playersGrid');
        panel.classList.add('fade-in');
        playersGrid.appendChild(panel);
        
        this.showStatus(`Added Player ${seatNumber} - ${this.playerPanels.size} players active`);
    }
    
    createPlayerPanel(seatNumber) {
        const template = document.getElementById('playerPanelTemplate');
        const panel = template.content.cloneNode(true).querySelector('.player-panel');
        
        // Set seat number
        panel.dataset.seatNumber = seatNumber;
        panel.querySelector('.player-title').textContent = `Player ${seatNumber}`;
        
        // Setup player input and dropdown
        const playerInput = panel.querySelector('.player-input');
        const playerDropdown = panel.querySelector('.player-dropdown');
        
        playerInput.addEventListener('input', (e) => this.handlePlayerInput(e, seatNumber));
        playerInput.addEventListener('focus', () => this.showPlayerDropdown(seatNumber));
        playerInput.addEventListener('keydown', (e) => this.handlePlayerInputKeydown(e, seatNumber));
        
        // Setup control buttons
        panel.querySelector('.clear-btn').addEventListener('click', () => this.clearPlayer(seatNumber));
        
        const removeBtn = panel.querySelector('.remove-btn');
        if (seatNumber > 1) {
            removeBtn.style.display = 'block';
            removeBtn.addEventListener('click', () => this.removePlayer(seatNumber));
        }
        
        // Populate dropdown if we have players
        if (this.players.length > 0) {
            this.updatePlayerDropdown(seatNumber, '');
        }
        
        return panel;
    }
    
    removePlayer(seatNumber) {
        const panel = this.playerPanels.get(seatNumber);
        if (panel) {
            // Clear selection
            this.selectedPlayers.delete(seatNumber);
            
            // Remove panel with animation
            panel.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => {
                panel.remove();
            }, 300);
            
            this.playerPanels.delete(seatNumber);
            this.showStatus(`Removed Player ${seatNumber} - ${this.playerPanels.size} players active`);
        }
    }
    
    handlePlayerInput(event, seatNumber) {
        const query = event.target.value.toLowerCase();
        this.updatePlayerDropdown(seatNumber, query);
        
        if (query === '') {
            this.clearPlayerStats(seatNumber);
            this.selectedPlayers.delete(seatNumber);
        }
    }
    
    handlePlayerInputKeydown(event, seatNumber) {
        const dropdown = this.getPlayerDropdown(seatNumber);
        const items = dropdown.querySelectorAll('.dropdown-item');
        const currentSelected = dropdown.querySelector('.dropdown-item.selected');
        
        let selectedIndex = -1;
        if (currentSelected) {
            selectedIndex = Array.from(items).indexOf(currentSelected);
        }
        
        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
                this.updateDropdownSelection(dropdown, selectedIndex);
                break;
                
            case 'ArrowUp':
                event.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, 0);
                this.updateDropdownSelection(dropdown, selectedIndex);
                break;
                
            case 'Enter':
                event.preventDefault();
                if (currentSelected) {
                    this.selectPlayer(seatNumber, currentSelected.textContent);
                }
                break;
                
            case 'Escape':
                this.hidePlayerDropdown(seatNumber);
                break;
        }
    }
    
    updateDropdownSelection(dropdown, selectedIndex) {
        const items = dropdown.querySelectorAll('.dropdown-item');
        items.forEach((item, index) => {
            item.classList.toggle('selected', index === selectedIndex);
        });
    }
    
    updatePlayerDropdown(seatNumber, query) {
        const dropdown = this.getPlayerDropdown(seatNumber);
        
        let filteredPlayers = this.players;
        
        if (query) {
            // Filter players - prioritize those that start with query
            const startsWithQuery = this.players.filter(p => p.toLowerCase().startsWith(query));
            const containsQuery = this.players.filter(p => 
                p.toLowerCase().includes(query) && !p.toLowerCase().startsWith(query)
            );
            filteredPlayers = [...startsWithQuery, ...containsQuery];
        }
        
        dropdown.innerHTML = '';
        
        filteredPlayers.forEach(player => {
            const item = document.createElement('div');
            item.className = 'dropdown-item';
            item.textContent = player;
            item.addEventListener('click', () => this.selectPlayer(seatNumber, player));
            dropdown.appendChild(item);
        });
        
        if (filteredPlayers.length > 0 && query) {
            this.showPlayerDropdown(seatNumber);
        } else if (filteredPlayers.length === 0) {
            this.hidePlayerDropdown(seatNumber);
        }
    }
    
    showPlayerDropdown(seatNumber) {
        const dropdown = this.getPlayerDropdown(seatNumber);
        dropdown.style.display = 'block';
    }
    
    hidePlayerDropdown(seatNumber) {
        const dropdown = this.getPlayerDropdown(seatNumber);
        dropdown.style.display = 'none';
    }
    
    getPlayerDropdown(seatNumber) {
        const panel = this.playerPanels.get(seatNumber);
        return panel.querySelector('.player-dropdown');
    }
    
    getPlayerInput(seatNumber) {
        const panel = this.playerPanels.get(seatNumber);
        return panel.querySelector('.player-input');
    }
    
    async selectPlayer(seatNumber, playerName) {
        // Check if player is already selected elsewhere
        for (const [seat, name] of this.selectedPlayers) {
            if (name === playerName && seat !== seatNumber) {
                this.showStatus(`${playerName} is already selected in Player ${seat}`, 'error');
                this.clearPlayer(seatNumber);
                return;
            }
        }
        
        // Update input and hide dropdown
        const input = this.getPlayerInput(seatNumber);
        input.value = playerName;
        this.hidePlayerDropdown(seatNumber);
        
        // Update selection
        this.selectedPlayers.set(seatNumber, playerName);
        
        // Load and display player stats
        try {
            const response = await fetch(`/api/player/${encodeURIComponent(playerName)}`);
            const data = await response.json();
            
            if (response.ok) {
                this.updatePlayerStats(seatNumber, data.stats);
                const hands = data.stats.hands_against_hero || 0;
                this.showStatus(`Selected ${playerName} (${hands.toLocaleString()} hands)`);
            } else {
                this.showStatus(`No data found for ${playerName}`, 'error');
                this.clearPlayerStats(seatNumber);
            }
        } catch (error) {
            this.showStatus(`Error loading player data: ${error.message}`, 'error');
            this.clearPlayerStats(seatNumber);
        }
    }
    
    updatePlayerStats(seatNumber, stats) {
        const panel = this.playerPanels.get(seatNumber);
        const statValues = panel.querySelectorAll('.stat-value');
        
        statValues.forEach(element => {
            const statKey = element.dataset.stat;
            
            if (stats && statKey in stats) {
                const value = stats[statKey];
                const { text, color } = this.formatStatValue(statKey, value);
                
                element.textContent = text;
                element.className = `stat-value stat-${color}`;
            } else {
                element.textContent = '--';
                element.className = 'stat-value stat-black';
            }
        });
    }
    
    formatStatValue(key, value) {
        let text, color;
        
        switch (key) {
            case 'hands_against_hero':
                text = value.toLocaleString();
                color = value >= 50 ? 'green' : value >= 20 ? 'orange' : 'red';
                break;
                
            case 'vpip_percentage':
                text = `${value.toFixed(1)}%`;
                color = value < 16 ? 'blue' : value <= 28 ? 'green' : 'red';
                break;
                
            case 'pfr_percentage':
                text = `${value.toFixed(1)}%`;
                color = value < 14 ? 'blue' : value <= 25 ? 'green' : 'red';
                break;
                
            case 'three_bet_percentage':
                text = `${value.toFixed(1)}%`;
                color = value < 4 ? 'blue' : value <= 8 ? 'green' : 'red';
                break;
                
            case 'cbet_percentage':
                text = `${value.toFixed(1)}%`;
                color = value < 50 ? 'blue' : value <= 75 ? 'green' : 'red';
                break;
                
            case 'went_to_showdown_percentage':
                text = `${value.toFixed(1)}%`;
                color = value < 20 ? 'blue' : value <= 30 ? 'green' : 'red';
                break;
                
            case 'won_at_showdown_percentage':
                text = `${value.toFixed(1)}%`;
                color = value < 45 ? 'blue' : value <= 65 ? 'green' : 'red';
                break;
                
            case 'fold_vs_flop_bet_percentage':
                text = `${value.toFixed(1)}%`;
                color = value < 40 ? 'blue' : value <= 60 ? 'green' : 'red';
                break;
                
            case 'fold_vs_turn_bet_percentage':
                text = `${value.toFixed(1)}%`;
                color = value < 35 ? 'blue' : value <= 55 ? 'green' : 'red';
                break;
                
            case 'fold_vs_river_bet_percentage':
                text = `${value.toFixed(1)}%`;
                color = value < 30 ? 'blue' : value <= 50 ? 'green' : 'red';
                break;
                
            case 'turn_cbet_percentage':
                text = `${value.toFixed(1)}%`;
                color = value < 35 ? 'blue' : value <= 65 ? 'green' : 'red';
                break;
                
            case 'river_cbet_percentage':
                text = `${value.toFixed(1)}%`;
                color = value < 30 ? 'blue' : value <= 60 ? 'green' : 'red';
                break;
                
            case 'donk_bet_percentage':
                text = `${value.toFixed(1)}%`;
                color = value > 15 ? 'red' : value <= 5 ? 'green' : 'orange';
                break;
                
            case 'afq_percentage':
                text = `${value.toFixed(1)}%`;
                color = value < 50 ? 'blue' : value <= 70 ? 'green' : 'red';
                break;
                
            case 'aggression_factor':
                text = value.toFixed(2);
                color = value > 1.0 ? 'green' : value > 0.5 ? 'orange' : 'red';
                break;
                
            case 'hero_net_vs_player':
                text = `$${value.toFixed(2)}`;
                color = value > 0 ? 'green' : value < 0 ? 'red' : 'black';
                break;
                
            default:
                text = value.toString();
                color = 'black';
        }
        
        return { text, color };
    }
    
    clearPlayer(seatNumber) {
        const input = this.getPlayerInput(seatNumber);
        input.value = '';
        this.hidePlayerDropdown(seatNumber);
        this.selectedPlayers.delete(seatNumber);
        this.clearPlayerStats(seatNumber);
    }
    
    clearPlayerStats(seatNumber) {
        const panel = this.playerPanels.get(seatNumber);
        const statValues = panel.querySelectorAll('.stat-value');
        
        statValues.forEach(element => {
            element.textContent = '--';
            element.className = 'stat-value stat-black';
        });
    }
    
    clearAllPlayers() {
        this.playerPanels.forEach((panel, seatNumber) => {
            this.clearPlayer(seatNumber);
        });
        this.showStatus('All players cleared');
    }
    
    async handlePlayersFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            this.showStatus('Loading players stats...', 'loading');
            
            const response = await fetch('/api/load_players', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.players = data.players;
                this.updateAllPlayerDropdowns();
                this.showStatus(data.message);
            } else {
                this.showStatus(data.error, 'error');
            }
        } catch (error) {
            this.showStatus(`Error uploading file: ${error.message}`, 'error');
        }
        
        // Reset file input
        event.target.value = '';
    }
    
    async handleHeroFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            this.showStatus('Loading hero stats...', 'loading');
            
            const response = await fetch('/api/load_hero', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.heroStats = data.hero_stats;
                this.updateHeroStats();
                this.showStatus(data.message);
            } else {
                this.showStatus(data.error, 'error');
            }
        } catch (error) {
            this.showStatus(`Error uploading file: ${error.message}`, 'error');
        }
        
        // Reset file input
        event.target.value = '';
    }
    
    async loadDefaultData() {
        try {
            this.showStatus('Loading default data...', 'loading');
            
            const response = await fetch('/api/load_default', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.players = data.players || [];
                this.heroStats = data.hero_stats || {};
                this.updateAllPlayerDropdowns();
                this.updateHeroStats();
                this.showStatus(data.message);
            } else {
                this.showStatus(data.error, 'error');
            }
        } catch (error) {
            this.showStatus(`Error loading default data: ${error.message}`, 'error');
        }
    }
    
    updateAllPlayerDropdowns() {
        this.playerPanels.forEach((panel, seatNumber) => {
            const input = this.getPlayerInput(seatNumber);
            this.updatePlayerDropdown(seatNumber, input.value.toLowerCase());
        });
    }
    
    updateHeroStats() {
        const heroElements = {
            'total_hands_played': 'heroHands',
            'net_result': 'heroNet',
            'roi_percentage': 'heroROI',
            'vpip_percentage': 'heroVPIP',
            'pfr_percentage': 'heroPFR',
            'three_bet_percentage': 'heroThreeBet',
            'aggression_factor': 'heroAggFactor'
        };
        
        for (const [statKey, elementId] of Object.entries(heroElements)) {
            const element = document.getElementById(elementId);
            
            if (this.heroStats && statKey in this.heroStats) {
                const value = this.heroStats[statKey];
                let text, color = '';
                
                switch (statKey) {
                    case 'total_hands_played':
                        text = value.toLocaleString();
                        break;
                    case 'net_result':
                        text = `$${value.toFixed(2)}`;
                        color = value > 0 ? 'green' : value < 0 ? 'red' : 'black';
                        break;
                    case 'roi_percentage':
                    case 'vpip_percentage':
                    case 'pfr_percentage':
                    case 'three_bet_percentage':
                        text = `${value.toFixed(1)}%`;
                        break;
                    case 'aggression_factor':
                        text = value.toFixed(2);
                        break;
                    default:
                        text = value.toString();
                }
                
                element.textContent = text;
                if (color) {
                    element.style.color = color === 'green' ? '#28a745' : color === 'red' ? '#dc3545' : '#333';
                }
            } else {
                element.textContent = '--';
                element.style.color = '#333';
            }
        }
    }
    
    toggleAlwaysOnTop() {
        // Note: This is limited in web browsers for security reasons
        // Most browsers don't allow websites to control window layering
        this.alwaysOnTop = !this.alwaysOnTop;
        
        if (this.alwaysOnTop) {
            // Try to request fullscreen as an alternative
            if (document.documentElement.requestFullscreen) {
                document.documentElement.requestFullscreen().catch(() => {
                    this.showStatus('Always on top not supported in this browser', 'error');
                });
            } else {
                this.showStatus('Always on top not supported in this browser', 'error');
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
        
        this.showStatus(`Always on top: ${this.alwaysOnTop ? 'ON' : 'OFF'}`);
    }
    
    handleOutsideClick(event) {
        // Close all dropdowns if clicking outside
        if (!event.target.closest('.player-selector')) {
            this.playerPanels.forEach((panel, seatNumber) => {
                this.hidePlayerDropdown(seatNumber);
            });
        }
    }
    
    showStatus(message, type = 'info') {
        const statusText = document.getElementById('statusText');
        statusText.textContent = message;
        
        // Reset classes
        statusText.className = '';
        
        // Add type-specific styling
        switch (type) {
            case 'error':
                statusText.style.color = '#dc3545';
                break;
            case 'loading':
                statusText.style.color = '#007bff';
                break;
            default:
                statusText.style.color = '#666';
        }
        
        // Auto-clear status after 5 seconds for non-error messages
        if (type !== 'error') {
            setTimeout(() => {
                if (statusText.textContent === message) {
                    statusText.textContent = 'Ready';
                    statusText.style.color = '#666';
                }
            }, 5000);
        }
    }
}

// Add CSS animation for fadeOut
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: scale(1); }
        to { opacity: 0; transform: scale(0.9); }
    }
`;
document.head.appendChild(style);

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.pokerTracker = new PokerTableTracker();
}); 