/**
 * Tasks Module - Handles task/todo management
 */

const Tasks = {
    // Priority levels
    priorities: ['low', 'medium', 'high'],

    // Categories
    categories: ['personal', 'work', 'study', 'health', 'other'],

    // Current filter
    currentFilter: 'all',

    // Initialize tasks module
    init() {
        this.bindEvents();
        this.render();
    },

    // Bind event listeners
    bindEvents() {
        // Add task button
        const addTaskBtn = document.getElementById('addTaskBtn');
        if (addTaskBtn) {
            const newAddBtn = addTaskBtn.cloneNode(true);
            addTaskBtn.parentNode.replaceChild(newAddBtn, addTaskBtn);
            newAddBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showAddModal();
            });
        }

        // Filter buttons - only bind once
        document.querySelectorAll('.filter-btn:not([data-bound])').forEach(btn => {
            btn.setAttribute('data-bound', 'true');
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentFilter = e.target.dataset.filter;
                this.render();
            });
        });
    },

    // Render tasks list
    render() {
        this.renderTasksList();
        this.renderQuickTasks();
    },

    // Render main tasks list
    renderTasksList() {
        const container = document.getElementById('tasksContainer');
        if (!container) return;

        let tasks = Storage.getTasks();

        // Apply filter
        if (this.currentFilter === 'active') {
            tasks = tasks.filter(t => !t.completed);
        } else if (this.currentFilter === 'completed') {
            tasks = tasks.filter(t => t.completed);
        }

        // Sort by priority and completion
        tasks.sort((a, b) => {
            if (a.completed !== b.completed) return a.completed ? 1 : -1;
            const priorityOrder = { high: 0, medium: 1, low: 2 };
            return priorityOrder[a.priority] - priorityOrder[b.priority];
        });

        if (tasks.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📋</div>
                    <div class="empty-state-text">${this.currentFilter === 'all' ? 'No tasks yet. Add your first task!' : 'No ' + this.currentFilter + ' tasks'}</div>
                    <button class="add-btn" onclick="Tasks.showAddModal()">+ Add Task</button>
                </div>
            `;
            return;
        }

        container.innerHTML = tasks.map(task => this.createTaskCard(task)).join('');

        // Bind task events
        container.querySelectorAll('.task-checkbox').forEach(checkbox => {
            checkbox.addEventListener('click', (e) => {
                const taskId = e.currentTarget.dataset.taskId;
                this.toggleTask(taskId);
            });
        });

        container.querySelectorAll('.task-edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const taskId = e.currentTarget.dataset.taskId;
                this.showEditModal(taskId);
            });
        });

        container.querySelectorAll('.task-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const taskId = e.currentTarget.dataset.taskId;
                this.deleteTask(taskId);
            });
        });
    },

    // Create task card HTML
    createTaskCard(task) {
        const priorityClass = `priority-${task.priority}`;
        const dueDate = task.dueDate ? new Date(task.dueDate).toLocaleDateString() : '';
        const isOverdue = task.dueDate && new Date(task.dueDate) < new Date() && !task.completed;

        return `
            <div class="task-card ${task.completed ? 'completed' : ''}" data-task-id="${task.id}">
                <div class="task-checkbox ${task.completed ? 'checked' : ''}" data-task-id="${task.id}">
                    ${task.completed ? '✓' : ''}
                </div>
                <div class="task-content">
                    <div class="task-title">${task.title}</div>
                    <div class="task-meta">
                        ${task.priority ? `<span class="task-priority ${priorityClass}">${task.priority}</span>` : ''}
                        ${task.category ? `<span class="task-category">${task.category}</span>` : ''}
                        ${dueDate ? `<span class="${isOverdue ? 'text-danger' : ''}">📅 ${dueDate}</span>` : ''}
                    </div>
                </div>
                <div class="habit-actions">
                    <button class="habit-action-btn task-edit" data-task-id="${task.id}" title="Edit">✏️</button>
                    <button class="habit-action-btn task-delete" data-task-id="${task.id}" title="Delete">🗑️</button>
                </div>
            </div>
        `;
    },

    // Render quick tasks for dashboard
    renderQuickTasks() {
        const container = document.getElementById('quickTasks');
        if (!container) return;

        const tasks = Storage.getTasks()
            .filter(t => !t.completed)
            .slice(0, 5);

        if (tasks.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="padding: 20px;">
                    <div class="empty-state-text">All tasks completed! 🎉</div>
                </div>
            `;
            return;
        }

        container.innerHTML = tasks.map(task => `
            <div class="quick-task">
                <div class="task-checkbox" data-task-id="${task.id}">
                </div>
                <span class="task-title">${task.title}</span>
                ${task.priority ? `<span class="task-priority priority-${task.priority}">${task.priority}</span>` : ''}
            </div>
        `).join('');

        // Bind quick task checkbox events
        container.querySelectorAll('.task-checkbox').forEach(checkbox => {
            checkbox.addEventListener('click', (e) => {
                const taskId = e.currentTarget.dataset.taskId;
                this.toggleTask(taskId);
            });
        });
    },

    // Toggle task completion
    toggleTask(taskId) {
        const tasks = Storage.getTasks();
        const task = tasks.find(t => t.id === taskId);
        if (!task) return;

        const updates = {
            completed: !task.completed,
            completedAt: !task.completed ? new Date().toISOString() : null
        };

        Storage.updateTask(taskId, updates);

        if (!task.completed) {
            App.showToast('Task completed! +15 XP', 'success');
            Storage.addXP(15);
            App.updateUserStats();

            // Check for task achievements
            const completedTasks = Storage.getTasks().filter(t => t.completed).length;
            if (completedTasks === 10) {
                Achievements.unlock('tasks_10');
            } else if (completedTasks === 50) {
                Achievements.unlock('tasks_50');
            }

            if (Math.random() > 0.8) {
                App.celebrate();
            }
        } else {
            App.showToast('Task unmarked', 'warning');
        }

        this.render();
        App.updateDashboard();
        Charts.updateChart('weeklyChart');
    },

    // Show add task modal
    showAddModal() {
        const today = Storage.getTodayString();
        
        const modalContent = {
            title: 'Add New Task',
            body: `
                <div class="form-group">
                    <label class="form-label">Task Title</label>
                    <input type="text" class="form-input" id="taskTitle" placeholder="What needs to be done?">
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Priority</label>
                        <select class="form-select" id="taskPriority">
                            <option value="low">Low</option>
                            <option value="medium" selected>Medium</option>
                            <option value="high">High</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Category</label>
                        <select class="form-select" id="taskCategory">
                            <option value="personal">Personal</option>
                            <option value="work">Work</option>
                            <option value="study">Study</option>
                            <option value="health">Health</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Due Date</label>
                    <input type="date" class="form-input" id="taskDueDate" value="${today}">
                </div>
                <div class="form-group">
                    <label class="form-label">Notes (optional)</label>
                    <textarea class="form-textarea" id="taskNotes" placeholder="Add any notes..."></textarea>
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="Tasks.addTask()">Add Task</button>
            `
        };

        App.showModal(modalContent);
    },

    // Add new task
    addTask() {
        const title = document.getElementById('taskTitle')?.value.trim();
        const priority = document.getElementById('taskPriority')?.value;
        const category = document.getElementById('taskCategory')?.value;
        const dueDate = document.getElementById('taskDueDate')?.value;
        const notes = document.getElementById('taskNotes')?.value.trim();

        if (!title) {
            App.showToast('Please enter a task title', 'error');
            return;
        }

        Storage.addTask({
            title,
            priority,
            category,
            dueDate,
            notes
        });

        App.closeModal();
        App.showToast('Task created!', 'success');
        this.render();
        App.updateDashboard();

        // Check for first task achievement
        const tasks = Storage.getTasks();
        if (tasks.length === 1) {
            Achievements.unlock('first_task');
        }
    },

    // Show edit task modal
    showEditModal(taskId) {
        const tasks = Storage.getTasks();
        const task = tasks.find(t => t.id === taskId);
        if (!task) return;

        const modalContent = {
            title: 'Edit Task',
            body: `
                <div class="form-group">
                    <label class="form-label">Task Title</label>
                    <input type="text" class="form-input" id="taskTitle" value="${task.title}">
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Priority</label>
                        <select class="form-select" id="taskPriority">
                            <option value="low" ${task.priority === 'low' ? 'selected' : ''}>Low</option>
                            <option value="medium" ${task.priority === 'medium' ? 'selected' : ''}>Medium</option>
                            <option value="high" ${task.priority === 'high' ? 'selected' : ''}>High</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Category</label>
                        <select class="form-select" id="taskCategory">
                            <option value="personal" ${task.category === 'personal' ? 'selected' : ''}>Personal</option>
                            <option value="work" ${task.category === 'work' ? 'selected' : ''}>Work</option>
                            <option value="study" ${task.category === 'study' ? 'selected' : ''}>Study</option>
                            <option value="health" ${task.category === 'health' ? 'selected' : ''}>Health</option>
                            <option value="other" ${task.category === 'other' ? 'selected' : ''}>Other</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Due Date</label>
                    <input type="date" class="form-input" id="taskDueDate" value="${task.dueDate || ''}">
                </div>
                <div class="form-group">
                    <label class="form-label">Notes</label>
                    <textarea class="form-textarea" id="taskNotes">${task.notes || ''}</textarea>
                </div>
            `,
            footer: `
                <button class="btn btn-danger" onclick="Tasks.deleteTask('${taskId}')">Delete</button>
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="Tasks.updateTask('${taskId}')">Save Changes</button>
            `
        };

        App.showModal(modalContent);
    },

    // Update task
    updateTask(taskId) {
        const title = document.getElementById('taskTitle')?.value.trim();
        const priority = document.getElementById('taskPriority')?.value;
        const category = document.getElementById('taskCategory')?.value;
        const dueDate = document.getElementById('taskDueDate')?.value;
        const notes = document.getElementById('taskNotes')?.value.trim();

        if (!title) {
            App.showToast('Please enter a task title', 'error');
            return;
        }

        Storage.updateTask(taskId, { title, priority, category, dueDate, notes });
        App.closeModal();
        App.showToast('Task updated!', 'success');
        this.render();
        App.updateDashboard();
        Charts.updateChart('weeklyChart');
    },

    // Delete task
    deleteTask(taskId) {
        if (confirm('Are you sure you want to delete this task?')) {
            Storage.deleteTask(taskId);
            App.closeModal();
            App.showToast('Task deleted', 'warning');
            this.render();
            App.updateDashboard();
        }
    },

    // Get completed tasks count for today
    getCompletedTodayCount() {
        const tasks = Storage.getTasks();
        const todayStr = Storage.getTodayString();
        return tasks.filter(t => {
            if (!t.completed || !t.completedAt) return false;
            return Storage.getDateString(t.completedAt) === todayStr;
        }).length;
    },

    // Get total active tasks count
    getActiveCount() {
        const tasks = Storage.getTasks();
        return tasks.filter(t => !t.completed).length;
    }
};

// Export for use in other modules
window.Tasks = Tasks;