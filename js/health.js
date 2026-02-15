/**
 * Health Module - Handles health metrics tracking
 */

const Health = {
    // Initialize health module
    init() {
        this.bindEvents();
        this.render();
    },

    // Bind event listeners
    bindEvents() {
        document.getElementById('addHealthBtn')?.addEventListener('click', () => {
            this.showAddModal();
        });

        // Mood selector
        document.querySelectorAll('.mood-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const mood = parseInt(e.target.dataset.mood);
                this.logMood(mood);
            });
        });
    },

    // Render health view
    render() {
        this.renderMetrics();
        this.renderCharts();
    },

    // Render health metrics
    renderMetrics() {
        const health = Storage.getHealthData();

        // Weight - latest entry
        const latestWeight = health.weight.length > 0 
            ? health.weight[health.weight.length - 1].value 
            : null;
        document.getElementById('currentWeight').textContent = latestWeight 
            ? `${latestWeight} kg` 
            : '-- kg';

        // Sleep - average of last 7 days
        const recentSleep = health.sleep.slice(-7);
        const avgSleep = recentSleep.length > 0
            ? (recentSleep.reduce((sum, s) => sum + s.value, 0) / recentSleep.length).toFixed(1)
            : '--';
        document.getElementById('avgSleep').textContent = `${avgSleep} hrs`;

        // Update mood selector state
        const todayMood = health.mood.find(m => m.date === Storage.getTodayString());
        document.querySelectorAll('.mood-btn').forEach(btn => {
            btn.classList.toggle('selected', todayMood && parseInt(btn.dataset.mood) === todayMood.value);
        });
    },

    // Render health charts
    renderCharts() {
        Charts.initWeightChart('weightChart');
        Charts.initSleepChart('sleepChart');
        Charts.initMoodChart('moodChart');
    },

    // Show add health data modal
    showAddModal() {
        const modalContent = {
            title: 'Log Health Data',
            body: `
                <div class="form-group">
                    <label class="form-label">Metric Type</label>
                    <select class="form-select" id="healthMetricType" onchange="Health.toggleMetricFields()">
                        <option value="weight">⚖️ Weight</option>
                        <option value="sleep">😴 Sleep</option>
                    </select>
                </div>
                <div class="form-group" id="weightField">
                    <label class="form-label">Weight (kg)</label>
                    <input type="number" class="form-input" id="healthWeight" placeholder="70.0" step="0.1" min="0">
                </div>
                <div class="form-group" id="sleepField" style="display: none;">
                    <label class="form-label">Sleep Hours</label>
                    <input type="number" class="form-input" id="healthSleep" placeholder="7.5" step="0.5" min="0" max="24">
                </div>
                <div class="form-group">
                    <label class="form-label">Date</label>
                    <input type="date" class="form-input" id="healthDate" value="${Storage.getTodayString()}">
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="Health.addHealthEntry()">Save</button>
            `
        };

        App.showModal(modalContent);
    },

    // Toggle metric fields based on selection
    toggleMetricFields() {
        const type = document.getElementById('healthMetricType')?.value;
        document.getElementById('weightField').style.display = type === 'weight' ? 'block' : 'none';
        document.getElementById('sleepField').style.display = type === 'sleep' ? 'block' : 'none';
    },

    // Add health entry
    addHealthEntry() {
        const type = document.getElementById('healthMetricType')?.value;
        const date = document.getElementById('healthDate')?.value;
        
        let value;
        if (type === 'weight') {
            value = parseFloat(document.getElementById('healthWeight')?.value);
        } else if (type === 'sleep') {
            value = parseFloat(document.getElementById('healthSleep')?.value);
        }

        if (!value || value <= 0) {
            App.showToast('Please enter a valid value', 'error');
            return;
        }

        Storage.addHealthEntry(type, value, date);
        App.closeModal();
        App.showToast('Health data logged!', 'success');
        this.render();
        App.updateDashboard();
        Charts.updateChart('weightChart');
        Charts.updateChart('sleepChart');
        Charts.updateChart('moodChart');
    },

    // Log mood
    logMood(mood) {
        Storage.addHealthEntry('mood', mood);
        App.showToast('Mood logged!', 'success');
        this.render();
        App.updateDashboard();

        // Check for mood achievements
        const health = Storage.getHealthData();
        if (health.mood.length >= 7) {
            Achievements.unlock('mood_week');
        }
    },

    // Get health score (simple calculation)
    getHealthScore() {
        const health = Storage.getHealthData();
        let score = 0;
        let factors = 0;

        // Weight tracking
        if (health.weight.length > 0) {
            score += 25;
        }
        factors++;

        // Sleep tracking
        if (health.sleep.length > 0) {
            const recentSleep = health.sleep.slice(-7);
            const avgSleep = recentSleep.reduce((sum, s) => sum + s.value, 0) / recentSleep.length;
            if (avgSleep >= 7 && avgSleep <= 9) {
                score += 25;
            }
        }
        factors++;

        // Mood tracking
        if (health.mood.length > 0) {
            score += 25;
        }
        factors++;

        // Consistency
        const totalEntries = health.weight.length + health.sleep.length + health.mood.length;
        if (totalEntries >= 30) {
            score += 25;
        }

        return score;
    }
};

// Export for use in other modules
window.Health = Health;

