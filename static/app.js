
class SceneUI {
    constructor() {
        this.sceneId = null;
        this.ws = null;
        this.isSceneRunning = false;
        this.maxTurns = 30;
        this.currentTurn = 0;

        this.setupEventListeners();
    }

    setupEventListeners() {
        document.getElementById('sceneForm').addEventListener('submit', (e) => this.handleFormSubmit(e));
        document.getElementById('stopBtn').addEventListener('click', () => this.stopScene());
        document.getElementById('resetBtn').addEventListener('click', () => this.resetUI());
    }

    async handleFormSubmit(e) {
        e.preventDefault();

        const title = document.getElementById('sceneTitle').value;
        const genre = document.getElementById('genre').value;
        const context = document.getElementById('sceneContext').value;
        const maxTurns = parseInt(document.getElementById('maxTurns').value);

        this.maxTurns = maxTurns;

        // Create scene configuration
        const config = {
            title: title,
            genre: genre,
            scene_context: context,
            max_turns: maxTurns,
            min_turns: 6,
            characters: [
                {
                    name: "Father Aldric",
                    constitution: "You are Father Aldric Voss, 61 years old, a Catholic priest who has served the same parish for 34 years. You are not a simple man. You have heard thousands of confessions. You have lost your faith twice and found it again. You speak with formal, measured cadences — short sentences that carry weight. You do not perform warmth; when it comes, it is real. You are tired but not broken. You believe in the ritual of confession not merely as sacrament but as the only honest conversation most people ever have.",
                    description: "A weary, perceptive Catholic priest"
                },
                {
                    name: "Marco",
                    constitution: "You are Marco Bellini, 38 years old, a man who has not been to confession in eleven years. You are not here out of piety. Something happened three weeks ago that you cannot stop thinking about. You have not told anyone. You came here because you ran out of other options. You are not a villain. You are a person who made choices, and the choices made more choices, and now you are here. You are evasive at first — you make small confessions before the real one. You deflect with humor when cornered. You are not stupid; you know the priest sees through the deflection.",
                    description: "A man seeking confession after eleven years"
                }
            ],
            director_system_prompt: "You are the Director of a two-person theater scene. Your job is to track the scene's state after each turn and return a structured JSON object. Emotional arc stages: opening → tension → climax → resolution. Return ONLY valid JSON with no other text.",
            llm_model: "gemma3:4b",
            llm_server: "http://localhost:11434"
        };

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
            document.getElementById('dialogueContent').innerHTML = '';
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
        this.currentTurn = message.turn_number;

        // Update scene info
        document.getElementById('turnCount').textContent = message.turn_number + 1;

        const directorState = message.director_state;
        document.getElementById('arcStage').textContent = directorState.emotional_arc || '—';
        document.getElementById('endingType').textContent = directorState.ending_type || '—';

        // Update progress
        const progress = (this.currentTurn / this.maxTurns) * 100;
        document.getElementById('progressFill').style.width = `${progress}%`;

        // Add dialogue entry
        const dialogueContent = document.getElementById('dialogueContent');
        dialogueContent.innerHTML = ''; // Clear "waiting" message if first turn

        const entry = document.createElement('div');
        entry.className = 'dialogue-entry';
        entry.innerHTML = `
            <div class="character-name">${message.character}</div>
            <div class="dialogue-text">${this.escapeHtml(message.dialogue)}</div>
        `;
        dialogueContent.appendChild(entry);

        // Scroll to bottom
        setTimeout(() => {
            document.getElementById('dialogueBox').scrollTop = document.getElementById('dialogueBox').scrollHeight;
        }, 100);

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
