/**
 * Time Module - Handles time tracking and productivity
 */

const Time = {
    // Timer state
    timerInterval: null,
    timerSeconds: 0,
    timerRunning: false,
    timerCategory: 'work',
    
    // Storage key for timer state
    TIMER_STATE_KEY: 'tracklife_timer_state',

    // Initialize time module
    init() {
        this.restoreTimerState();
        this.bindEvents();
        this.render();
    },
    
    // Save timer state to localStorage
    saveTimerState() {
        const timerState = {
            seconds: this.timerSeconds,
            running: this.timerRunning,
            category: this.timerCategory,
            timestamp: Date.now()
        };
        
        try {
            localStorage.setItem(this.TIMER_STATE_KEY, JSON.stringify(timerState));
        } catch (error) {
            console.error('Error saving timer state:', error);
        }
    },
    
    // Restore timer state from localStorage
    restoreTimerState() {
        try {
            const timerState = localStorage.getItem(this.TIMER_STATE_KEY);
            if (timerState) {
                const state = JSON.parse(timerState);
                
                // Calculate elapsed time since last save if timer was running
                if (state.running) {
                    const elapsed = Math.floor((Date.now() - state.timestamp) / 1000);
                    this.timerSeconds = state.seconds + elapsed;
                } else {
                    this.timerSeconds = state.seconds;
                }
                
                this.timerRunning = state.running;
                this.timerCategory = state.category;
                
                // Restart the timer if it was previously running
                if (this.timerRunning) {
                    this.startTimer();
                }
            }
        } catch (error) {
            console.error('Error restoring timer state:', error);
            // Reset to default state on error
            this.timerSeconds = 0;
            this.timerRunning = false;
            this.timerCategory = 'work';
        }
    },
    
    // Clear timer state
    clearTimerState() {
        try {
            localStorage.removeItem(this.TIMER_STATE_KEY);
        } catch (error) {
            console.error('Error clearing timer state:', error);
        }
    },

    // Bind event listeners
    bindEvents() {
        const addTimeEntryBtn = document.getElementById('addTimeEntryBtn');
        if (addTimeEntryBtn) {
            const newBtn = addTimeEntryBtn.cloneNode(true);
            addTimeEntryBtn.parentNode.replaceChild(newBtn, addTimeEntryBtn);
            newBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showAddModal();
            });
        }

        const timerStart = document.getElementById('timerStart');
        if (timerStart) {
            const newStartBtn = timerStart.cloneNode(true);
            timerStart.parentNode.replaceChild(newStartBtn, timerStart);
            newStartBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.startTimer();
            });
        }

        const timerPause = document.getElementById('timerPause');
        if (timerPause) {
            const newPauseBtn = timerPause.cloneNode(true);
            timerPause.parentNode.replaceChild(newPauseBtn, timerPause);
            newPauseBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.pauseTimer();
            });
        }

        const timerReset = document.getElementById('timerReset');
        if (timerReset) {
            const newResetBtn = timerReset.cloneNode(true);
            timerReset.parentNode.replaceChild(newResetBtn, timerReset);
            newResetBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.resetTimer();
            });
        }

        const timerCategory = document.getElementById('timerCategory');
        if (timerCategory) {
            const newCategorySelect = timerCategory.cloneNode(true);
            timerCategory.parentNode.replaceChild(newCategorySelect, timerCategory);
            newCategorySelect.addEventListener('change', (e) => {
                this.timerCategory = e.target.value;
                this.saveTimerState();
            });
        }
    },

    // Render time view
    render() {
        this.renderTimerDisplay();
        this.renderTimeEntries();
        this.renderChart();
    },

    // Render timer display
    renderTimerDisplay() {
        const display = document.getElementById('timerDisplay');
        if (display) {
            display.textContent = this.formatTime(this.timerSeconds);
        }
    },

    // Render time entries
    renderTimeEntries() {
        const container = document.getElementById('timeEntriesList');
        if (!container) return;

        const entries = Storage.getTimeEntries();
        const todayStr = Storage.getTodayString();
        const todayEntries = entries.filter(e => e.date === todayStr);

        if (todayEntries.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="padding: 20px;">
                    <div class="empty-state-text">No time entries today</div>
                </div>
            `;
            return;
        }

        container.innerHTML = todayEntries.map(entry => this.createTimeEntryItem(entry)).join('');

        // Bind delete events
        container.querySelectorAll('.time-entry-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const entryId = e.currentTarget.dataset.entryId;
                this.deleteTimeEntry(entryId);
            });
        });
    },

    // Create time entry item HTML
    createTimeEntryItem(entry) {
        const categoryIcons = {
            work: '💼',
            study: '📚',
            exercise: '🏃',
            leisure: '🎮',
            other: '📌'
        };

        return `
            <div class="time-entry">
                <div class="time-entry-category">${categoryIcons[entry.category] || '📌'}</div>
                <div class="time-entry-info">
                    <div class="time-entry-title">${entry.category.charAt(0).toUpperCase() + entry.category.slice(1)}</div>
                    <div class="time-entry-duration">${this.formatDuration(entry.duration)}</div>
                </div>
                <button class="habit-action-btn time-entry-delete" data-entry-id="${entry.id}" title="Delete">🗑️</button>
            </div>
        `;
    },

    // Render time chart
    renderChart() {
        Charts.initTimeChart('timeChart');
    },

    // Start timer
    startTimer() {
        if (this.timerRunning) return;

        this.timerRunning = true;
        this.timerInterval = setInterval(() => {
            this.timerSeconds++;
            this.renderTimerDisplay();
        }, 1000);

        App.showToast('Timer started!', 'success');
        this.saveTimerState();
    },

    // Pause timer
    pauseTimer() {
        if (!this.timerRunning) return;

        this.timerRunning = false;
        clearInterval(this.timerInterval);

        App.showToast('Timer paused', 'warning');
        this.saveTimerState();
    },

    // Reset timer
    resetTimer() {
        this.pauseTimer();

        if (this.timerSeconds > 0) {
            if (confirm('Do you want to save this time entry before resetting?')) {
                this.saveTimeEntry();
            }
        }

        this.timerSeconds = 0;
        this.renderTimerDisplay();
        this.clearTimerState();
    },

    // Save time entry
    saveTimeEntry() {
        if (this.timerSeconds < 60) {
            App.showToast('Timer must be at least 1 minute', 'error');
            return;
        }

        const minutes = Math.floor(this.timerSeconds / 60);
        
        Storage.addTimeEntry({
            category: this.timerCategory,
            duration: minutes,
            date: Storage.getTodayString()
        });

        App.showToast('Time entry saved!', 'success');
        
        this.timerSeconds = 0;
        this.renderTimerDisplay();
        this.render();
        App.updateDashboard();

        // Check for time tracking achievements
        const entries = Storage.getTimeEntries();
        if (entries.length >= 10) {
            Achievements.unlock('time_10');
        }
    },

    // Show add time entry modal
    showAddModal() {
        const modalContent = {
            title: 'Add Time Entry',
            body: `
                <div class="form-group">
                    <label class="form-label">Category</label>
                    <select class="form-select" id="timeCategory">
                        <option value="work">💼 Work</option>
                        <option value="study">📚 Study</option>
                        <option value="exercise">🏃 Exercise</option>
                        <option value="leisure">🎮 Leisure</option>
                        <option value="other">📌 Other</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Duration (minutes)</label>
                    <input type="number" class="form-input" id="timeDuration" placeholder="60" min="1">
                </div>
                <div class="form-group">
                    <label class="form-label">Date</label>
                    <input type="date" class="form-input" id="timeDate" value="${Storage.getTodayString()}">
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="Time.addTimeEntry()">Add Entry</button>
            `
        };

        App.showModal(modalContent);
    },

    // Add time entry from modal
    addTimeEntry() {
        const category = document.getElementById('timeCategory')?.value;
        const duration = parseInt(document.getElementById('timeDuration')?.value);
        const date = document.getElementById('timeDate')?.value;

        if (!duration || duration <= 0) {
            App.showToast('Please enter a valid duration', 'error');
            return;
        }

        Storage.addTimeEntry({ category, duration, date });
        App.closeModal();
        App.showToast('Time entry added!', 'success');
        this.render();
        App.updateDashboard();
        Charts.updateChart('timeChart');
    },

    // Delete time entry
    deleteTimeEntry(entryId) {
        if (confirm('Are you sure you want to delete this time entry?')) {
            Storage.deleteTimeEntry(entryId);
            App.showToast('Time entry deleted', 'warning');
            this.render();
            App.updateDashboard();
        }
    },

    // Format seconds to HH:MM:SS
    formatTime(seconds) {
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    },

    // Format duration for display
    formatDuration(minutes) {
        const hrs = Math.floor(minutes / 60);
        const mins = minutes % 60;
        if (hrs > 0) {
            return `${hrs}h ${mins}m`;
        }
        return `${mins}m`;
    },

    // Get today's total time
    getTodayTotalTime() {
        const entries = Storage.getTimeEntries();
        const todayStr = Storage.getTodayString();
        const todayEntries = entries.filter(e => e.date === todayStr);
        return todayEntries.reduce((sum, e) => sum + e.duration, 0);
    }
};

// Export for use in other modules
window.Time = Time;

