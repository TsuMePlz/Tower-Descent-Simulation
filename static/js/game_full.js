// ============================================================================
// MHA ROGUELIKE - FULLY INTEGRATED FRONTEND
// ============================================================================

class FullMHAGame {
    constructor() {
        this.sessionId = null;
        this.gameState = null;
        
        // dom elements
        this.els = {
            startOverlay: document.getElementById('startOverlay'),
            startButton: document.getElementById('startButton'),
            continueButton: document.getElementById('continueButton'),
            tutorialButton: document.getElementById('tutorialButton'),
            tutorialOverlay: document.getElementById('tutorialOverlay'),
            closeTutorialButton: document.getElementById('closeTutorialButton'),
            imageArea: document.getElementById('imageArea'),
            displayImage: document.getElementById('displayImage'),
            imageOverlay: document.getElementById('imageOverlay'),
            zoneInfo: document.getElementById('zoneInfo'),
            enemyInfo: document.getElementById('enemyInfo'),
            enemyNameCombat: document.getElementById('enemyNameCombat'),
            enemyLevelCombat: document.getElementById('enemyLevelCombat'),
            enemyHpFillCombat: document.getElementById('enemyHpFillCombat'),
            enemyHpTextCombat: document.getElementById('enemyHpTextCombat'),
            textContent: document.getElementById('textContent'),
            textArea: document.getElementById('textArea'),
            statsBar: document.getElementById('statsBar'),
            userInput: document.getElementById('userInput'),
            submitButton: document.getElementById('submitButton'),
            inputPrompt: document.getElementById('inputPrompt'),
            progressText: document.getElementById('progressText'),
            studentsText: document.getElementById('studentsText'),
            charName: document.getElementById('charName'),
            charHpFill: document.getElementById('charHpFill'),
            charHpText: document.getElementById('charHpText'),
            charEnergyFill: document.getElementById('charEnergyFill'),
            charEnergyText: document.getElementById('charEnergyText'),
            inventoryCount: document.getElementById('inventoryCount'),
        };
        
        this.checkForSave();
        this.initEvents();
    }
    
    checkForSave() {
        const saveData = localStorage.getItem('mha_save');
        if (saveData) {
            this.els.continueButton.disabled = false;
            try {
                const save = JSON.parse(saveData);
                this.els.continueButton.textContent = `CONTINUE (Zone ${save.zone})`;
            } catch (e) {
                localStorage.removeItem('mha_save');
                this.els.continueButton.disabled = true;
                this.els.continueButton.textContent = 'CONTINUE';
            }
        }
    }
    
    initEvents() {
        this.els.startButton.addEventListener('click', () => this.startGame());
        this.els.continueButton.addEventListener('click', () => this.continueGame());
        this.els.tutorialButton.addEventListener('click', () => this.showTutorial());
        this.els.closeTutorialButton.addEventListener('click', () => this.hideTutorial());
        this.els.submitButton.addEventListener('click', () => this.sendInput());
        this.els.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendInput();
        });
    }
    
    showTutorial() {
        this.els.tutorialOverlay.style.display = 'flex';
    }
    
    hideTutorial() {
        this.els.tutorialOverlay.style.display = 'none';
    }
    
    async continueGame() {
        const saveData = localStorage.getItem('mha_save');
        if (!saveData) {
            alert('No save found!');
            return;
        }
        
        try {
            const save = JSON.parse(saveData);
            this.sessionId = save.sessionId;
            this.gameState = save.gameState;
            this.els.startOverlay.classList.add('hidden');
            this.updateUI(this.gameState);
            this.els.userInput.focus();
        } catch (e) {
            alert('Save corrupted!');
            localStorage.removeItem('mha_save');
            this.checkForSave();
        }
    }
    
    async startGame() {
        console.log('Starting game...');
        try {
            const response = await fetch('/api/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });
            
            const data = await response.json();
            console.log('Game started:', data);
            
            this.sessionId = data.session_id;
            this.updateUI(data.state);
            
            this.els.startOverlay.classList.add('hidden');
            this.els.userInput.focus();
        } catch (error) {
            console.error('Start error:', error);
            this.showError('Failed to start game: ' + error.message);
        }
    }
    
    async sendInput() {
        const input = this.els.userInput.value.trim();
        
        // Allow empty input for "continue" prompts (just pressing Enter)
        if (!this.sessionId) return;
        if (!input && this.gameState && this.gameState.pending_input !== 'continue') return;
        
        this.els.userInput.value = '';
        console.log('Sending input:', input || '[ENTER]');
        
        try {
            const response = await fetch('/api/input', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    session_id: this.sessionId,
                    input: input || 'continue'  // Send 'continue' if empty
                })
            });
            
            const data = await response.json();
            console.log('Response:', data);
            
            if (data.state) {
                this.updateUI(data.state);
            } else if (data.error) {
                this.showError(data.error);
            }
            
        } catch (error) {
            console.error('Input error:', error);
            this.showError('Connection error: ' + error.message);
        }
    }
    
    updateUI(state) {
        this.gameState = state;
        
        // Check if this is a new screen (game state changed)
        const isNewScreen = !this.lastGameState || this.lastGameState !== state.game_state;
        this.lastGameState = state.game_state;
        
        // Update messages
        this.clearText();
        if (state.messages && state.messages.length > 0) {
            state.messages.forEach(msg => {
                this.addMessage(msg.text, msg.type);
            });
            
            // Scroll behavior
            if (isNewScreen) {
                // New screen - scroll to top so user can read from beginning
                setTimeout(() => this.scrollToTop(), 50);
            } else {
                // Same screen with new text - only scroll down if needed
                setTimeout(() => this.smartScroll(), 50);
            }
        }
        
        // Update image
        this.updateImage(state);
        
        // Update stats
        this.updateStats(state);
        
        // Update progress
        this.updateProgress(state);
        
        // Update input prompt
        this.updatePrompt(state);
        
        // Scroll to bottom
        this.scrollToBottom();
        
        // Focus input
        this.els.userInput.focus();
    }
    
    updateImage(state) {
        console.log('=== updateImage DEBUG ===');
        console.log('Full state:', state);
        console.log('state.theme:', state.theme);
        console.log('state.in_combat:', state.in_combat);
        console.log('state.game_state:', state.game_state);
        console.log('state.zone:', state.zone);
        
        let imageSrc = '';
        let overlayText = '';
        
        if (state.in_combat && state.enemy) {
            // Show enemy image
            imageSrc = this.getEnemyImage(state.enemy.name);
            overlayText = `${state.enemy.name} - Level ${state.enemy.level}`;
            
            // Special handling for All For One - dramatic black screen
            if (state.enemy.name === 'All For One') {
                imageSrc = ''; // No image - pure black
                overlayText = '⚡ ALL FOR ONE ⚡';
            }
            
            // Show enemy info in overlay, hide zone info
            this.els.zoneInfo.classList.add('hidden');
            this.els.enemyInfo.classList.remove('hidden');
        } else if (state.theme === 'intro') {
            // Show placeholder during intro
            imageSrc = '/images/placeholder.png';
            overlayText = 'U.A. High School Training Exercise';
            
            // Show zone info
            this.els.zoneInfo.classList.remove('hidden');
            this.els.enemyInfo.classList.add('hidden');
            this.els.zoneInfo.textContent = overlayText;
        } else if (state.theme === 'char_select') {
            // Show placeholder during character selection
            imageSrc = '/images/placeholder.png';
            overlayText = `Zone ${state.zone} - Character Selection`;
            
            // Show zone info
            this.els.zoneInfo.classList.remove('hidden');
            this.els.enemyInfo.classList.add('hidden');
            this.els.zoneInfo.textContent = overlayText;
        } else if (state.theme === 'final_boss') {
            // Dramatic black screen for final boss intro
            imageSrc = '';
            overlayText = '⚡ FINAL FLOOR ⚡';
            
            // Show zone info
            this.els.zoneInfo.classList.remove('hidden');
            this.els.enemyInfo.classList.add('hidden');
            this.els.zoneInfo.textContent = overlayText;
        } else if (state.theme && state.theme !== 'intro' && state.theme !== 'char_select') {
            // Show zone background for actual zone themes
            imageSrc = `/images/zones/${state.theme}.png`;
            overlayText = `Zone ${state.zone} - ${this.formatTheme(state.theme)}`;
            
            console.log('Setting zone image:', imageSrc);
            console.log('Overlay text:', overlayText);
            
            // Show zone info
            this.els.zoneInfo.classList.remove('hidden');
            this.els.enemyInfo.classList.add('hidden');
            this.els.zoneInfo.textContent = overlayText;
        }
        
        console.log('Final imageSrc:', imageSrc);
        
        if (imageSrc) {
            // Clear previous error handlers
            this.els.displayImage.onerror = null;
            this.els.displayImage.onload = null;
            
            // Set new handlers
            this.els.displayImage.onerror = () => {
                console.warn('Image failed to load:', imageSrc);
                console.log('Attempting fallback to placeholder');
                // Only use placeholder as last resort
                this.els.displayImage.onerror = null; // Prevent infinite loop
                this.els.displayImage.src = '/images/placeholder.png';
            };
            this.els.displayImage.onload = () => {
                console.log('✓ Image loaded successfully:', imageSrc);
            };
            
            // Set the source - this will trigger load or error
            this.els.displayImage.src = imageSrc;
            this.els.displayImage.style.display = 'block';
        } else {
            // No image - pure black (for final boss)
            console.log('No image - black screen');
            this.els.displayImage.style.display = 'none';
        }
    }
    
    updateStats(state) {
        if (state.character) {
            const char = state.character;
            this.els.statsBar.classList.remove('hidden');
            this.els.statsBar.classList.add('visible');
            
            this.els.charName.textContent = char.name;
            
            const hpPct = (char.hp / char.max_hp) * 100;
            this.els.charHpFill.style.width = `${hpPct}%`;
            this.els.charHpText.textContent = `${char.hp}/${char.max_hp}`;
            
            const energyPct = (char.energy / char.max_energy) * 100;
            this.els.charEnergyFill.style.width = `${energyPct}%`;
            this.els.charEnergyText.textContent = `${char.energy}/${char.max_energy}`;
            
            // Update inventory count
            const itemCount = char.inventory ? char.inventory.length : 0;
            this.els.inventoryCount.textContent = `Items: ${itemCount}`;
        } else {
            this.els.statsBar.classList.add('hidden');
            this.els.statsBar.classList.remove('visible');
        }
        
        // Update enemy stats in bottom overlay
        if (state.in_combat && state.enemy) {
            const enemy = state.enemy;
            
            this.els.enemyNameCombat.textContent = enemy.name;
            this.els.enemyLevelCombat.textContent = `Level ${enemy.level}`;
            
            const enemyHpPct = (enemy.hp / enemy.max_hp) * 100;
            this.els.enemyHpFillCombat.style.width = `${enemyHpPct}%`;
            this.els.enemyHpTextCombat.textContent = `${enemy.hp}/${enemy.max_hp}`;
        }
        
        // auto save when at character selection between zones
        if (state.game_state === 'character_select' && state.zone > 0) {
            this.autoSave();
        }
    }
    
    autoSave() {
        try {
            const saveData = {
                sessionId: this.sessionId,
                gameState: this.gameState,
                zone: this.gameState.zone,
                timestamp: Date.now()
            };
            localStorage.setItem('mha_save', JSON.stringify(saveData));
            console.log('auto saved at zone', this.gameState.zone);
        } catch (e) {
            console.error('save failed:', e);
        }
    }
    
    updateProgress(state) {
        if (state.zone) {
            this.els.progressText.textContent = `Zone ${state.zone}/20`;
        }
        
        if (state.active_count !== undefined && state.total_count !== undefined) {
            this.els.studentsText.textContent = `Active: ${state.active_count}/${state.total_count}`;
        }
    }
    
    updatePrompt(state) {
        const prompts = {
            'intro': 'Press Enter to begin...',
            'ready': 'Press Enter to start Zone 1',
            'char_select': 'Select character (1-20):',
            'navigation': 'Enter direction or action:',
            'combat': 'Choose action (1, 2, 3):',
            'boss_warning': 'Enter (1) or Retreat (2):',
            'game_over': 'Game Over',
            'victory': 'Victory!'
        };
        
        const prompt = prompts[state.game_state] || 'Your input:';
        this.els.inputPrompt.textContent = prompt;
    }
    
    getEnemyImage(enemyName) {
        const nameMap = {
            'Villain Thug': 'villain_thug',
            'League Recruit': 'league_recruit',
            'Nomu': 'nomu',
            'Muscular': 'muscular',
            'Moonfish': 'moonfish',
            'Mustard': 'mustard',
            'Magne': 'magne',
            'Spinner': 'spinner',
            'Mr. Compress': 'mr_compress',
            'Twice': 'twice',
            'Dabi': 'dabi',
            'Himiko Toga': 'himiko_toga',
            'Gigantomachia': 'gigantomachia',
        };
        
        const fileName = nameMap[enemyName];
        if (!fileName) return '/images/placeholder.png';
        
        const bosses = ['muscular', 'moonfish', 'mustard', 'magne', 'spinner', 
                        'mr_compress', 'twice', 'dabi', 'himiko_toga', 'gigantomachia'];
        
        if (bosses.includes(fileName)) {
            return `/images/bosses/${fileName}.png`;
        } else {
            return `/images/enemies/${fileName}.png`;
        }
    }
    
    formatTheme(theme) {
        const names = {
            'forest': 'Forest Zone',
            'industrial': 'Industrial Complex',
            'flashfire': 'Flashfire Zone',
            'lake': 'Lake Zone',
            'blizzard': 'Blizzard Zone',
            'urban': 'Urban Ruins',
            'facility': 'Research Facility',
            'flooded': 'Flooded City',
            'mountain': 'Mountain Pass',
            'desert': 'Desert Wasteland',
            'ruins': 'Ancient Ruins',
            'underground': 'Underground Caverns',
        };
        return names[theme] || theme;
    }
    
    addMessage(text, type = 'normal') {
        const p = document.createElement('p');
        p.className = 'game-text';
        if (type && type !== 'normal') p.classList.add(type);
        
        // Bold character names and Aizawa
        text = this.boldNames(text);
        p.innerHTML = text;
        
        this.els.textContent.appendChild(p);
        p.classList.add('fade-in');
    }
    
    boldNames(text) {
        // Character names with their signature colors
        const characterColors = {
            'Izuku Midoriya': '#4CAF50',      // Green
            'Katsuki Bakugo': '#FF5722',      // Orange-Red
            'Shoto Todoroki': '#00FFFF',      // Cyan
            'Ochaco Uraraka': '#FFB3D9',      // Light Pink
            'Tenya Iida': '#0000FF',          // Blue
            'Tsuyu Asui': '#8BC34A',          // Light Green
            'Eijiro Kirishima': '#F44336',    // Red
            'Momo Yaoyorozu': '#FF0000',      // Red
            'Denki Kaminari': '#FFEB3B',      // Yellow
            'Fumikage Tokoyami': '#673AB7',   // Deep Purple
            'Shoji Mezo': '#795548',          // Brown
            'Mina Ashido': '#FF4081',         // Hot Pink
            'Kyoka Jiro': '#9C27B0',          // Purple
            'Hanta Sero': '#FFFF00',          // Yellow
            'Mashirao Ojiro': '#FFC107',      // Amber
            'Toru Hagakure': '#90EE90',       // Light Green
            'Koji Koda': '#FFFF99',           // Light Yellow
            'Rikido Sato': '#CC9900',         // Dark Yellow
            'Yuga Aoyama': '#ADD8E6',         // Light Blue
            'Minoru Mineta': '#7B1FA2',       // Dark Purple
            'Hitoshi Shinso': '#5E35B1',      // Indigo
        };
        
        // Zone type colors
        const zoneColors = {
            'FOREST': '#4CAF50',
            'FLASHFIRE': '#FF6600',
            'URBAN': '#9E9E9E',
            'LAKE': '#2196F3',
            'MOUNTAIN': '#795548',
            'BLIZZARD': '#00E5FF',
            'UNDERGROUND': '#5D4037'
        };
        
        // Bold and color each character name
        Object.entries(characterColors).forEach(([name, color]) => {
            const regex = new RegExp(`\\b${name}\\b`, 'g');
            text = text.replace(regex, `<strong style="color: ${color};">${name}</strong>`);
        });
        
        // Color zone names
        Object.entries(zoneColors).forEach(([zone, color]) => {
            const regex = new RegExp(`\\b${zone}\\b`, 'g');
            text = text.replace(regex, `<span style="color: ${color}; font-weight: bold;">${zone}</span>`);
        });
        
        // Bold Aizawa in white
        text = text.replace(/\[Aizawa\]:/g, '<strong style="color: #FFFFFF;">[Aizawa]:</strong>');
        text = text.replace(/\bAizawa\b/g, '<strong style="color: #FFFFFF;">Aizawa</strong>');
        
        return text;
    }
    
    clearText() {
        this.els.textContent.innerHTML = '';
    }
    
    scrollToBottom() {
        this.els.textArea.scrollTop = this.els.textArea.scrollHeight;
    }
    
    scrollToTop() {
        this.els.textArea.scrollTop = 0;
    }
    
    smartScroll() {
        // Only scroll down if all new content can be seen
        const textArea = this.els.textArea;
        const contentHeight = this.els.textContent.scrollHeight;
        const visibleHeight = textArea.clientHeight;
        const currentScroll = textArea.scrollTop;
        
        // If content fits in view, scroll to top
        if (contentHeight <= visibleHeight) {
            textArea.scrollTop = 0;
        } else {
            // If user was at bottom, keep at bottom
            const wasAtBottom = (currentScroll + visibleHeight) >= (textArea.scrollHeight - 50);
            if (wasAtBottom) {
                textArea.scrollTop = textArea.scrollHeight;
            }
            // Otherwise don't scroll - let user read where they are
        }
    }
    
    showError(message) {
        this.addMessage('ERROR: ' + message, 'warning');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.game = new FullMHAGame();
    console.log('MHA Roguelike - Fully Integrated Version Ready!');
});
