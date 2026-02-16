/**
 * Enhanced Goals Module - Advanced goal tracking with conditions and variables
 */

const EnhancedGoals = {
    // Initialize enhanced goals module
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
                    <button class="add-btn" onclick="EnhancedGoals.showAddModal()">+ Add Goal</button>
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

        container.querySelectorAll('.goal-condition-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const goalId = e.currentTarget.dataset.goalId;
                this.showConditionModal(goalId);
            });
        });

        container.querySelectorAll('.goal-delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const goalId = e.currentTarget.dataset.goalId;
                this.deleteGoal(goalId);
            });
        });
    },

    // Create enhanced goal card HTML
    createGoalCard(goal) {
        const deadline = goal.deadline
            ? new Date(goal.deadline).toLocaleDateString()
            : 'No deadline';

        const isCompleted = goal.progress >= 100;
        
        // Format goal conditions display
        let conditionsDisplay = '';
        if (goal.conditions && goal.conditions.length > 0) {
            conditionsDisplay = `
                <div class="goal-conditions">
                    ${goal.conditions.map(condition => this.formatCondition(condition)).join('')}
                </div>
            `;
        }

        return `
            <div class="goal-card ${isCompleted ? 'completed' : ''}">
                <div class="goal-header">
                    <div class="goal-title">${goal.title}</div>
                    <div class="goal-deadline">📅 ${deadline}</div>
                </div>
                <div class="goal-description">
                    ${goal.description || ''}
                </div>
                ${conditionsDisplay}
                <div class="goal-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${goal.progress}%"></div>
                    </div>
                    <div class="progress-text">
                        <span>${goal.progress}% complete</span>
                        <span>Target: ${goal.target}</span>
                    </div>
                </div>
                <div class="goal-streak">
                    🔥 Streak: ${goal.streak || 0} days
                </div>
                <div class="goal-actions">
                    <button class="goal-action-btn goal-progress-btn" data-goal-id="${goal.id}">
                        ${isCompleted ? '✅ Completed' : '📈 Update Progress'}
                    </button>
                    <button class="goal-action-btn goal-condition-btn" data-goal-id="${goal.id}">
                        ⚙️ Conditions
                    </button>
                    <button class="goal-action-btn goal-delete-btn" data-goal-id="${goal.id}">🗑️</button>
                </div>
            </div>
        `;
    },

    // Format condition for display
    formatCondition(condition) {
        if (condition.type === 'COMPARISON') {
            return `
                <div class="condition-item">
                    <span class="condition-operator">${condition.operator}</span>
                    <span class="condition-target">${condition.target}</span>
                </div>
            `;
        } else if (condition.type === 'GOAL_MET') {
            return `
                <div class="condition-item">
                    <span class="condition-goal">Depends on: ${condition.goalName}</span>
                </div>
            `;
        }
        return '';
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
                    <div class="goal-overview-streak">🔥 ${goal.streak || 0}</div>
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
                
                <!-- Goal Conditions Section -->
                <div class="form-group">
                    <label class="form-label">Goal Conditions</label>
                    <div class="goal-conditions-section">
                        <div class="condition-row">
                            <select class="form-select condition-type" id="conditionType">
                                <option value="COMPARISON">Comparison</option>
                                <option value="GOAL_MET">Goal Met</option>
                            </select>
                            
                            <select class="form-select condition-operator" id="conditionOperator" style="display: inline-block; width: auto;">
                                <option value="GREATER_THAN">Greater Than</option>
                                <option value="LESS_THAN">Less Than</option>
                                <option value="EQUAL">Equal To</option>
                                <option value="GREATER_THAN_EQUAL">Greater Than or Equal</option>
                                <option value="LESS_THAN_EQUAL">Less Than or Equal</option>
                            </select>
                            
                            <input type="text" class="form-input condition-target" id="conditionTarget" placeholder="Target value" style="display: inline-block; width: auto;">
                        </div>
                        
                        <button type="button" class="btn btn-small" id="addConditionBtn">+ Add Condition</button>
                        
                        <div class="existing-conditions" id="existingConditionsList">
                            <!-- Existing conditions will be added here -->
                        </div>
                    </div>
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="EnhancedGoals.addGoal()">Add Goal</button>
            `
        };

        App.showModal(modalContent);
        
        // Bind condition events
        document.getElementById('addConditionBtn')?.addEventListener('click', () => {
            this.addConditionToList();
        });
    },

    // Add condition to the list in modal
    addConditionToList() {
        const type = document.getElementById('conditionType')?.value;
        const operator = document.getElementById('conditionOperator')?.value;
        const target = document.getElementById('conditionTarget')?.value;

        if (!target) {
            App.showToast('Please enter a target value for the condition', 'error');
            return;
        }

        const conditionId = 'cond_' + Date.now();
        const conditionHtml = `
            <div class="added-condition" data-id="${conditionId}">
                <span>${type} - ${operator} - ${target}</span>
                <button type="button" class="btn btn-danger btn-small remove-condition" data-id="${conditionId}">Remove</button>
                <input type="hidden" name="condition" value='${JSON.stringify({id: conditionId, type, operator, target})}'>
            </div>
        `;

        const listContainer = document.getElementById('existingConditionsList');
        if (listContainer) {
            listContainer.insertAdjacentHTML('beforeend', conditionHtml);
            
            // Add event listener to remove button
            document.querySelector(`[data-id="${conditionId}"] .remove-condition`).addEventListener('click', (e) => {
                const id = e.currentTarget.dataset.id;
                document.querySelector(`[data-id="${id}"]`).remove();
            });
        }

        // Clear inputs
        document.getElementById('conditionTarget').value = '';
    },

    // Add new goal with conditions
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

        // Collect conditions
        const conditionElements = document.querySelectorAll('.added-condition input[type="hidden"]');
        const conditions = Array.from(conditionElements).map(el => JSON.parse(el.value));

        Storage.addGoal({
            title,
            target,
            deadline,
            description,
            conditions: conditions,
            progress: 0,
            streak: 0,
            currentValue: 0
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
                    <input type="text" class="form-input" id="goalCurrent" value="${goal.currentValue || ''}" placeholder="e.g., 21 km">
                </div>
                <div class="form-group">
                    <label class="form-label">Streak Days</label>
                    <input type="number" class="form-input" id="goalStreak" value="${goal.streak || 0}" min="0">
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="EnhancedGoals.updateProgress('${goalId}')">Update</button>
            `
        };

        App.showModal(modalContent);
    },

    // Update goal progress
    updateProgress(goalId) {
        const progress = parseInt(document.getElementById('goalProgress')?.value);
        const current = document.getElementById('goalCurrent')?.value.trim();
        const streak = parseInt(document.getElementById('goalStreak')?.value);

        if (isNaN(progress) || progress < 0 || progress > 100) {
            App.showToast('Please enter a valid progress (0-100)', 'error');
            return;
        }

        if (isNaN(streak) || streak < 0) {
            App.showToast('Please enter a valid streak value', 'error');
            return;
        }

        Storage.updateGoal(goalId, {
            progress,
            currentValue: current,
            streak
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

    // Show condition management modal
    showConditionModal(goalId) {
        const goals = Storage.getGoals();
        const goal = goals.find(g => g.id === goalId);
        if (!goal) return;

        const conditionsHtml = goal.conditions && goal.conditions.length > 0 
            ? goal.conditions.map(cond => `
                <div class="condition-item">
                    <span>${cond.type} - ${cond.operator || 'N/A'} - ${cond.target || cond.goalName || 'N/A'}</span>
                    <button class="btn btn-danger btn-small" onclick="EnhancedGoals.removeCondition('${goalId}', '${cond.id}')">Remove</button>
                </div>
              `).join('')
            : '<div class="no-conditions">No conditions defined</div>';

        const modalContent = {
            title: 'Manage Goal Conditions',
            body: `
                <div class="form-group">
                    <label class="form-label">Goal: ${goal.title}</label>
                </div>
                <div class="form-group">
                    <label class="form-label">Existing Conditions</label>
                    <div class="existing-conditions-list">
                        ${conditionsHtml}
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Add New Condition</label>
                    <div class="condition-row">
                        <select class="form-select condition-type" id="newConditionType">
                            <option value="COMPARISON">Comparison</option>
                            <option value="GOAL_MET">Goal Met</option>
                        </select>
                        
                        <select class="form-select condition-operator" id="newConditionOperator">
                            <option value="GREATER_THAN">Greater Than</option>
                            <option value="LESS_THAN">Less Than</option>
                            <option value="EQUAL">Equal To</option>
                            <option value="GREATER_THAN_EQUAL">Greater Than or Equal</option>
                            <option value="LESS_THAN_EQUAL">Less Than or Equal</option>
                        </select>
                        
                        <input type="text" class="form-input condition-target" id="newConditionTarget" placeholder="Target value">
                    </div>
                    
                    <button type="button" class="btn btn-small" onclick="EnhancedGoals.addConditionToGoal('${goalId}')">+ Add Condition</button>
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="App.closeModal()">Close</button>
            `
        };

        App.showModal(modalContent);
    },

    // Add condition to a specific goal
    addConditionToGoal(goalId) {
        const type = document.getElementById('newConditionType')?.value;
        const operator = document.getElementById('newConditionOperator')?.value;
        const target = document.getElementById('newConditionTarget')?.value;

        if (!target) {
            App.showToast('Please enter a target value for the condition', 'error');
            return;
        }

        const goals = Storage.getGoals();
        const goal = goals.find(g => g.id === goalId);
        if (!goal) return;

        const newCondition = {
            id: 'cond_' + Date.now(),
            type,
            operator,
            target
        };

        goal.conditions = goal.conditions || [];
        goal.conditions.push(newCondition);

        Storage.updateGoal(goalId, { conditions: goal.conditions });

        App.showToast('Condition added!', 'success');
        this.showConditionModal(goalId); // Refresh the modal
    },

    // Remove condition from a goal
    removeCondition(goalId, conditionId) {
        const goals = Storage.getGoals();
        const goal = goals.find(g => g.id === goalId);
        if (!goal) return;

        goal.conditions = goal.conditions.filter(cond => cond.id !== conditionId);

        Storage.updateGoal(goalId, { conditions: goal.conditions });

        App.showToast('Condition removed!', 'success');
        this.showConditionModal(goalId); // Refresh the modal
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

    // Evaluate if goal conditions are met
    areGoalConditionsMet(goal, currentValue) {
        if (!goal.conditions || goal.conditions.length === 0) {
            // If no conditions, just check if progress is 100%
            return goal.progress >= 100;
        }

        // Evaluate each condition
        for (const condition of goal.conditions) {
            if (condition.type === 'COMPARISON') {
                const targetValue = this.parseValue(condition.target);
                const actualValue = this.parseValue(currentValue);

                if (targetValue === null || actualValue === null) {
                    continue; // Skip if values are not valid
                }

                switch (condition.operator) {
                    case 'EQUAL':
                        if (actualValue !== targetValue) return false;
                        break;
                    case 'NOT_EQUAL':
                        if (actualValue === targetValue) return false;
                        break;
                    case 'GREATER_THAN':
                        if (actualValue <= targetValue) return false;
                        break;
                    case 'GREATER_THAN_EQUAL':
                        if (actualValue < targetValue) return false;
                        break;
                    case 'LESS_THAN':
                        if (actualValue >= targetValue) return false;
                        break;
                    case 'LESS_THAN_EQUAL':
                        if (actualValue > targetValue) return false;
                        break;
                }
            } else if (condition.type === 'GOAL_MET') {
                // Check if another goal is met
                const dependentGoal = this.getGoalById(condition.goalVariableId);
                if (!dependentGoal || !this.areGoalConditionsMet(dependentGoal, dependentGoal.currentValue)) {
                    return false;
                }
            }
            // Add more condition types as needed
        }

        return true;
    },

    // Parse a value from string to number
    parseValue(value) {
        if (typeof value === 'number') {
            return value;
        }
        if (typeof value === 'string') {
            const parsed = parseFloat(value);
            return isNaN(parsed) ? null : parsed;
        }
        return null;
    },

    // Get goal by ID
    getGoalById(goalId) {
        const goals = Storage.getGoals();
        return goals.find(g => g.id === goalId);
    },

    // Evaluate goal progress based on conditions
    evaluateGoalProgress(goal) {
        if (!goal.conditions || goal.conditions.length === 0) {
            // If no conditions, return the stored progress
            return goal.progress || 0;
        }

        // For now, we'll calculate progress based on how many conditions are met
        let metConditions = 0;
        for (const condition of goal.conditions) {
            // This is a simplified evaluation - in a real implementation,
            // you would evaluate the condition against actual data
            if (this.evaluateCondition(goal, condition)) {
                metConditions++;
            }
        }

        // Return percentage of conditions met
        return Math.min(100, Math.round((metConditions / goal.conditions.length) * 100));
    },

    // Evaluate a single condition
    evaluateCondition(goal, condition) {
        if (condition.type === 'COMPARISON') {
            const targetValue = this.parseValue(condition.target);
            const actualValue = this.parseValue(goal.currentValue);

            if (targetValue === null || actualValue === null) {
                return false; // Can't evaluate
            }

            switch (condition.operator) {
                case 'EQUAL':
                    return actualValue === targetValue;
                case 'NOT_EQUAL':
                    return actualValue !== targetValue;
                case 'GREATER_THAN':
                    return actualValue > targetValue;
                case 'GREATER_THAN_EQUAL':
                    return actualValue >= targetValue;
                case 'LESS_THAN':
                    return actualValue < targetValue;
                case 'LESS_THAN_EQUAL':
                    return actualValue <= targetValue;
                default:
                    return false;
            }
        } else if (condition.type === 'GOAL_MET') {
            // Check if another goal is met
            const dependentGoal = this.getGoalById(condition.goalVariableId);
            return dependentGoal ? this.areGoalConditionsMet(dependentGoal, dependentGoal.currentValue) : false;
        }

        return false;
    },

    // Update goal progress based on conditions
    updateGoalProgressBasedOnConditions(goalId) {
        const goals = Storage.getGoals();
        const goal = goals.find(g => g.id === goalId);
        
        if (!goal) return;

        // Calculate progress based on conditions
        const newProgress = this.evaluateGoalProgress(goal);
        
        // Update the goal with the new progress
        Storage.updateGoal(goalId, { progress: newProgress });
    },

    // Get completed goals count
    getCompletedCount() {
        const goals = Storage.getGoals();
        return goals.filter(g => g.progress >= 100).length;
    },

    // Calculate goal streak based on recent progress
    calculateStreak(goalId) {
        // This is a simplified version - in a real implementation, 
        // you would track daily progress and calculate consecutive days
        const goals = Storage.getGoals();
        const goal = goals.find(g => g.id === goalId);
        if (!goal) return 0;

        // For now, return the stored streak value
        return goal.streak || 0;
    },

    // Calculate advanced streak based on goal conditions
    calculateAdvancedStreak(goalId) {
        const goals = Storage.getGoals();
        const goal = goals.find(g => g.id === goalId);
        if (!goal) return 0;

        // If no conditions, use traditional streak calculation
        if (!goal.conditions || goal.conditions.length === 0) {
            return this.calculateTraditionalStreak(goalId);
        }

        // Calculate streak based on goal conditions being met
        return this.calculateConditionBasedStreak(goal);
    },

    // Calculate traditional streak (consecutive days with progress)
    calculateTraditionalStreak(goalId) {
        // For now, return the stored streak value
        // In a real implementation, you would track daily progress
        const goals = Storage.getGoals();
        const goal = goals.find(g => g.id === goalId);
        return goal.streak || 0;
    },

    // Calculate streak based on conditions being met
    calculateConditionBasedStreak(goal) {
        // This would typically involve checking historical data
        // to see how many consecutive days/periods the goal conditions were met
        
        // For now, we'll simulate this by checking if recent progress values meet conditions
        // In a real implementation, you would have historical data to check
        
        // Placeholder implementation - in reality, you'd check historical data
        // to see how many consecutive periods the goal conditions were satisfied
        let streak = goal.streak || 0;
        
        // Simulate checking recent history to determine if conditions were met
        // This is a simplified version - real implementation would check actual historical data
        if (this.areGoalConditionsMet(goal, goal.currentValue)) {
            // If current conditions are met, increment streak if it's continuing
            streak = Math.max(streak, 1);
        } else {
            // If current conditions aren't met, reset streak
            streak = 0;
        }
        
        return streak;
    },

    // Update goal streak based on conditions
    updateGoalStreak(goalId) {
        const goals = Storage.getGoals();
        const goal = goals.find(g => g.id === goalId);
        if (!goal) return;

        // Calculate the new streak value
        const newStreak = this.calculateAdvancedStreak(goalId);

        // Update the goal with the new streak
        Storage.updateGoal(goalId, { streak: newStreak });
    },

    // Calculate streak considering weekdays (similar to perfice approach)
    calculateStreakWithWeekdays(goalId, weekDays = null) {
        const goals = Storage.getGoals();
        const goal = goals.find(g => g.id === goalId);
        if (!goal) return 0;

        // If weekDays is specified, only count streak on those days
        // This is similar to perfice's approach where goals can be set for specific days
        if (weekDays && weekDays.length > 0) {
            // In a real implementation, you would check historical data
            // and only count streak days that fall on the specified weekDays
            return this.calculateConditionBasedStreak(goal);
        }

        // Otherwise, use standard streak calculation
        return this.calculateConditionBasedStreak(goal);
    }
};

// Export for use in other modules
window.EnhancedGoals = EnhancedGoals;