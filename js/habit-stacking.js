/**
 * Habit Stacking Module - UI for BJ Fogg's Tiny Habits methodology
 * Phase 3.1 Implementation
 * 
 * Key Features:
 * - Create and manage habit stacks
 * - Visual chain diagram
 * - Stack completion tracking
 * - SRBAI survey for automaticity
 */

const HabitStacking = {
    // Anchor presets based on BJ Fogg's research
    anchorPresets: [
        // Morning anchors
        { id: 'anchor_wake', name: 'Wake up', description: 'After I wake up', category: 'morning', icon: '🌅' },
        { id: 'anchor_alarm', name: 'Turn off alarm', description: 'After I turn off my alarm', category: 'morning', icon: '⏰' },
        { id: 'anchor_brush', name: 'Brush teeth', description: 'After I brush my teeth', category: 'hygiene', icon: '🦷' },
        { id: 'anchor_coffee', name: 'Brew coffee', description: 'After I brew my coffee', category: 'morning', icon: '☕' },
        { id: 'anchor_shower', name: 'Shower', description: 'After I finish my shower', category: 'hygiene', icon: '🚿' },
        // Transit anchors
        { id: 'anchor_car', name: 'Start car', description: 'After I start my car', category: 'transit', icon: '🚗' },
        { id: 'anchor_desk', name: 'Arrive at desk', description: 'After I sit down at my desk', category: 'work', icon: '🪑' },
        { id: 'anchor_door', name: 'Enter home', description: 'After I walk through my front door', category: 'transit', icon: '🚪' },
        // Meal anchors
        { id: 'anchor_breakfast', name: 'Finish breakfast', description: 'After I finish eating breakfast', category: 'meal', icon: '🥣' },
        { id: 'anchor_lunch', name: 'Finish lunch', description: 'After I finish eating lunch', category: 'meal', icon: '🍽️' },
        { id: 'anchor_dinner', name: 'Finish dinner', description: 'After I finish eating dinner', category: 'meal', icon: '🍽️' },
        // Evening anchors
        { id: 'anchor_dishes', name: 'Wash dishes', description: 'After I finish washing dishes', category: 'evening', icon: '🧽' },
        { id: 'anchor_pajamas', name: 'Put on pajamas', description: 'After I put on my pajamas', category: 'evening', icon: '👕' },
        { id: 'anchor_lights', name: 'Turn off lights', description: 'After I turn off the lights', category: 'evening', icon: '💡' },
        { id: 'anchor_bed', name: 'Get into bed', description: 'After I get into bed', category: 'evening', icon: '🛏️' },
        // Exercise anchors
        { id: 'anchor_workout', name: 'Finish workout', description: 'After I finish my workout', category: 'exercise', icon: '💪' }
    ],

    // Category colors
    categoryColors: {
        morning: '#f59e0b',
        hygiene: '#06b6d4',
        transit: '#3b82f6',
        work: '#6366f1',
        meal: '#10b981',
        evening: '#8b5cf6',
        exercise: '#ef4444',
        custom: '#64748b'
    },

    // Initialize module
    init() {
        this.bindEvents();
        this.render();
    },

    // Bind event listeners
    bindEvents() {
        document.getElementById('addStackBtn')?.addEventListener('click', () => {
            this.showAddStackModal();
        });
    },

    // Main render function
    render() {
        this.renderStacksList();
        this.renderStackAnalytics();
    },

    // Render list of habit stacks
    renderStacksList() {
        const container = document.getElementById('stacksContainer');
        if (!container) return;

        const stacks = Storage.getHabitStacks();
        
        if (stacks.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🔗</div>
                    <div class="empty-state-text">No habit stacks yet. Start chaining habits together!</div>
                    <button class="add-btn" onclick="HabitStacking.showAddStackModal()">+ Create Your First Stack</button>
                </div>
            `;
            return;
        }

        container.innerHTML = stacks.map(stack => this.createStackCard(stack)).join('');
        
        // Bind stack card events
        container.querySelectorAll('.stack-start-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const stackId = e.currentTarget.dataset.stackId;
                this.startStack(stackId);
            });
        });

        container.querySelectorAll('.stack-edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const stackId = e.currentTarget.dataset.stackId;
                this.showEditStackModal(stackId);
            });
        });

        container.querySelectorAll('.stack-delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const stackId = e.currentTarget.dataset.stackId;
                this.deleteStack(stackId);
            });
        });

        container.querySelectorAll('.stack-toggle').forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                const stackId = e.currentTarget.dataset.stackId;
                this.toggleStack(stackId, e.target.checked);
            });
        });
    },

    // Create stack card HTML
    createStackCard(stack) {
        const habits = Storage.getHabits();
        const stackHabits = (stack.items || []).map(item => {
            return habits.find(h => h.id === item.habit_id);
        }).filter(h => h);

        const categoryColor = this.categoryColors[stack.anchor_category] || this.categoryColors.custom;
        const completions = Storage.getStackCompletions().filter(c => c.stack_id === stack.id);
        const conversionRate = this.calculateConversionRate(stack, completions);

        return `
            <div class="stack-card ${stack.is_active ? '' : 'inactive'}" data-stack-id="${stack.id}">
                <div class="stack-header">
                    <div class="stack-icon" style="background: ${categoryColor}20; color: ${categoryColor}">
                        ${this.getCategoryIcon(stack.anchor_category)}
                    </div>
                    <div class="stack-info">
                        <h3 class="stack-name">${stack.name}</h3>
                        <p class="stack-trigger">${stack.trigger_description}</p>
                    </div>
                    <div class="stack-controls">
                        <label class="toggle-switch">
                            <input type="checkbox" class="stack-toggle" data-stack-id="${stack.id}" ${stack.is_active ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                </div>
                
                <div class="stack-chain">
                    ${this.renderChainDiagram(stackHabits, stack)}
                </div>
                
                <div class="stack-stats">
                    <div class="stack-stat">
                        <span class="stat-value">${stackHabits.length}</span>
                        <span class="stat-label">Habits</span>
                    </div>
                    <div class="stack-stat">
                        <span class="stat-value">${conversionRate}%</span>
                        <span class="stat-label">Conversion</span>
                    </div>
                    <div class="stack-stat">
                        <span class="stat-value">${completions.length}</span>
                        <span class="stat-label">Completions</span>
                    </div>
                </div>
                
                <div class="stack-actions">
                    <button class="stack-btn stack-start-btn" data-stack-id="${stack.id}">
                        ▶️ Start Stack
                    </button>
                    <button class="stack-btn stack-edit-btn" data-stack-id="${stack.id}">
                        ✏️ Edit
                    </button>
                    <button class="stack-btn stack-delete-btn" data-stack-id="${stack.id}">
                        🗑️
                    </button>
                </div>
            </div>
        `;
    },

    // Render visual chain diagram
    renderChainDiagram(habits, stack) {
        if (habits.length === 0) {
            return '<div class="chain-empty">No habits in this stack</div>';
        }

        const today = Storage.getTodayString();
        
        return habits.map((habit, index) => {
            const isCompleted = Storage.isHabitCompletedOnDate(habit.id, today);
            const item = stack.items?.find(i => i.habit_id === habit.id);
            const delay = item?.delay_seconds || 0;
            
            return `
                <div class="chain-item ${isCompleted ? 'completed' : ''}" data-habit-id="${habit.id}">
                    <div class="chain-node">
                        <div class="chain-icon">${habit.icon}</div>
                        ${index < habits.length - 1 ? '<div class="chain-arrow">→</div>' : ''}
                    </div>
                    <div class="chain-label">${habit.name}</div>
                    ${delay > 0 ? `<div class="chain-delay">+${delay}s</div>` : ''}
                    ${isCompleted ? '<div class="chain-check">✓</div>' : ''}
                </div>
            `;
        }).join('');
    },

    // Get icon for category
    getCategoryIcon(category) {
        const icons = {
            morning: '🌅',
            hygiene: '🧼',
            transit: '🚗',
            work: '💼',
            meal: '🍽️',
            evening: '🌙',
            exercise: '💪',
            custom: '📌'
        };
        return icons[category] || icons.custom;
    },

    // Calculate conversion rate
    calculateConversionRate(stack, completions) {
        if (completions.length === 0) return 0;
        const totalRate = completions.reduce((sum, c) => sum + (c.conversion_rate || 0), 0);
        return Math.round((totalRate / completions.length) * 100);
    },

    // Show add stack modal
    showAddStackModal() {
        const habits = Storage.getHabits();
        
        const modalContent = {
            title: 'Create Habit Stack',
            body: `
                <div class="form-group">
                    <label class="form-label">Stack Name</label>
                    <input type="text" class="form-input" id="stackName" placeholder="e.g., Morning Routine">
                </div>
                
                <div class="form-group">
                    <label class="form-label">Anchor (Trigger)</label>
                    <select class="form-select" id="stackAnchor">
                        <option value="">Select an anchor...</option>
                        ${this.anchorPresets.map(anchor => `
                            <option value="${anchor.id}" data-description="${anchor.description}" data-category="${anchor.category}">
                                ${anchor.icon} ${anchor.name} - ${anchor.description}
                            </option>
                        `).join('')}
                        <option value="custom">✏️ Custom anchor...</option>
                    </select>
                </div>
                
                <div class="form-group" id="customAnchorGroup" style="display: none;">
                    <label class="form-label">Custom Anchor Description</label>
                    <input type="text" class="form-input" id="customAnchor" placeholder="e.g., After I feed my cat...">
                </div>
                
                <div class="form-group">
                    <label class="form-label">Select Habits (in order)</label>
                    <div class="habit-selector" id="habitSelector">
                        ${habits.map(habit => `
                            <div class="habit-selector-item" data-habit-id="${habit.id}">
                                <input type="checkbox" id="habit_${habit.id}" class="habit-checkbox">
                                <label for="habit_${habit.id}" class="habit-selector-label">
                                    <span class="habit-icon">${habit.icon}</span>
                                    <span class="habit-name">${habit.name}</span>
                                </label>
                                <select class="habit-position" data-habit-id="${habit.id}">
                                    ${habits.map((_, i) => `<option value="${i + 1}">${i + 1}</option>`).join('')}
                                </select>
                            </div>
                        `).join('')}
                    </div>
                    ${habits.length === 0 ? '<p class="form-hint">No habits available. Create some habits first!</p>' : ''}
                </div>
                
                <div class="form-group">
                    <label class="form-label">Selected Habits Order</label>
                    <div class="selected-habits-preview" id="selectedHabitsPreview">
                        <p class="form-hint">Select habits above to see the order</p>
                    </div>
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="HabitStacking.createStack()">Create Stack</button>
            `
        };

        App.showModal(modalContent);

        // Bind anchor change event
        document.getElementById('stackAnchor').addEventListener('change', (e) => {
            const customGroup = document.getElementById('customAnchorGroup');
            customGroup.style.display = e.target.value === 'custom' ? 'block' : 'none';
        });

        // Bind habit selection events
        document.querySelectorAll('.habit-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateSelectedHabitsPreview());
        });
        document.querySelectorAll('.habit-position').forEach(select => {
            select.addEventListener('change', () => this.updateSelectedHabitsPreview());
        });
    },

    // Update selected habits preview
    updateSelectedHabitsPreview() {
        const container = document.getElementById('selectedHabitsPreview');
        const habits = Storage.getHabits();
        
        const selected = [];
        document.querySelectorAll('.habit-checkbox:checked').forEach(checkbox => {
            const habitId = checkbox.dataset.habitId || checkbox.id.replace('habit_', '');
            const positionSelect = document.querySelector(`.habit-position[data-habit-id="${habitId}"]`);
            const habit = habits.find(h => h.id === habitId);
            if (habit) {
                selected.push({
                    ...habit,
                    position: parseInt(positionSelect?.value || 1)
                });
            }
        });

        if (selected.length === 0) {
            container.innerHTML = '<p class="form-hint">Select habits above to see the order</p>';
            return;
        }

        selected.sort((a, b) => a.position - b.position);
        container.innerHTML = `
            <div class="selected-habits-chain">
                ${selected.map((h, i) => `
                    <div class="selected-habit-item">
                        <span class="position">${i + 1}</span>
                        <span class="icon">${h.icon}</span>
                        <span class="name">${h.name}</span>
                        ${i < selected.length - 1 ? '<span class="arrow">→</span>' : ''}
                    </div>
                `).join('')}
            </div>
        `;
    },

    // Create new stack
    createStack() {
        const name = document.getElementById('stackName')?.value.trim();
        const anchorSelect = document.getElementById('stackAnchor');
        const anchorId = anchorSelect?.value;
        
        if (!name) {
            App.showToast('Please enter a stack name', 'error');
            return;
        }

        if (!anchorId) {
            App.showToast('Please select an anchor', 'error');
            return;
        }

        // Get anchor details
        let anchorDescription, anchorCategory;
        if (anchorId === 'custom') {
            anchorDescription = document.getElementById('customAnchor')?.value.trim();
            anchorCategory = 'custom';
            if (!anchorDescription) {
                App.showToast('Please enter a custom anchor description', 'error');
                return;
            }
        } else {
            const selectedOption = anchorSelect.options[anchorSelect.selectedIndex];
            anchorDescription = selectedOption.dataset.description;
            anchorCategory = selectedOption.dataset.category;
        }

        // Get selected habits
        const habits = Storage.getHabits();
        const items = [];
        document.querySelectorAll('.habit-checkbox:checked').forEach(checkbox => {
            const habitId = checkbox.dataset.habitId || checkbox.id.replace('habit_', '');
            const positionSelect = document.querySelector(`.habit-position[data-habit-id="${habitId}"]`);
            items.push({
                habit_id: habitId,
                position_index: parseInt(positionSelect?.value || 1) - 1
            });
        });

        if (items.length === 0) {
            App.showToast('Please select at least one habit', 'error');
            return;
        }

        // Sort by position
        items.sort((a, b) => a.position_index - b.position_index);
        
        // Re-index
        items.forEach((item, i) => {
            item.position_index = i;
        });

        const stack = Storage.addHabitStack({
            name,
            trigger_description: anchorDescription,
            anchor_category: anchorCategory,
            items
        });

        App.closeModal();
        App.showToast('Habit stack created!', 'success');
        this.render();
    },

    // Show edit stack modal
    showEditStackModal(stackId) {
        const stacks = Storage.getHabitStacks();
        const stack = stacks.find(s => s.id === stackId);
        if (!stack) return;

        const habits = Storage.getHabits();
        
        const modalContent = {
            title: 'Edit Habit Stack',
            body: `
                <div class="form-group">
                    <label class="form-label">Stack Name</label>
                    <input type="text" class="form-input" id="stackName" value="${stack.name}">
                </div>
                
                <div class="form-group">
                    <label class="form-label">Anchor (Trigger)</label>
                    <select class="form-select" id="stackAnchor">
                        ${this.anchorPresets.map(anchor => `
                            <option value="${anchor.id}" data-description="${anchor.description}" data-category="${anchor.category}" ${anchor.description === stack.trigger_description ? 'selected' : ''}>
                                ${anchor.icon} ${anchor.name} - ${anchor.description}
                            </option>
                        `).join('')}
                        <option value="custom" ${stack.anchor_category === 'custom' ? 'selected' : ''}>✏️ Custom anchor...</option>
                    </select>
                </div>
                
                <div class="form-group" id="customAnchorGroup" style="display: ${stack.anchor_category === 'custom' ? 'block' : 'none'};">
                    <label class="form-label">Custom Anchor Description</label>
                    <input type="text" class="form-input" id="customAnchor" value="${stack.anchor_category === 'custom' ? stack.trigger_description : ''}">
                </div>
                
                <div class="form-group">
                    <label class="form-label">Habits in Stack</label>
                    <div class="habit-selector" id="habitSelector">
                        ${habits.map(habit => {
                            const isInStack = stack.items?.some(i => i.habit_id === habit.id);
                            const stackItem = stack.items?.find(i => i.habit_id === habit.id);
                            return `
                                <div class="habit-selector-item" data-habit-id="${habit.id}">
                                    <input type="checkbox" id="habit_${habit.id}" class="habit-checkbox" ${isInStack ? 'checked' : ''}>
                                    <label for="habit_${habit.id}" class="habit-selector-label">
                                        <span class="habit-icon">${habit.icon}</span>
                                        <span class="habit-name">${habit.name}</span>
                                    </label>
                                    <select class="habit-position" data-habit-id="${habit.id}">
                                        ${habits.map((_, i) => `<option value="${i + 1}" ${stackItem?.position_index === i ? 'selected' : ''}>${i + 1}</option>`).join('')}
                                    </select>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `,
            footer: `
                <button class="btn btn-danger" onclick="HabitStacking.deleteStack('${stackId}')">Delete</button>
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="HabitStacking.updateStack('${stackId}')">Save Changes</button>
            `
        };

        App.showModal(modalContent);

        // Bind events
        document.getElementById('stackAnchor').addEventListener('change', (e) => {
            document.getElementById('customAnchorGroup').style.display = e.target.value === 'custom' ? 'block' : 'none';
        });
        document.querySelectorAll('.habit-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateSelectedHabitsPreview());
        });
        document.querySelectorAll('.habit-position').forEach(select => {
            select.addEventListener('change', () => this.updateSelectedHabitsPreview());
        });
    },

    // Update stack
    updateStack(stackId) {
        const name = document.getElementById('stackName')?.value.trim();
        const anchorSelect = document.getElementById('stackAnchor');
        const anchorId = anchorSelect?.value;
        
        if (!name) {
            App.showToast('Please enter a stack name', 'error');
            return;
        }

        // Get anchor details
        let anchorDescription, anchorCategory;
        if (anchorId === 'custom') {
            anchorDescription = document.getElementById('customAnchor')?.value.trim();
            anchorCategory = 'custom';
        } else {
            const selectedOption = anchorSelect.options[anchorSelect.selectedIndex];
            anchorDescription = selectedOption.dataset.description;
            anchorCategory = selectedOption.dataset.category;
        }

        // Get selected habits
        const items = [];
        document.querySelectorAll('.habit-checkbox:checked').forEach(checkbox => {
            const habitId = checkbox.dataset.habitId || checkbox.id.replace('habit_', '');
            const positionSelect = document.querySelector(`.habit-position[data-habit-id="${habitId}"]`);
            items.push({
                habit_id: habitId,
                position_index: parseInt(positionSelect?.value || 1) - 1
            });
        });

        items.sort((a, b) => a.position_index - b.position_index);
        items.forEach((item, i) => {
            item.position_index = i;
        });

        Storage.updateHabitStack(stackId, {
            name,
            trigger_description: anchorDescription,
            anchor_category: anchorCategory,
            items
        });

        App.closeModal();
        App.showToast('Stack updated!', 'success');
        this.render();
    },

    // Delete stack
    deleteStack(stackId) {
        if (confirm('Are you sure you want to delete this habit stack?')) {
            Storage.deleteHabitStack(stackId);
            App.closeModal();
            App.showToast('Stack deleted', 'warning');
            this.render();
        }
    },

    // Toggle stack active state
    toggleStack(stackId, isActive) {
        Storage.updateHabitStack(stackId, { is_active: isActive });
        App.showToast(isActive ? 'Stack activated' : 'Stack deactivated', 'info');
    },

    // Start stack (begin completion flow)
    startStack(stackId) {
        const stacks = Storage.getHabitStacks();
        const stack = stacks.find(s => s.id === stackId);
        if (!stack) return;

        const habits = Storage.getHabits();
        const stackHabits = (stack.items || [])
            .sort((a, b) => a.position_index - b.position_index)
            .map(item => habits.find(h => h.id === item.habit_id))
            .filter(h => h);

        if (stackHabits.length === 0) {
            App.showToast('No habits in this stack', 'warning');
            return;
        }

        this.currentStack = {
            stack,
            habits: stackHabits,
            currentIndex: 0,
            completedIds: []
        };

        this.showStackProgressModal();
    },

    // Show stack progress modal
    showStackProgressModal() {
        const { stack, habits, currentIndex, completedIds } = this.currentStack;
        const currentHabit = habits[currentIndex];
        const progress = ((completedIds.length) / habits.length) * 100;

        const modalContent = {
            title: stack.name,
            body: `
                <div class="stack-progress-header">
                    <p class="stack-trigger-text">${stack.trigger_description}</p>
                    <div class="stack-progress-bar">
                        <div class="stack-progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <p class="stack-progress-text">${completedIds.length} / ${habits.length} completed</p>
                </div>
                
                <div class="current-habit-display">
                    <div class="current-habit-icon">${currentHabit.icon}</div>
                    <h3 class="current-habit-name">${currentHabit.name}</h3>
                    <p class="current-habit-prompt">Did you complete this habit?</p>
                </div>
                
                <div class="stack-chain-mini">
                    ${habits.map((h, i) => `
                        <div class="mini-chain-item ${i < currentIndex ? 'completed' : ''} ${i === currentIndex ? 'current' : ''}">
                            <span class="mini-icon">${h.icon}</span>
                        </div>
                    `).join('')}
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="HabitStacking.skipHabit()">Skip</button>
                <button class="btn btn-primary" onclick="HabitStacking.completeCurrentHabit()">✓ Completed</button>
            `
        };

        App.showModal(modalContent);
    },

    // Complete current habit in stack
    completeCurrentHabit() {
        const { habits, currentIndex, completedIds } = this.currentStack;
        const currentHabit = habits[currentIndex];
        
        // Log habit completion
        Storage.logHabitCompletion(currentHabit.id);
        completedIds.push(currentHabit.id);
        
        // Check for reward
        if (Math.random() > 0.7) {
            const reward = Storage.rollForReward();
            if (reward) {
                setTimeout(() => this.showRewardModal(reward), 500);
            }
        }
        
        // Move to next habit or finish
        if (currentIndex < habits.length - 1) {
            this.currentStack.currentIndex++;
            this.showStackProgressModal();
        } else {
            this.finishStack();
        }
    },

    // Skip current habit
    skipHabit() {
        const { habits, currentIndex } = this.currentStack;
        
        if (currentIndex < habits.length - 1) {
            this.currentStack.currentIndex++;
            this.showStackProgressModal();
        } else {
            this.finishStack();
        }
    },

    // Finish stack
    finishStack() {
        const { stack, completedIds } = this.currentStack;
        
        // Record completion
        Storage.addStackCompletion({
            stack_id: stack.id,
            completion_date: Storage.getTodayString(),
            completed_items: completedIds,
            conversion_rate: completedIds.length / this.currentStack.habits.length
        });

        App.closeModal();
        App.showToast(`Stack completed! ${completedIds.length}/${this.currentStack.habits.length} habits done!`, 'success');
        App.celebrate();
        this.render();
        App.updateDashboard();
    },

    // Show reward modal
    showRewardModal(reward) {
        const rarityColors = {
            common: '#6b7280',
            uncommon: '#10b981',
            rare: '#3b82f6',
            legendary: '#f59e0b'
        };

        const modalContent = {
            title: '🎉 Reward Earned!',
            body: `
                <div class="reward-reveal">
                    <div class="reward-icon ${reward.rarity}" style="background: ${rarityColors[reward.rarity]}20; border-color: ${rarityColors[reward.rarity]}">
                        ${reward.icon}
                    </div>
                    <h3 class="reward-name">${reward.name}</h3>
                    <p class="reward-rarity" style="color: ${rarityColors[reward.rarity]}">${reward.rarity.toUpperCase()}</p>
                    <p class="reward-description">${reward.description}</p>
                    <div class="reward-value">+${reward.value} XP</div>
                </div>
            `,
            footer: `
                <button class="btn btn-primary" onclick="App.closeModal()">Awesome!</button>
            `
        };

        App.showModal(modalContent);
    },

    // Render stack analytics
    renderStackAnalytics() {
        const container = document.getElementById('stackAnalytics');
        if (!container) return;

        const stacks = Storage.getHabitStacks();
        const completions = Storage.getStackCompletions();

        if (stacks.length === 0) {
            container.innerHTML = '<p class="empty-state-text">Create stacks to see analytics</p>';
            return;
        }

        // Calculate overall stats
        const totalCompletions = completions.length;
        const avgConversion = completions.length > 0
            ? Math.round((completions.reduce((sum, c) => sum + (c.conversion_rate || 0), 0) / completions.length) * 100)
            : 0;

        // Find weak links
        const weakLinks = this.identifyWeakLinks(stacks, completions);

        container.innerHTML = `
            <div class="analytics-grid">
                <div class="analytics-stat">
                    <div class="analytics-value">${stacks.length}</div>
                    <div class="analytics-label">Active Stacks</div>
                </div>
                <div class="analytics-stat">
                    <div class="analytics-value">${totalCompletions}</div>
                    <div class="analytics-label">Total Completions</div>
                </div>
                <div class="analytics-stat">
                    <div class="analytics-value">${avgConversion}%</div>
                    <div class="analytics-label">Avg Conversion</div>
                </div>
                <div class="analytics-stat">
                    <div class="analytics-value">${weakLinks.length}</div>
                    <div class="analytics-label">Weak Links</div>
                </div>
            </div>
            ${weakLinks.length > 0 ? `
                <div class="weak-links-section">
                    <h4>⚠️ Weak Links Detected</h4>
                    <p class="form-hint">These habits have low completion rates in their stacks:</p>
                    <ul class="weak-links-list">
                        ${weakLinks.map(link => `
                            <li>${link.habitName} in "${link.stackName}" (${link.rate}% completion)</li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
    },

    // Identify weak links in stacks
    identifyWeakLinks(stacks, completions) {
        const weakLinks = [];
        const habits = Storage.getHabits();
        const threshold = 0.6;

        stacks.forEach(stack => {
            const stackCompletions = completions.filter(c => c.stack_id === stack.id);
            if (stackCompletions.length < 3) return; // Need enough data

            (stack.items || []).forEach(item => {
                const completionRate = stackCompletions.filter(c => 
                    c.completed_items?.includes(item.habit_id)
                ).length / stackCompletions.length;

                if (completionRate < threshold) {
                    const habit = habits.find(h => h.id === item.habit_id);
                    weakLinks.push({
                        habitId: item.habit_id,
                        habitName: habit?.name || 'Unknown',
                        stackId: stack.id,
                        stackName: stack.name,
                        rate: Math.round(completionRate * 100)
                    });
                }
            });
        });

        return weakLinks;
    },

    // Show SRBAI survey (after 14 days of habit streak)
    showSRBAISurvey(habitId) {
        const habits = Storage.getHabits();
        const habit = habits.find(h => h.id === habitId);
        if (!habit) return;

        const modalContent = {
            title: 'Habit Automaticity Survey',
            body: `
                <p class="form-hint">You've been working on "${habit.name}" for 14 days! Let's check your progress.</p>
                <p class="survey-instruction">Rate each statement from 1 (Strongly Disagree) to 7 (Strongly Agree)</p>
                
                <div class="survey-questions">
                    <div class="survey-question">
                        <p>I do this automatically</p>
                        <div class="survey-scale">
                            ${[1,2,3,4,5,6,7].map(n => `
                                <label class="scale-option">
                                    <input type="radio" name="q1" value="${n}" required>
                                    <span>${n}</span>
                                </label>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="survey-question">
                        <p>I do this without thinking</p>
                        <div class="survey-scale">
                            ${[1,2,3,4,5,6,7].map(n => `
                                <label class="scale-option">
                                    <input type="radio" name="q2" value="${n}" required>
                                    <span>${n}</span>
                                </label>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="survey-question">
                        <p>I start doing this without realizing</p>
                        <div class="survey-scale">
                            ${[1,2,3,4,5,6,7].map(n => `
                                <label class="scale-option">
                                    <input type="radio" name="q3" value="${n}" required>
                                    <span>${n}</span>
                                </label>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="survey-question">
                        <p>It would be difficult not to do this</p>
                        <div class="survey-scale">
                            ${[1,2,3,4,5,6,7].map(n => `
                                <label class="scale-option">
                                    <input type="radio" name="q4" value="${n}" required>
                                    <span>${n}</span>
                                </label>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `,
            footer: `
                <button class="btn btn-primary" onclick="HabitStacking.submitSRBAI('${habitId}')">Submit Survey</button>
            `
        };

        App.showModal(modalContent);
    },

    // Submit SRBAI survey
    submitSRBAI(habitId) {
        const q1 = parseInt(document.querySelector('input[name="q1"]:checked')?.value);
        const q2 = parseInt(document.querySelector('input[name="q2"]:checked')?.value);
        const q3 = parseInt(document.querySelector('input[name="q3"]:checked')?.value);
        const q4 = parseInt(document.querySelector('input[name="q4"]:checked')?.value);

        if (!q1 || !q2 || !q3 || !q4) {
            App.showToast('Please answer all questions', 'error');
            return;
        }

        const score = (q1 + q2 + q3 + q4) / 4;
        const isHabitFormed = score >= 5.5;

        Storage.addSRBAIResult({
            habit_id: habitId,
            survey_date: Storage.getTodayString(),
            q1_automatic: q1,
            q2_without_thinking: q2,
            q3_start_unintentionally: q3,
            q4_difficult_not_to_do: q4,
            automaticity_score: score,
            is_habit_formed: isHabitFormed
        });

        App.closeModal();

        if (isHabitFormed) {
            App.showToast(`🎉 Congratulations! "${habit.name}" has become a habit!`, 'success');
            App.celebrate();
        } else {
            App.showToast(`Keep going! Your automaticity score is ${score.toFixed(1)}/7`, 'info');
        }
    }
};

// Export for use in other modules
window.HabitStacking = HabitStacking;