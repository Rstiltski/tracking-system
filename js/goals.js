/**
 * Goals Module - Handles goal setting and progress tracking
 */

const Goals = {
    // Initialize goals module
    init() {
        this.bindEvents();
        this.render();
    },

    // Bind event listeners
    bindEvents() {
        document.getElementById('addGoalBtn')?.addEventListener('click', () => {
            this.showAddModal();
        });
    },

    // Render goals view
    render() {
        this.renderGoalsList();
        this.renderGoalsOverview();
    },

    // Render main goals list
    renderGoalsList() {
        const container = document.getElementById('goalsContainer');
        if (!container) return;

        const goals = Storage.getGoals();

        if (goals.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🎯</div>
                    <div class="empty-state-text">No goals yet. Set your first goal!</div>
                    <button class="add-btn" onclick="Goals.showAddModal()">+ Add Goal</button>
                </div>
            `;
            return;
        }

        container.innerHTML = goals.map(goal => this.createGoalCard(goal)).join('');

        // Bind goal events
        container.querySelectorAll('.goal-progress-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const goalId = e.currentTarget.dataset.goalId;
                this.showProgressModal(goalId);
            });
        });

        container.querySelectorAll('.goal-delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const goalId = e.currentTarget.dataset.goalId;
                this.deleteGoal(goalId);
            });
        });
    },

    // Create goal card HTML
    createGoalCard(goal) {
        const deadline = goal.deadline 
            ? new Date(goal.deadline).toLocaleDateString() 
            : 'No deadline';
        
        const isCompleted = goal.progress >= 100;

        return `
            <div class="goal-card ${isCompleted ? 'completed' : ''}">
                <div class="goal-header">
                    <div class="goal-title">${goal.title}</div>
                    <div class="goal-deadline">📅 ${deadline}</div>
                </div>
                <div class="goal-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${goal.progress}%"></div>
                    </div>
                    <div class="progress-text">
                        <span>${goal.progress}% complete</span>
                        <span>Target: ${goal.target}</span>
                    </div>
                </div>
                <div class="goal-actions">
                    <button class="goal-action-btn goal-progress-btn" data-goal-id="${goal.id}">
                        ${isCompleted ? '✅ Completed' : '📈 Update Progress'}
                    </button>
                    <button class="goal-action-btn goal-delete-btn" data-goal-id="${goal.id}">🗑️</button>
                </div>
            </div>
        `;
    },

    // Render goals overview for dashboard
    renderGoalsOverview() {
        const container = document.getElementById('goalsOverview');
        if (!container) return;

        const goals = Storage.getGoals();

        if (goals.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="padding: 15px;">
                    <div class="empty-state-text">No goals set</div>
                </div>
            `;
            return;
        }

        container.innerHTML = goals.slice(0, 3).map(goal => {
            const color = goal.progress >= 100 ? '#10b981' : '#6366f1';
            return `
                <div class="goal-overview-item">
                    <div class="goal-overview-name">${goal.title}</div>
                    <div class="goal-overview-bar">
                        <div class="goal-overview-fill" style="width: ${goal.progress}%; background: ${color}"></div>
                    </div>
                </div>
            `;
        }).join('');
    },

    // Show add goal modal
    showAddModal() {
        const modalContent = {
            title: 'Add New Goal',
            body: `
                <div class="form-group">
                    <label class="form-label">Goal Title</label>
                    <input type="text" class="form-input" id="goalTitle" placeholder="e.g., Run a marathon">
                </div>
                <div class="form-group">
                    <label class="form-label">Target Value</label>
                    <input type="text" class="form-input" id="goalTarget" placeholder="e.g., 42 km, $5000, Read 20 books">
                </div>
                <div class="form-group">
                    <label class="form-label">Deadline (optional)</label>
                    <input type="date" class="form-input" id="goalDeadline">
                </div>
                <div class="form-group">
                    <label class="form-label">Description (optional)</label>
                    <textarea class="form-textarea" id="goalDescription" placeholder="Describe your goal..."></textarea>
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="Goals.addGoal()">Add Goal</button>
            `
        };

        App.showModal(modalContent);
    },

    // Add new goal
    addGoal() {
        const title = document.getElementById('goalTitle')?.value.trim();
        const target = document.getElementById('goalTarget')?.value.trim();
        const deadline = document.getElementById('goalDeadline')?.value;
        const description = document.getElementById('goalDescription')?.value.trim();

        if (!title) {
            App.showToast('Please enter a goal title', 'error');
            return;
        }

        if (!target) {
            App.showToast('Please enter a target value', 'error');
            return;
        }

        Storage.addGoal({
            title,
            target,
            deadline,
            description
        });

        App.closeModal();
        App.showToast('Goal created!', 'success');
        this.render();
        App.updateDashboard();

        // Check for first goal achievement
        const goals = Storage.getGoals();
        if (goals.length === 1) {
            Achievements.unlock('first_goal');
        }
    },

    // Show progress update modal
    showProgressModal(goalId) {
        const goals = Storage.getGoals();
        const goal = goals.find(g => g.id === goalId);
        if (!goal) return;

        const modalContent = {
            title: 'Update Progress',
            body: `
                <div class="form-group">
                    <label class="form-label">Current Progress (%)</label>
                    <input type="number" class="form-input" id="goalProgress" value="${goal.progress}" min="0" max="100">
                </div>
                <div class="form-group">
                    <label class="form-label">Current Value</label>
                    <input type="text" class="form-input" id="goalCurrent" placeholder="e.g., 21 km">
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="Goals.updateProgress('${goalId}')">Update</button>
            `
        };

        App.showModal(modalContent);
    },

    // Update goal progress
    updateProgress(goalId) {
        const progress = parseInt(document.getElementById('goalProgress')?.value);
        const current = document.getElementById('goalCurrent')?.value.trim();

        if (isNaN(progress) || progress < 0 || progress > 100) {
            App.showToast('Please enter a valid progress (0-100)', 'error');
            return;
        }

        Storage.updateGoal(goalId, { 
            progress,
            currentValue: current
        });

        App.closeModal();
        
        if (progress >= 100) {
            App.showToast('🎉 Goal completed!', 'success');
            Storage.addXP(50);
            App.updateUserStats();
            Achievements.unlock('goal_completed');
            App.celebrate();
        } else {
            App.showToast('Progress updated!', 'success');
        }
        
        this.render();
        App.updateDashboard();
    },

    // Delete goal
    deleteGoal(goalId) {
        if (confirm('Are you sure you want to delete this goal?')) {
            Storage.deleteGoal(goalId);
            App.showToast('Goal deleted', 'warning');
            this.render();
            App.updateDashboard();
        }
    },

    // Get completed goals count
    getCompletedCount() {
        const goals = Storage.getGoals();
        return goals.filter(g => g.progress >= 100).length;
    }
};

// Export for use in other modules
window.Goals = Goals;

