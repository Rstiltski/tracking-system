/**
 * Implementation Intentions Module - UI for If-Then planning
 * Phase 3.2 Implementation
 * 
 * Based on Peter Gollwitzer's research: "If situation X, then I will perform response Y"
 * Effect size: d = 0.6-0.8 on goal attainment
 */

const ImplementationIntentions = {
    // Trigger types
    triggerTypes: {
        time: { name: 'Time', icon: '⏰', description: 'At a specific time' },
        event: { name: 'Event', icon: '📅', description: 'After something happens' },
        location: { name: 'Location', icon: '📍', description: 'When at a place' },
        app: { name: 'App State', icon: '💻', description: 'When using an app' },
        calendar: { name: 'Calendar', icon: '📆', description: 'Before/after calendar events' }
    },

    // Action types
    actionTypes: {
        notification: { name: 'Notification', icon: '🔔', description: 'Send a notification' },
        reminder: { name: 'Reminder', icon: '⏰', description: 'Set a reminder' },
        habit_prompt: { name: 'Habit Prompt', icon: '✅', description: 'Prompt to complete a habit' }
    },

    // Preset templates
    presets: [
        {
            name: 'Morning Hydration',
            description: 'Drink water first thing in the morning',
            trigger_type: 'time',
            trigger_config: { time: '07:00' },
            action_type: 'notification',
            action_config: { message: 'Time to drink a glass of water! 💧' },
            icon: '💧'
        },
        {
            name: 'Post-Lunch Walk',
            description: 'Take a short walk after lunch',
            trigger_type: 'time',
            trigger_config: { time: '13:00' },
            action_type: 'notification',
            action_config: { message: 'Time for a short walk! 🚶' },
            icon: '🚶'
        },
        {
            name: 'Evening Reflection',
            description: 'Review your day before bed',
            trigger_type: 'time',
            trigger_config: { time: '21:00' },
            action_type: 'notification',
            action_config: { message: 'Time for daily reflection! 📝' },
            icon: '📝'
        },
        {
            name: 'Habit Chain Trigger',
            description: 'Trigger next habit after completing one',
            trigger_type: 'event',
            trigger_config: { event_type: 'habit_completed' },
            action_type: 'habit_prompt',
            action_config: { message: 'Ready for the next habit in your stack?' },
            icon: '🔗'
        },
        {
            name: 'Focus Time',
            description: 'Start focused work session',
            trigger_type: 'time',
            trigger_config: { time: '09:00' },
            action_type: 'notification',
            action_config: { message: 'Time to focus! Close distractions and get to work. 🎯' },
            icon: '🎯'
        },
        {
            name: 'Hydration Reminder',
            description: 'Stay hydrated throughout the day',
            trigger_type: 'time',
            trigger_config: { time: '10:00', repeat: true, interval: 2 },
            action_type: 'notification',
            action_config: { message: 'Drink some water! 💧' },
            icon: '💧'
        }
    ],

    // Initialize module
    init() {
        this.bindEvents();
        this.render();
        this.setupIntentionChecker();
    },

    // Bind event listeners
    bindEvents() {
        document.getElementById('addIntentionBtn')?.addEventListener('click', () => {
            this.showAddIntentionModal();
        });
    },

    // Main render function
    render() {
        this.renderIntentionsList();
        this.renderIntentionsAnalytics();
    },

    // Render list of implementation intentions
    renderIntentionsList() {
        const container = document.getElementById('intentionsContainer');
        if (!container) return;

        const intentions = Storage.getImplementationIntentions();
        
        if (intentions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🎯</div>
                    <div class="empty-state-text">No implementation intentions yet. Create If-Then rules to automate your behavior!</div>
                    <button class="add-btn" onclick="ImplementationIntentions.showAddIntentionModal()">+ Create Your First Intention</button>
                </div>
            `;
            return;
        }

        container.innerHTML = intentions.map(intention => this.createIntentionCard(intention)).join('');
        
        // Bind events
        container.querySelectorAll('.intention-toggle').forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                const intentionId = e.currentTarget.dataset.intentionId;
                this.toggleIntention(intentionId, e.target.checked);
            });
        });

        container.querySelectorAll('.intention-edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const intentionId = e.currentTarget.dataset.intentionId;
                this.showEditIntentionModal(intentionId);
            });
        });

        container.querySelectorAll('.intention-delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const intentionId = e.currentTarget.dataset.intentionId;
                this.deleteIntention(intentionId);
            });
        });

        container.querySelectorAll('.intention-trigger-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const intentionId = e.currentTarget.dataset.intentionId;
                this.triggerIntention(intentionId);
            });
        });
    },

    // Create intention card HTML
    createIntentionCard(intention) {
        const triggerType = this.triggerTypes[intention.trigger_type] || this.triggerTypes.time;
        const actionType = this.actionTypes[intention.action_type] || this.actionTypes.notification;
        const successRate = intention.trigger_count > 0 
            ? Math.round((intention.success_count / intention.trigger_count) * 100) 
            : 0;

        return `
            <div class="intention-card ${intention.is_active ? '' : 'inactive'}" data-intention-id="${intention.id}">
                <div class="intention-header">
                    <div class="intention-icon">${intention.icon || '🎯'}</div>
                    <div class="intention-info">
                        <h3 class="intention-name">${intention.name}</h3>
                        <p class="intention-description">${intention.description || ''}</p>
                    </div>
                    <label class="toggle-switch">
                        <input type="checkbox" class="intention-toggle" data-intention-id="${intention.id}" ${intention.is_active ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                </div>
                
                <div class="intention-rule">
                    <div class="rule-part if-part">
                        <span class="rule-label">IF</span>
                        <span class="rule-icon">${triggerType.icon}</span>
                        <span class="rule-text">${this.formatTriggerText(intention)}</span>
                    </div>
                    <div class="rule-arrow">↓</div>
                    <div class="rule-part then-part">
                        <span class="rule-label">THEN</span>
                        <span class="rule-icon">${actionType.icon}</span>
                        <span class="rule-text">${this.formatActionText(intention)}</span>
                    </div>
                </div>
                
                <div class="intention-stats">
                    <div class="intention-stat">
                        <span class="stat-value">${intention.trigger_count || 0}</span>
                        <span class="stat-label">Triggers</span>
                    </div>
                    <div class="intention-stat">
                        <span class="stat-value">${successRate}%</span>
                        <span class="stat-label">Success</span>
                    </div>
                </div>
                
                <div class="intention-actions">
                    <button class="intention-btn intention-trigger-btn" data-intention-id="${intention.id}" title="Trigger Now">
                        🔔 Test
                    </button>
                    <button class="intention-btn intention-edit-btn" data-intention-id="${intention.id}">
                        ✏️ Edit
                    </button>
                    <button class="intention-btn intention-delete-btn" data-intention-id="${intention.id}">
                        🗑️
                    </button>
                </div>
            </div>
        `;
    },

    // Format trigger text for display
    formatTriggerText(intention) {
        switch (intention.trigger_type) {
            case 'time':
                const timeConfig = intention.trigger_config || {};
                if (timeConfig.time) {
                    return `It's ${timeConfig.time}`;
                }
                return 'Time-based trigger';
            case 'event':
                const eventConfig = intention.trigger_config || {};
                if (eventConfig.event_type === 'habit_completed') {
                    return 'A habit is completed';
                }
                return eventConfig.event_type || 'Event occurs';
            case 'location':
                const locConfig = intention.trigger_config || {};
                return `At ${locConfig.location || 'location'}`;
            case 'app':
                const appConfig = intention.trigger_config || {};
                return `Using ${appConfig.app || 'app'}`;
            case 'calendar':
                const calConfig = intention.trigger_config || {};
                return calConfig.event_match || 'Calendar event';
            default:
                return intention.trigger_description || 'Trigger';
        }
    },

    // Format action text for display
    formatActionText(intention) {
        const config = intention.action_config || {};
        switch (intention.action_type) {
            case 'notification':
                return config.message || 'Send notification';
            case 'reminder':
                return `Remind: ${config.message || 'Reminder'}`;
            case 'habit_prompt':
                const habit = Storage.getHabits().find(h => h.id === config.habit_id);
                return habit ? `Prompt: ${habit.name}` : 'Prompt for habit';
            default:
                return config.message || 'Take action';
        }
    },

    // Show add intention modal
    showAddIntentionModal() {
        const habits = Storage.getHabits();
        
        const modalContent = {
            title: 'Create Implementation Intention',
            body: `
                <div class="form-group">
                    <label class="form-label">Name</label>
                    <input type="text" class="form-input" id="intentionName" placeholder="e.g., Morning Hydration">
                </div>
                
                <div class="form-group">
                    <label class="form-label">Description (optional)</label>
                    <input type="text" class="form-input" id="intentionDescription" placeholder="e.g., Drink water first thing in the morning">
                </div>
                
                <div class="form-group">
                    <label class="form-label">Icon</label>
                    <div class="icon-picker" id="intentionIconPicker">
                        ${['🎯', '💧', '🏃', '📚', '💪', '🧘', '✍️', '🍎', '💤', '🧠', '⏰', '🔔'].map((icon, i) => `
                            <button type="button" class="icon-option ${i === 0 ? 'selected' : ''}" data-icon="${icon}">${icon}</button>
                        `).join('')}
                    </div>
                </div>
                
                <div class="form-section">
                    <h4 class="form-section-title">IF (Trigger)</h4>
                    
                    <div class="form-group">
                        <label class="form-label">Trigger Type</label>
                        <select class="form-select" id="triggerType">
                            ${Object.entries(this.triggerTypes).map(([key, type]) => `
                                <option value="${key}">${type.icon} ${type.name} - ${type.description}</option>
                            `).join('')}
                        </select>
                    </div>
                    
                    <div id="triggerConfigContainer">
                        ${this.renderTriggerConfig('time')}
                    </div>
                </div>
                
                <div class="form-section">
                    <h4 class="form-section-title">THEN (Action)</h4>
                    
                    <div class="form-group">
                        <label class="form-label">Action Type</label>
                        <select class="form-select" id="actionType">
                            ${Object.entries(this.actionTypes).map(([key, type]) => `
                                <option value="${key}">${type.icon} ${type.name} - ${type.description}</option>
                            `).join('')}
                        </select>
                    </div>
                    
                    <div id="actionConfigContainer">
                        ${this.renderActionConfig('notification', habits)}
                    </div>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Or use a preset template</label>
                    <select class="form-select" id="presetSelector">
                        <option value="">Select a preset...</option>
                        ${this.presets.map(preset => `
                            <option value="${preset.name}">${preset.icon} ${preset.name} - ${preset.description}</option>
                        `).join('')}
                    </select>
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="ImplementationIntentions.createIntention()">Create Intention</button>
            `
        };

        App.showModal(modalContent);

        // Bind events
        this.bindModalEvents(habits);
    },

    // Bind modal events
    bindModalEvents(habits) {
        // Icon picker
        document.querySelectorAll('#intentionIconPicker .icon-option').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('#intentionIconPicker .icon-option').forEach(b => b.classList.remove('selected'));
                e.target.classList.add('selected');
            });
        });

        // Trigger type change
        document.getElementById('triggerType').addEventListener('change', (e) => {
            document.getElementById('triggerConfigContainer').innerHTML = this.renderTriggerConfig(e.target.value);
        });

        // Action type change
        document.getElementById('actionType').addEventListener('change', (e) => {
            document.getElementById('actionConfigContainer').innerHTML = this.renderActionConfig(e.target.value, habits);
        });

        // Preset selector
        document.getElementById('presetSelector').addEventListener('change', (e) => {
            if (e.target.value) {
                this.applyPreset(e.target.value);
            }
        });
    },

    // Render trigger configuration based on type
    renderTriggerConfig(type) {
        switch (type) {
            case 'time':
                return `
                    <div class="form-group">
                        <label class="form-label">Time</label>
                        <input type="time" class="form-input" id="triggerTime" value="08:00">
                    </div>
                    <div class="form-group">
                        <label class="form-check">
                            <input type="checkbox" id="triggerRepeat">
                            <span class="form-check-label">Repeat daily</span>
                        </label>
                    </div>
                `;
            case 'event':
                return `
                    <div class="form-group">
                        <label class="form-label">Event Type</label>
                        <select class="form-select" id="triggerEvent">
                            <option value="habit_completed">Habit completed</option>
                            <option value="goal_achieved">Goal achieved</option>
                            <option value="streak_milestone">Streak milestone</option>
                            <option value="level_up">Level up</option>
                        </select>
                    </div>
                `;
            case 'location':
                return `
                    <div class="form-group">
                        <label class="form-label">Location</label>
                        <input type="text" class="form-input" id="triggerLocation" placeholder="e.g., Gym, Office, Home">
                    </div>
                `;
            case 'app':
                return `
                    <div class="form-group">
                        <label class="form-label">Application</label>
                        <input type="text" class="form-input" id="triggerApp" placeholder="e.g., VS Code, Slack">
                    </div>
                `;
            case 'calendar':
                return `
                    <div class="form-group">
                        <label class="form-label">Event Match</label>
                        <input type="text" class="form-input" id="triggerCalendar" placeholder="e.g., Meeting, Standup">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Timing</label>
                        <select class="form-select" id="triggerCalendarTiming">
                            <option value="before">Before event</option>
                            <option value="after">After event</option>
                            <option value="during">During event</option>
                        </select>
                    </div>
                `;
            default:
                return '';
        }
    },

    // Render action configuration based on type
    renderActionConfig(type, habits = []) {
        switch (type) {
            case 'notification':
                return `
                    <div class="form-group">
                        <label class="form-label">Message</label>
                        <input type="text" class="form-input" id="actionMessage" placeholder="e.g., Time to drink water! 💧">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Priority</label>
                        <select class="form-select" id="actionPriority">
                            <option value="0">Normal</option>
                            <option value="1">High</option>
                            <option value="2">Urgent</option>
                        </select>
                    </div>
                `;
            case 'reminder':
                return `
                    <div class="form-group">
                        <label class="form-label">Reminder Message</label>
                        <input type="text" class="form-input" id="actionMessage" placeholder="e.g., Don't forget to stretch!">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Snooze (minutes)</label>
                        <input type="number" class="form-input" id="actionSnooze" value="5" min="1" max="60">
                    </div>
                `;
            case 'habit_prompt':
                return `
                    <div class="form-group">
                        <label class="form-label">Select Habit</label>
                        <select class="form-select" id="actionHabit">
                            ${habits.map(h => `<option value="${h.id}">${h.icon} ${h.name}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Prompt Message</label>
                        <input type="text" class="form-input" id="actionMessage" placeholder="e.g., Ready for your next habit?">
                    </div>
                `;
            default:
                return '';
        }
    },

    // Apply preset template
    applyPreset(presetName) {
        const preset = this.presets.find(p => p.name === presetName);
        if (!preset) return;

        document.getElementById('intentionName').value = preset.name;
        document.getElementById('intentionDescription').value = preset.description;
        
        // Set icon
        document.querySelectorAll('#intentionIconPicker .icon-option').forEach(btn => {
            btn.classList.toggle('selected', btn.dataset.icon === preset.icon);
        });

        // Set trigger type
        document.getElementById('triggerType').value = preset.trigger_type;
        document.getElementById('triggerConfigContainer').innerHTML = this.renderTriggerConfig(preset.trigger_type);

        // Set trigger config
        if (preset.trigger_config.time) {
            const timeInput = document.getElementById('triggerTime');
            if (timeInput) timeInput.value = preset.trigger_config.time;
        }

        // Set action type
        document.getElementById('actionType').value = preset.action_type;
        document.getElementById('actionConfigContainer').innerHTML = this.renderActionConfig(preset.action_type);

        // Set action config
        if (preset.action_config.message) {
            const msgInput = document.getElementById('actionMessage');
            if (msgInput) msgInput.value = preset.action_config.message;
        }
    },

    // Create new intention
    createIntention() {
        const name = document.getElementById('intentionName')?.value.trim();
        const description = document.getElementById('intentionDescription')?.value.trim();
        const icon = document.querySelector('#intentionIconPicker .icon-option.selected')?.dataset.icon || '🎯';
        const triggerType = document.getElementById('triggerType')?.value;
        const actionType = document.getElementById('actionType')?.value;

        if (!name) {
            App.showToast('Please enter a name', 'error');
            return;
        }

        // Get trigger config
        const triggerConfig = this.getTriggerConfig(triggerType);
        const actionConfig = this.getActionConfig(actionType);

        const intention = Storage.addImplementationIntention({
            name,
            description,
            icon,
            trigger_type: triggerType,
            trigger_source: this.getTriggerSource(triggerType),
            trigger_predicate: this.buildPredicate(triggerType, triggerConfig),
            trigger_description: this.formatTriggerText({ trigger_type: triggerType, trigger_config: triggerConfig }),
            trigger_config: triggerConfig,
            action_type: actionType,
            action_payload: actionConfig.message || '',
            action_config: actionConfig,
            action_priority: parseInt(actionConfig.priority) || 0
        });

        App.closeModal();
        App.showToast('Implementation intention created!', 'success');
        this.render();
    },

    // Get trigger config from form
    getTriggerConfig(type) {
        switch (type) {
            case 'time':
                return {
                    time: document.getElementById('triggerTime')?.value || '08:00',
                    repeat: document.getElementById('triggerRepeat')?.checked || false
                };
            case 'event':
                return {
                    event_type: document.getElementById('triggerEvent')?.value || 'habit_completed'
                };
            case 'location':
                return {
                    location: document.getElementById('triggerLocation')?.value || ''
                };
            case 'app':
                return {
                    app: document.getElementById('triggerApp')?.value || ''
                };
            case 'calendar':
                return {
                    event_match: document.getElementById('triggerCalendar')?.value || '',
                    timing: document.getElementById('triggerCalendarTiming')?.value || 'before'
                };
            default:
                return {};
        }
    },

    // Get action config from form
    getActionConfig(type) {
        const config = {
            message: document.getElementById('actionMessage')?.value || ''
        };

        if (type === 'reminder') {
            config.snooze = parseInt(document.getElementById('actionSnooze')?.value) || 5;
        }

        if (type === 'habit_prompt') {
            config.habit_id = document.getElementById('actionHabit')?.value || '';
        }

        if (type === 'notification') {
            config.priority = document.getElementById('actionPriority')?.value || '0';
        }

        return config;
    },

    // Get trigger source
    getTriggerSource(type) {
        const sources = {
            time: 'clock',
            event: 'event_bus',
            location: 'location_service',
            app: 'app_monitor',
            calendar: 'calendar'
        };
        return sources[type] || 'custom';
    },

    // Build predicate string
    buildPredicate(type, config) {
        switch (type) {
            case 'time':
                return `time == '${config.time}'`;
            case 'event':
                return `event_type == '${config.event_type}'`;
            case 'location':
                return `location == '${config.location}'`;
            case 'app':
                return `app == '${config.app}'`;
            case 'calendar':
                return `before_event == '${config.event_match}'`;
            default:
                return 'true';
        }
    },

    // Show edit intention modal
    showEditIntentionModal(intentionId) {
        const intentions = Storage.getImplementationIntentions();
        const intention = intentions.find(i => i.id === intentionId);
        if (!intention) return;

        const habits = Storage.getHabits();
        
        const modalContent = {
            title: 'Edit Implementation Intention',
            body: `
                <div class="form-group">
                    <label class="form-label">Name</label>
                    <input type="text" class="form-input" id="intentionName" value="${intention.name}">
                </div>
                
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <input type="text" class="form-input" id="intentionDescription" value="${intention.description || ''}">
                </div>
                
                <div class="form-group">
                    <label class="form-label">Icon</label>
                    <div class="icon-picker" id="intentionIconPicker">
                        ${['🎯', '💧', '🏃', '📚', '💪', '🧘', '✍️', '🍎', '💤', '🧠', '⏰', '🔔'].map(icon => `
                            <button type="button" class="icon-option ${icon === intention.icon ? 'selected' : ''}" data-icon="${icon}">${icon}</button>
                        `).join('')}
                    </div>
                </div>
                
                <div class="form-section">
                    <h4 class="form-section-title">IF (Trigger)</h4>
                    <div class="form-group">
                        <label class="form-label">Trigger Type</label>
                        <select class="form-select" id="triggerType">
                            ${Object.entries(this.triggerTypes).map(([key, type]) => `
                                <option value="${key}" ${key === intention.trigger_type ? 'selected' : ''}>${type.icon} ${type.name}</option>
                            `).join('')}
                        </select>
                    </div>
                    <div id="triggerConfigContainer">
                        ${this.renderTriggerConfig(intention.trigger_type)}
                    </div>
                </div>
                
                <div class="form-section">
                    <h4 class="form-section-title">THEN (Action)</h4>
                    <div class="form-group">
                        <label class="form-label">Action Type</label>
                        <select class="form-select" id="actionType">
                            ${Object.entries(this.actionTypes).map(([key, type]) => `
                                <option value="${key}" ${key === intention.action_type ? 'selected' : ''}>${type.icon} ${type.name}</option>
                            `).join('')}
                        </select>
                    </div>
                    <div id="actionConfigContainer">
                        ${this.renderActionConfig(intention.action_type, habits)}
                    </div>
                </div>
            `,
            footer: `
                <button class="btn btn-danger" onclick="ImplementationIntentions.deleteIntention('${intentionId}')">Delete</button>
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="ImplementationIntentions.updateIntention('${intentionId}')">Save Changes</button>
            `
        };

        App.showModal(modalContent);
        this.bindModalEvents(habits);

        // Populate existing values
        setTimeout(() => {
            const triggerConfig = intention.trigger_config || {};
            const actionConfig = intention.action_config || {};

            // Trigger config
            if (triggerConfig.time) {
                const timeInput = document.getElementById('triggerTime');
                if (timeInput) timeInput.value = triggerConfig.time;
            }
            if (triggerConfig.event_type) {
                const eventSelect = document.getElementById('triggerEvent');
                if (eventSelect) eventSelect.value = triggerConfig.event_type;
            }

            // Action config
            if (actionConfig.message) {
                const msgInput = document.getElementById('actionMessage');
                if (msgInput) msgInput.value = actionConfig.message;
            }
        }, 100);
    },

    // Update intention
    updateIntention(intentionId) {
        const name = document.getElementById('intentionName')?.value.trim();
        const description = document.getElementById('intentionDescription')?.value.trim();
        const icon = document.querySelector('#intentionIconPicker .icon-option.selected')?.dataset.icon || '🎯';
        const triggerType = document.getElementById('triggerType')?.value;
        const actionType = document.getElementById('actionType')?.value;

        if (!name) {
            App.showToast('Please enter a name', 'error');
            return;
        }

        const triggerConfig = this.getTriggerConfig(triggerType);
        const actionConfig = this.getActionConfig(actionType);

        Storage.updateImplementationIntention(intentionId, {
            name,
            description,
            icon,
            trigger_type: triggerType,
            trigger_source: this.getTriggerSource(triggerType),
            trigger_predicate: this.buildPredicate(triggerType, triggerConfig),
            trigger_description: this.formatTriggerText({ trigger_type: triggerType, trigger_config: triggerConfig }),
            trigger_config: triggerConfig,
            action_type: actionType,
            action_payload: actionConfig.message || '',
            action_config: actionConfig,
            action_priority: parseInt(actionConfig.priority) || 0
        });

        App.closeModal();
        App.showToast('Intention updated!', 'success');
        this.render();
    },

    // Delete intention
    deleteIntention(intentionId) {
        if (confirm('Are you sure you want to delete this implementation intention?')) {
            Storage.deleteImplementationIntention(intentionId);
            App.closeModal();
            App.showToast('Intention deleted', 'warning');
            this.render();
        }
    },

    // Toggle intention active state
    toggleIntention(intentionId, isActive) {
        Storage.updateImplementationIntention(intentionId, { is_active: isActive });
        App.showToast(isActive ? 'Intention activated' : 'Intention deactivated', 'info');
    },

    // Manually trigger an intention
    triggerIntention(intentionId) {
        const intentions = Storage.getImplementationIntentions();
        const intention = intentions.find(i => i.id === intentionId);
        if (!intention) return;

        // Increment trigger count
        Storage.updateImplementationIntention(intentionId, {
            trigger_count: (intention.trigger_count || 0) + 1
        });

        // Show the action
        this.showIntentionAction(intention);

        // Record trigger
        Storage.addIntentionTrigger({
            intention_id: intentionId,
            action_dispatched: true
        });

        this.render();
    },

    // Show intention action (notification/reminder)
    showIntentionAction(intention) {
        const config = intention.action_config || {};
        
        App.showModal({
            title: intention.name,
            body: `
                <div class="intention-action-display">
                    <div class="action-icon">${intention.icon || '🎯'}</div>
                    <p class="action-message">${config.message || 'Time to take action!'}</p>
                    ${intention.action_type === 'habit_prompt' && config.habit_id ? `
                        <button class="btn btn-primary" onclick="ImplementationIntentions.completeHabitFromPrompt('${config.habit_id}', '${intention.id}')">
                            ✓ Mark Complete
                        </button>
                    ` : ''}
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="ImplementationIntentions.dismissIntention('${intention.id}')">Dismiss</button>
                <button class="btn btn-primary" onclick="ImplementationIntentions.respondToIntention('${intention.id}')">Done!</button>
            `
        });
    },

    // Complete habit from prompt
    completeHabitFromPrompt(habitId, intentionId) {
        Storage.logHabitCompletion(habitId);
        this.respondToIntention(intentionId);
        App.closeModal();
        App.showToast('Habit completed!', 'success');
    },

    // Respond to intention (mark success)
    respondToIntention(intentionId) {
        const intentions = Storage.getImplementationIntentions();
        const intention = intentions.find(i => i.id === intentionId);
        
        if (intention) {
            Storage.updateImplementationIntention(intentionId, {
                success_count: (intention.success_count || 0) + 1
            });
        }

        App.closeModal();
        App.showToast('Great job!', 'success');
        this.render();
    },

    // Dismiss intention
    dismissIntention(intentionId) {
        App.closeModal();
    },

    // Setup intention checker (runs periodically)
    setupIntentionChecker() {
        // Check every minute for time-based triggers
        setInterval(() => this.checkTimeTriggers(), 60000);
        
        // Initial check
        this.checkTimeTriggers();
    },

    // Check time-based triggers
    checkTimeTriggers() {
        const now = new Date();
        const currentTime = now.toTimeString().slice(0, 5); // HH:MM format
        
        const intentions = Storage.getImplementationIntentions()
            .filter(i => i.is_active && i.trigger_type === 'time');
        
        intentions.forEach(intention => {
            const config = intention.trigger_config || {};
            if (config.time === currentTime) {
                // Check if already triggered today
                const triggers = Storage.getIntentionTriggers()
                    .filter(t => t.intention_id === intention.id);
                const todayTrigger = triggers.find(t => 
                    Storage.isSameDay(t.triggeredAt, now)
                );
                
                if (!todayTrigger) {
                    this.triggerIntention(intention.id);
                }
            }
        });
    },

    // Render analytics
    renderIntentionsAnalytics() {
        const container = document.getElementById('intentionsAnalytics');
        if (!container) return;

        const intentions = Storage.getImplementationIntentions();
        const triggers = Storage.getIntentionTriggers();

        if (intentions.length === 0) {
            container.innerHTML = '<p class="empty-state-text">Create intentions to see analytics</p>';
            return;
        }

        const activeCount = intentions.filter(i => i.is_active).length;
        const totalTriggers = triggers.length;
        const totalSuccess = intentions.reduce((sum, i) => sum + (i.success_count || 0), 0);
        const avgSuccessRate = totalTriggers > 0 
            ? Math.round((totalSuccess / totalTriggers) * 100)
            : 0;

        container.innerHTML = `
            <div class="analytics-grid">
                <div class="analytics-stat">
                    <div class="analytics-value">${activeCount}</div>
                    <div class="analytics-label">Active Intentions</div>
                </div>
                <div class="analytics-stat">
                    <div class="analytics-value">${totalTriggers}</div>
                    <div class="analytics-label">Total Triggers</div>
                </div>
                <div class="analytics-stat">
                    <div class="analytics-value">${avgSuccessRate}%</div>
                    <div class="analytics-label">Success Rate</div>
                </div>
            </div>
        `;
    }
};

// Export for use in other modules
window.ImplementationIntentions = ImplementationIntentions;