
class SceneUI {
    constructor() {
        this.sceneId = null;
        this.ws = null;
        this.isSceneRunning = false;
        this.maxTurns = 30;
        this.currentTurn = 0;
        this.dialogueHistory = [];
        this.currentTemplate = null;

        this.setupEventListeners();
        this.fetchTemplates();
    }

    setupEventListeners() {
        document.getElementById('templateSelect').addEventListener('change', (e) => this.handleTemplateChange(e));
        document.getElementById('sceneForm').addEventListener('submit', (e) => this.handleFormSubmit(e));
        document.getElementById('stopBtn').addEventListener('click', () => this.stopScene());
        document.getElementById('resetBtn').addEventListener('click', () => this.resetUI());
    }

    async fetchTemplates() {
        try {
            const response = await fetch('/api/templates');
            const data = await response.json();
            const select = document.getElementById('templateSelect');

            data.templates.forEach(templateId => {
                const option = document.createElement('option');
                option.value = templateId;
                option.textContent = templateId.charAt(0).toUpperCase() + templateId.slice(1);
                select.appendChild(option);
            });

            // If "confession" is available, select it by default
            if (data.templates.includes('confession')) {
                select.value = 'confession';
                this.loadTemplate('confession');
            }
        } catch (error) {
            console.error('Error fetching templates:', error);
        }
    }

    async handleTemplateChange(e) {
        const templateId = e.target.value;
        if (templateId === 'custom') {
            this.currentTemplate = null;
            return;
        }
        await this.loadTemplate(templateId);
    }

    async loadTemplate(templateId) {
        try {
            const response = await fetch(`/api/templates/${templateId}`);
            const template = await response.json();
            this.currentTemplate = template;

            // Populate form
            document.getElementById('sceneTitle').value = template.title;
            document.getElementById('genre').value = template.genre;
            document.getElementById('sceneContext').value = template.scene_context;
            document.getElementById('maxTurns').value = template.max_turns;

        } catch (error) {
            console.error('Error loading template:', error);
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();

        const title = document.getElementById('sceneTitle').value;
        const genre = document.getElementById('genre').value;
        const context = document.getElementById('sceneContext').value;
        const maxTurns = parseInt(document.getElementById('maxTurns').value);

        this.maxTurns = maxTurns;
        this.dialogueHistory = []; // Reset history for new scene

        // Create scene configuration
        let config;

        if (this.currentTemplate) {
            // Use template as base, but allow overrides from form
            config = {
                ...this.currentTemplate,
                title: title,
                genre: genre,
                scene_context: context,
                max_turns: maxTurns
            };
        } else {
            // Default "Custom" configuration (minimal fallback)
            config = {
                title: title,
                genre: genre,
                scene_context: context,
                max_turns: maxTurns,
                min_turns: 6,
                characters: [
                    {
                        name: "Actor 1",
                        constitution: "You are Actor 1. Play your part based on the context.",
                        description: "First character"
                    },
                    {
                        name: "Actor 2",
                        constitution: "You are Actor 2. Play your part based on the context.",
                        description: "Second character"
                    }
                ],
                director_system_prompt: "You are the Director. Track the scene state and return JSON.",
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

        // Add dialogue entry UI
        const entry = document.createElement('div');
        // Add character-specific class (e.g., character-father-aldric)
        const charClass = `character-${message.character.toLowerCase().replace(/\s+/g, '-')}`;
        entry.className = `dialogue-entry ${charClass}`;
        
        entry.innerHTML = `
            <div class="character-name">${message.character}</div>
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
        if (this.ws) {
            this.sendMessage({ type: 'stop' });
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
