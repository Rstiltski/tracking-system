/**
 * Habits Module - Handles habit tracking functionality
 */

const Habits = {
    // Default habit icons
    icons: ['🏃', '📚', '💧', '🧘', '💪', '🎯', '✍️', '🛏️', '🥗', '💊', '🎨', '🎵', '💻', '🌱', '🙏'],

    // Default habit colors
    colors: ['#6366f1', '#ec4899', '#10b981', '#f59e0b', '#3b82f6', '#ef4444', '#8b5cf6', '#06b6d4'],

    // Initialize habits module
    init() {
        this.bindEvents();
        this.render();
    },

    // Bind event listeners
    bindEvents() {
        // Add habit button
        document.getElementById('addHabitBtn')?.addEventListener('click', () => {
            this.showAddModal();
        });
    },

    // Render habits list
    render() {
        this.renderHabitsList();
        this.renderQuickHabits();
    },

    // Render main habits list
    renderHabitsList() {
        const container = document.getElementById('habitsContainer');
        if (!container) return;

        const habits = Storage.getHabits();
        
        if (habits.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">✅</div>
                    <div class="empty-state-text">No habits yet. Start building good habits!</div>
                    <button class="add-btn" onclick="Habits.showAddModal()">+ Add Your First Habit</button>
                </div>
            `;
            return;
        }

        container.innerHTML = habits.map(habit => this.createHabitCard(habit)).join('');
        
        // Bind habit card events
        container.querySelectorAll('.habit-checkbox').forEach(checkbox => {
            checkbox.addEventListener('click', (e) => {
                const habitId = e.currentTarget.dataset.habitId;
                this.toggleHabit(habitId);
            });
        });

        container.querySelectorAll('.habit-edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const habitId = e.currentTarget.dataset.habitId;
                this.showEditModal(habitId);
            });
        });

        container.querySelectorAll('.habit-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const habitId = e.currentTarget.dataset.habitId;
                this.deleteHabit(habitId);
            });
        });
    },

    // Create habit card HTML
    createHabitCard(habit) {
        const isCompleted = Storage.isHabitCompletedOnDate(habit.id);
        const streak = Storage.getHabitStreak(habit.id);
        
        // Use Habit Score if available, otherwise fall back to streak display
        let scoreHtml = '';
        if (window.HabitScore) {
            scoreHtml = HabitScore.renderScore(habit.id);
        } else {
            scoreHtml = `
                <div class="habit-streak">
                    ${streak > 0 ? `<span class="streak-flame">🔥 ${streak} day streak</span>` : 'Start your streak today!'}
                </div>
            `;
        }

        return `
            <div class="habit-card ${isCompleted ? 'completed' : ''}" data-habit-id="${habit.id}">
                <div class="habit-checkbox ${isCompleted ? 'checked' : ''}" data-habit-id="${habit.id}">
                    ${isCompleted ? '✓' : ''}
                </div>
                <div class="habit-icon" style="color: ${habit.color}">${habit.icon}</div>
                <div class="habit-info">
                    <div class="habit-name">${habit.name}</div>
                    ${scoreHtml}
                </div>
                <div class="habit-actions">
                    <button class="habit-action-btn habit-edit" data-habit-id="${habit.id}" title="Edit">✏️</button>
                    <button class="habit-action-btn habit-delete" data-habit-id="${habit.id}" title="Delete">🗑️</button>
                </div>
            </div>
        `;
    },

    // Render quick habits for dashboard
    renderQuickHabits() {
        const container = document.getElementById('quickHabits');
        if (!container) return;

        const habits = Storage.getHabits();
        
        if (habits.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="padding: 20px;">
                    <div class="empty-state-text">No habits yet</div>
                </div>
            `;
            return;
        }

        container.innerHTML = habits.slice(0, 5).map(habit => {
            const isCompleted = Storage.isHabitCompletedOnDate(habit.id);
            return `
                <div class="quick-habit">
                    <div class="habit-checkbox ${isCompleted ? 'checked' : ''}" data-habit-id="${habit.id}">
                        ${isCompleted ? '✓' : ''}
                    </div>
                    <span class="habit-icon">${habit.icon}</span>
                    <span class="habit-name">${habit.name}</span>
                </div>
            `;
        }).join('');

        // Bind quick habit checkbox events
        container.querySelectorAll('.habit-checkbox').forEach(checkbox => {
            checkbox.addEventListener('click', (e) => {
                const habitId = e.currentTarget.dataset.habitId;
                this.toggleHabit(habitId);
            });
        });
    },

    // Toggle habit completion
    toggleHabit(habitId) {
        const isCompleted = Storage.isHabitCompletedOnDate(habitId);
        
        if (isCompleted) {
            Storage.unlogHabitCompletion(habitId);
            App.showToast('Habit unmarked', 'warning');
        } else {
            Storage.logHabitCompletion(habitId);
            App.showToast('Habit completed! +10 XP', 'success');
            Storage.addXP(10);
            App.updateUserStats();
            
            // Check for streak achievements
            const streak = Storage.getHabitStreak(habitId);
            if (streak === 7) {
                Achievements.unlock('streak_7');
            } else if (streak === 30) {
                Achievements.unlock('streak_30');
            }
            
            // Play celebration for completing habits
            if (Math.random() > 0.7) {
                App.celebrate();
            }
        }
        
        this.render();
        App.updateDashboard();
        Charts.updateChart('weeklyChart');
    },

    // Show add habit modal
    showAddModal() {
        const modalContent = {
            title: 'Add New Habit',
            body: `
                <div class="form-group">
                    <label class="form-label">Habit Name</label>
                    <input type="text" class="form-input" id="habitName" placeholder="e.g., Morning Exercise">
                </div>
                <div class="form-group">
                    <label class="form-label">Icon</label>
                    <div class="icon-picker" id="habitIconPicker">
                        ${this.icons.map((icon, i) => `
                            <button type="button" class="icon-option ${i === 0 ? 'selected' : ''}" data-icon="${icon}">${icon}</button>
                        `).join('')}
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Color</label>
                    <div class="color-picker" id="habitColorPicker">
                        ${this.colors.map((color, i) => `
                            <button type="button" class="color-option ${i === 0 ? 'selected' : ''}" data-color="${color}" style="background: ${color}"></button>
                        `).join('')}
                    </div>
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="Habits.addHabit()">Add Habit</button>
            `
        };

        App.showModal(modalContent);

        // Bind icon picker events
        document.querySelectorAll('#habitIconPicker .icon-option').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('#habitIconPicker .icon-option').forEach(b => b.classList.remove('selected'));
                e.target.classList.add('selected');
            });
        });

        // Bind color picker events
        document.querySelectorAll('#habitColorPicker .color-option').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('#habitColorPicker .color-option').forEach(b => b.classList.remove('selected'));
                e.target.classList.add('selected');
            });
        });
    },

    // Add new habit
    addHabit() {
        const name = document.getElementById('habitName')?.value.trim();
        const icon = document.querySelector('#habitIconPicker .icon-option.selected')?.dataset.icon || '🎯';
        const color = document.querySelector('#habitColorPicker .color-option.selected')?.dataset.color || this.colors[0];

        if (!name) {
            App.showToast('Please enter a habit name', 'error');
            return;
        }

        const habit = Storage.addHabit({
            name,
            icon,
            color
        });

        App.closeModal();
        App.showToast('Habit created successfully!', 'success');
        this.render();
        App.updateDashboard();

        // Check for first habit achievement
        const habits = Storage.getHabits();
        if (habits.length === 1) {
            Achievements.unlock('first_habit');
        }
    },

    // Show edit habit modal
    showEditModal(habitId) {
        const habits = Storage.getHabits();
        const habit = habits.find(h => h.id === habitId);
        if (!habit) return;

        const modalContent = {
            title: 'Edit Habit',
            body: `
                <div class="form-group">
                    <label class="form-label">Habit Name</label>
                    <input type="text" class="form-input" id="habitName" value="${habit.name}">
                </div>
                <div class="form-group">
                    <label class="form-label">Icon</label>
                    <div class="icon-picker" id="habitIconPicker">
                        ${this.icons.map(icon => `
                            <button type="button" class="icon-option ${icon === habit.icon ? 'selected' : ''}" data-icon="${icon}">${icon}</button>
                        `).join('')}
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Color</label>
                    <div class="color-picker" id="habitColorPicker">
                        ${this.colors.map(color => `
                            <button type="button" class="color-option ${color === habit.color ? 'selected' : ''}" data-color="${color}" style="background: ${color}"></button>
                        `).join('')}
                    </div>
                </div>
            `,
            footer: `
                <button class="btn btn-danger" onclick="Habits.deleteHabit('${habitId}')">Delete</button>
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="Habits.updateHabit('${habitId}')">Save Changes</button>
            `
        };

        App.showModal(modalContent);

        // Bind picker events
        document.querySelectorAll('#habitIconPicker .icon-option').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('#habitIconPicker .icon-option').forEach(b => b.classList.remove('selected'));
                e.target.classList.add('selected');
            });
        });

        document.querySelectorAll('#habitColorPicker .color-option').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('#habitColorPicker .color-option').forEach(b => b.classList.remove('selected'));
                e.target.classList.add('selected');
            });
        });
    },

    // Update habit
    updateHabit(habitId) {
        const name = document.getElementById('habitName')?.value.trim();
        const icon = document.querySelector('#habitIconPicker .icon-option.selected')?.dataset.icon;
        const color = document.querySelector('#habitColorPicker .color-option.selected')?.dataset.color;

        if (!name) {
            App.showToast('Please enter a habit name', 'error');
            return;
        }

        Storage.updateHabit(habitId, { name, icon, color });
        App.closeModal();
        App.showToast('Habit updated!', 'success');
        this.render();
        App.updateDashboard();
        Charts.updateChart('weeklyChart');
    },

    // Delete habit
    deleteHabit(habitId) {
        if (confirm('Are you sure you want to delete this habit?')) {
            Storage.deleteHabit(habitId);
            App.closeModal();
            App.showToast('Habit deleted', 'warning');
            this.render();
            App.updateDashboard();
        }
    },

    // Get total streaks count
    getTotalStreaks() {
        const habits = Storage.getHabits();
        return habits.reduce((total, habit) => {
            const streak = Storage.getHabitStreak(habit.id);
            return total + (streak > 0 ? 1 : 0);
        }, 0);
    }
};

// Export for use in other modules
window.Habits = Habits;