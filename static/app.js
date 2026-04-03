
class SceneUI {
    constructor() {
        this.sceneId = null;
        this.ws = null;
        this.isSceneRunning = false;
        this.maxTurns = 30;
        this.minTurns = 6;
        this.currentTurn = 0;
        this.dialogueHistory = [];
        this.currentTemplate = null;
        this.characterColors = [];
        
        // Color palette for dynamic character assignment
        this.colorPalette = [
            { name: 'steel-blue', hex: '#81c1d9', rgb: '129, 193, 217' },
            { name: 'rose', hex: '#e9a5a5', rgb: '233, 165, 165' },
            { name: 'gold', hex: '#ffd700', rgb: '255, 215, 0' },
            { name: 'coral', hex: '#ff6b6b', rgb: '255, 107, 107' },
            { name: 'purple', hex: '#aa96da', rgb: '170, 150, 218' },
            { name: 'orange', hex: '#ffb347', rgb: '255, 179, 71' },
            { name: 'pink', hex: '#ff69b4', rgb: '255, 105, 180' },
            { name: 'teal', hex: '#20b2aa', rgb: '32, 178, 170' }
        ];

        this.setupEventListeners();
        this.fetchTemplates();
    }

    setupEventListeners() {
        // Landing page buttons
        document.getElementById('defaultSceneBtn').addEventListener('click', () => this.handleDefaultSceneChoice());
        document.getElementById('customSceneBtn').addEventListener('click', () => this.handleCustomSceneChoice());
        
        // Setup form
        document.getElementById('sceneForm').addEventListener('submit', (e) => this.handleFormSubmit(e));
        document.getElementById('backBtn').addEventListener('click', () => this.backToLanding());
        
        // Character constitution counters
        document.getElementById('char1Constitution').addEventListener('input', (e) => this.updateCharCounter(e, 'char1Constitution'));
        document.getElementById('char2Constitution').addEventListener('input', (e) => this.updateCharCounter(e, 'char2Constitution'));
        
        // Scene controls
        document.getElementById('stopBtn').addEventListener('click', () => this.stopScene());
        document.getElementById('resetBtn').addEventListener('click', () => this.resetUI());
    }

    async fetchTemplates() {
        try {
            const response = await fetch('/api/templates');
            const data = await response.json();
            console.log('Templates fetched:', data);
        } catch (error) {
            console.error('Error fetching templates:', error);
        }
    }

    handleDefaultSceneChoice() {
        console.log('User chose: Use default scene');
        // Hide landing panel
        document.getElementById('landingPanel').classList.remove('panel-active');
        
        // Load default scene and prepare for immediate start
        this.loadDefaultScene();
    }

    handleCustomSceneChoice() {
        console.log('User chose: Build custom scene');
        // Hide landing panel, show setup panel
        document.getElementById('landingPanel').classList.remove('panel-active');
        document.getElementById('setupPanel').classList.add('panel-active');
    }

    backToLanding() {
        // Hide setup panel, show landing panel
        document.getElementById('setupPanel').classList.remove('panel-active');
        document.getElementById('landingPanel').classList.add('panel-active');
    }

    async loadDefaultScene() {
        try {
            const response = await fetch('/api/templates/default');
            if (!response.ok) throw new Error('Failed to load default scene');
            
            const defaultScene = await response.json();
            this.currentTemplate = defaultScene;
            
            // Pre-populate form (read-only view)
            document.getElementById('sceneTitle').value = defaultScene.title;
            document.getElementById('genre').value = defaultScene.genre;
            document.getElementById('sceneContext').value = defaultScene.scene_context;
            document.getElementById('maxTurns').value = defaultScene.max_turns;
            document.getElementById('minTurns').value = defaultScene.min_turns;
            
            // Populate characters
            if (defaultScene.characters && defaultScene.characters.length >= 2) {
                document.getElementById('char1Name').value = defaultScene.characters[0].name;
                document.getElementById('char1Desc').value = defaultScene.characters[0].description;
                document.getElementById('char1Constitution').value = defaultScene.characters[0].constitution;
                this.updateCharCounter({ target: document.getElementById('char1Constitution') }, 'char1Constitution');
                
                document.getElementById('char2Name').value = defaultScene.characters[1].name;
                document.getElementById('char2Desc').value = defaultScene.characters[1].description;
                document.getElementById('char2Constitution').value = defaultScene.characters[1].constitution;
                this.updateCharCounter({ target: document.getElementById('char2Constitution') }, 'char2Constitution');
            }
            
            // Show setup panel (read-only)
            document.getElementById('setupPanel').classList.add('panel-active');
            
            // Make form fields read-only to indicate default scene
            this.setFormReadOnly(true);
            
        } catch (error) {
            console.error('Error loading default scene:', error);
            alert('Error loading default scene: ' + error.message);
            // Go back to landing if loading fails
            document.getElementById('landingPanel').classList.add('panel-active');
        }
    }

    setFormReadOnly(readOnly) {
        const formInputs = document.querySelectorAll('#sceneForm input, #sceneForm textarea, #sceneForm select');
        formInputs.forEach(input => {
            input.readOnly = readOnly;
            input.disabled = readOnly;
            if (readOnly) {
                input.classList.add('disabled-field');
            } else {
                input.classList.remove('disabled-field');
            }
        });
        
        // Back button should still be enabled
        document.getElementById('backBtn').disabled = false;
    }

    updateCharCounter(event, fieldId) {
        const textarea = event.target;
        const length = textarea.value.length;
        const limit = textarea.maxLength;
        const label = document.querySelector(`label[for="${fieldId}"] .char-limit`);
        if (label) {
            label.textContent = `(${length}/${limit})`;
        }
    }

    assignCharacterColors(characters) {
        // Assign colors sequentially from the palette
        this.characterColors = {};
        characters.forEach((char, index) => {
            if (index < this.colorPalette.length) {
                this.characterColors[char.name] = this.colorPalette[index];
            }
        });
        return this.characterColors;
    }

    async handleFormSubmit(e) {
        e.preventDefault();

        const title = document.getElementById('sceneTitle').value;
        const genre = document.getElementById('genre').value;
        const context = document.getElementById('sceneContext').value;
        const maxTurns = parseInt(document.getElementById('maxTurns').value);
        const minTurns = parseInt(document.getElementById('minTurns').value);

        this.maxTurns = maxTurns;
        this.minTurns = minTurns;
        this.dialogueHistory = []; // Reset history for new scene

        // Collect character data from form
        const characters = [
            {
                name: document.getElementById('char1Name').value,
                description: document.getElementById('char1Desc').value,
                constitution: document.getElementById('char1Constitution').value
            },
            {
                name: document.getElementById('char2Name').value,
                description: document.getElementById('char2Desc').value,
                constitution: document.getElementById('char2Constitution').value
            }
        ];

        // Assign colors to characters
        this.assignCharacterColors(characters);

        // Create scene configuration
        let config;

        if (this.currentTemplate && Object.keys(this.currentTemplate).length > 0) {
            // Use template as base, but allow overrides from form
            config = {
                ...this.currentTemplate,
                title: title,
                genre: genre,
                scene_context: context,
                max_turns: maxTurns,
                min_turns: minTurns,
                characters: characters
            };
        } else {
            // Custom scene configuration
            config = {
                title: title,
                genre: genre,
                scene_context: context,
                max_turns: maxTurns,
                min_turns: minTurns,
                characters: characters,
                // Note: director_system_prompt is now optional and will be auto-generated
                llm_model: "gemma3:4b",
                llm_server: "http://localhost:11434"
            };
        }

        try {
            const response = await fetch('/api/scenes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });

            if (!response.ok) throw new Error('Failed to create scene');

            const data = await response.json();
            this.sceneId = data.scene_id;

            // Switch to scene panel
            document.getElementById('setupPanel').classList.remove('panel-active');
            document.getElementById('scenePanel').classList.add('panel-active');

            // Update scene display
            document.getElementById('sceneTitle2').textContent = title;
            document.getElementById('genreDisplay').textContent = `Genre: ${genre.replace('_', ' ').toUpperCase()}`;
            document.getElementById('turnCount').textContent = '1';

            // Connect WebSocket
            this.connectWebSocket();

        } catch (error) {
            console.error('Error creating scene:', error);
            alert('Error creating scene: ' + error.message);
        }
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const url = `${protocol}//${window.location.host}/ws/scene/${this.sceneId}`;

        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.isSceneRunning = true;
            document.getElementById('stopBtn').disabled = false;
            this.sendMessage({ type: 'start' });
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            alert('Connection error');
        };

        this.ws.onclose = () => {
            console.log('WebSocket closed');
            this.isSceneRunning = false;
            document.getElementById('stopBtn').disabled = true;
        };
    }

    handleMessage(message) {
        const type = message.type;

        if (type === 'connected') {
            console.log('Connected to scene:', message.scene_id);
            // Don't clear here, handleTurn will manage the "waiting" message
        }

        else if (type === 'turn') {
            this.handleTurn(message);
        }

        else if (type === 'scene_end') {
            this.handleSceneEnd(message);
        }

        else if (type === 'error') {
            this.handleError(message);
        }
    }

    handleTurn(message) {
        // Clear "waiting" message on the very first turn arriving
        const dialogueContent = document.getElementById('dialogueContent');
        if (this.dialogueHistory.length === 0) {
            dialogueContent.innerHTML = '';
        }

        this.currentTurn = message.turn_number;

        // Update scene info
        document.getElementById('turnCount').textContent = message.turn_number;

        const directorState = message.director_state;
        document.getElementById('arcStage').textContent = directorState.emotional_arc || '\u2014';
        document.getElementById('endingType').textContent = directorState.ending_type || '\u2014';

        // Update progress
        const progress = (this.currentTurn / this.maxTurns) * 100;
        document.getElementById('progressFill').style.width = `${progress}%`;

        // Add to history
        const turnData = {
            character: message.character,
            dialogue: message.dialogue,
            turn: message.turn_number
        };
        this.dialogueHistory.push(turnData);

        // Add dialogue entry UI with dynamic character colors
        const entry = document.createElement('div');
        const charClass = `character-${message.character.toLowerCase().replace(/\s+/g, '-')}`;
        entry.className = `dialogue-entry ${charClass}`;
        
        // Apply dynamic color if available
        const charColor = this.characterColors[message.character];
        if (charColor) {
            entry.style.setProperty('--char-color', charColor.hex);
            entry.style.setProperty('--char-color-rgb', charColor.rgb);
            entry.style.borderLeftColor = charColor.hex;
            entry.style.background = `rgba(${charColor.rgb}, 0.02)`;
        }
        
        entry.innerHTML = `
            <div class="character-name" style="color: ${charColor ? charColor.hex : ''}">${message.character}</div>
            <div class="dialogue-text">${this.escapeHtml(message.dialogue)}</div>
        `;
        dialogueContent.appendChild(entry);

        // Scroll to bottom
        setTimeout(() => {
            const dialogueBox = document.getElementById('dialogueBox');
            dialogueBox.scrollTop = dialogueBox.scrollHeight;
        }, 50);

        // Update stage directions
        if (message.stage_direction) {
            document.getElementById('stageDirections').classList.remove('hidden');
            document.getElementById('directionText').textContent = message.stage_direction;
        } else {
            document.getElementById('stageDirections').classList.add('hidden');
        }

        // Update threads
        this.updateThreads(directorState.unresolved_threads, directorState.resolved_threads);
    }

    handleSceneEnd(message) {
        this.isSceneRunning = false;
        document.getElementById('stopBtn').disabled = true;

        const completionMsg = document.getElementById('completionMessage');
        completionMsg.classList.remove('hidden');

        let text = `<strong>Scene Completed</strong><br>`;
        text += `Total Turns: ${message.total_turns}<br>`;
        if (message.ending_type) text += `Ending Type: ${message.ending_type}<br>`;
        text += `${message.completion_reason}`;

        document.getElementById('completionText').innerHTML = text;

        // Add completion message to dialogue
        const entry = document.createElement('div');
        entry.className = 'dialogue-entry';
        entry.innerHTML = `<div class="info-message">${message.completion_reason}</div>`;
        document.getElementById('dialogueContent').appendChild(entry);
    }

    handleError(message) {
        const entry = document.createElement('div');
        entry.className = 'dialogue-entry';
        entry.innerHTML = `<div class="info-message" style="color: #ff6b6b;">ERROR: ${this.escapeHtml(message.message)}</div>`;
        document.getElementById('dialogueContent').appendChild(entry);
    }

    updateThreads(unresolved, resolved) {
        const unresolvedList = document.getElementById('unresolvedThreads');
        unresolvedList.innerHTML = '';
        unresolved.forEach(thread => {
            const li = document.createElement('li');
            li.textContent = thread;
            unresolvedList.appendChild(li);
        });

        const resolvedList = document.getElementById('resolvedThreads');
        resolvedList.classList.add('resolved');
        resolvedList.innerHTML = '';
        resolved.forEach(thread => {
            const li = document.createElement('li');
            li.textContent = thread;
            resolvedList.appendChild(li);
        });
    }

    stopScene() {
        if (this.sceneId) {
            // Use REST endpoint to stop (doesn't depend on WebSocket connection)
            fetch(`/api/scenes/${this.sceneId}/stop`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(() => console.log("Stop request sent to backend"))
            .catch(error => console.error("Error stopping scene:", error));
        }
        if (this.ws) {
            this.ws.close();
        }
        this.isSceneRunning = false;
    }

    resetUI() {
        location.reload();
    }

    sendMessage(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
}

// Initialize UI when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.sceneUI = new SceneUI();
});
