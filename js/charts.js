/**
 * Charts Module - Handles all Chart.js visualizations
 */

const Charts = {
    // Chart instances
    instances: {},
    
    // Real-time update interval reference
    updateInterval: null,
    
    // Real-time update frequency (in milliseconds)
    UPDATE_FREQUENCY: 30000, // 30 seconds
    
    // Last data state for change detection
    lastDataState: null,

    // Default chart options
    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            }
        }
    },

    // Color palette
    colors: {
        primary: '#6366f1',
        purple: '#a855f7',
        blue: '#3b82f6',
        cyan: '#06b6d4',
        green: '#10b981',
        yellow: '#f59e0b',
        orange: '#f97316',
        red: '#ef4444',
        pink: '#ec4899'
    },

    // Get gradient colors
    getGradient(ctx, color1, color2) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        return gradient;
    },

    // Initialize weekly progress chart (Dashboard)
    initWeeklyChart(canvasId, viewType = 'daily') {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');

        // Destroy existing instance
        if (this.instances.weekly) {
            this.instances.weekly.destroy();
        }

        let labels = [];
        let habitData = [];
        let taskData = [];

        if (viewType === 'weekly') {
            // Get last 7 days data
            for (let i = 6; i >= 0; i--) {
                const date = new Date();
                date.setDate(date.getDate() - i);
                labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }));

                // Calculate completion rate for habits
                const dateStr = Storage.getDateString(date);
                const logs = Storage.getHabitLogs();
                const habits = Storage.getHabits();
                const completedHabits = logs[dateStr]?.length || 0;
                const habitRate = habits.length > 0 ? (completedHabits / habits.length) * 100 : 0;
                habitData.push(habitRate);

                // Calculate task completion
                const tasks = Storage.getTasks();
                const completedTasks = tasks.filter(t =>
                    t.completed && Storage.isSameDay(t.completedAt || t.createdAt, date)
                ).length;
                taskData.push(completedTasks);
            }
        } else if (viewType === 'monthly') {
            // Get last 4 weeks data
            for (let i = 3; i >= 0; i--) {
                const startDate = new Date();
                startDate.setDate(startDate.getDate() - (i * 7));
                const endDate = new Date(startDate);
                endDate.setDate(endDate.getDate() + 6);
                
                // Format label as "Week X" or date range
                labels.push(`Week ${i + 1}`);

                // Calculate completion rate for habits for the week
                let weeklyHabitCompletions = 0;
                let totalPossibleHabitCompletions = 0;
                
                // Loop through each day in the week
                for (let j = 0; j < 7; j++) {
                    const date = new Date(startDate);
                    date.setDate(date.getDate() + j);
                    const dateStr = Storage.getDateString(date);
                    
                    const logs = Storage.getHabitLogs();
                    const habits = Storage.getHabits();
                    const completedHabits = logs[dateStr]?.length || 0;
                    
                    weeklyHabitCompletions += completedHabits;
                    totalPossibleHabitCompletions += habits.length;
                }
                
                const habitRate = totalPossibleHabitCompletions > 0 ? 
                    (weeklyHabitCompletions / totalPossibleHabitCompletions) * 100 : 0;
                habitData.push(habitRate);

                // Calculate task completion for the week
                const tasks = Storage.getTasks();
                const completedTasks = tasks.filter(t => {
                    if (!t.completed) return false;
                    const taskDate = new Date(t.completedAt || t.createdAt);
                    return taskDate >= startDate && taskDate <= endDate;
                }).length;
                taskData.push(completedTasks);
            }
        } else { // daily view (default)
            // Get last 7 days data
            for (let i = 6; i >= 0; i--) {
                const date = new Date();
                date.setDate(date.getDate() - i);
                labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }));

                // Calculate completion rate for habits
                const dateStr = Storage.getDateString(date);
                const logs = Storage.getHabitLogs();
                const habits = Storage.getHabits();
                const completedHabits = logs[dateStr]?.length || 0;
                const habitRate = habits.length > 0 ? (completedHabits / habits.length) * 100 : 0;
                habitData.push(habitRate);

                // Calculate task completion
                const tasks = Storage.getTasks();
                const completedTasks = tasks.filter(t =>
                    t.completed && Storage.isSameDay(t.completedAt || t.createdAt, date)
                ).length;
                taskData.push(completedTasks);
            }
        }

        this.instances.weekly = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Habits %',
                        data: habitData,
                        borderColor: this.colors.primary,
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointBackgroundColor: this.colors.primary
                    },
                    {
                        label: 'Tasks',
                        data: taskData,
                        borderColor: this.colors.green,
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointBackgroundColor: this.colors.green
                    }
                ]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        max: 100,
                        ticks: {
                            callback: value => value + '%'
                        }
                    }
                }
            }
        });

        return this.instances.weekly;
    },

    // Initialize expenses chart (Finances)
    initExpensesChart(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');
        
        // Destroy existing instance
        if (this.instances.expenses) {
            this.instances.expenses.destroy();
        }

        // Get expenses by category
        const transactions = Storage.getTransactions();
        const expensesByCategory = {};
        
        transactions
            .filter(t => t.type === 'expense')
            .forEach(t => {
                const category = t.category || 'other';
                expensesByCategory[category] = (expensesByCategory[category] || 0) + t.amount;
            });

        const categories = Object.keys(expensesByCategory);
        const amounts = Object.values(expensesByCategory);
        
        const categoryColors = {
            food: this.colors.orange,
            transport: this.colors.blue,
            entertainment: this.colors.purple,
            shopping: this.colors.pink,
            bills: this.colors.red,
            health: this.colors.green,
            other: this.colors.cyan
        };

        const backgroundColors = categories.map(c => categoryColors[c] || this.colors.primary);

        if (categories.length === 0) {
            // Show empty state
            this.instances.expenses = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['No expenses'],
                    datasets: [{
                        data: [1],
                        backgroundColor: ['#e2e8f0']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        } else {
            this.instances.expenses = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: categories.map(c => c.charAt(0).toUpperCase() + c.slice(1)),
                    datasets: [{
                        data: amounts,
                        backgroundColor: backgroundColors,
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom'
                        }
                    }
                }
            });
        }

        return this.instances.expenses;
    },

    // Initialize weight chart (Health)
    initWeightChart(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');
        
        if (this.instances.weight) {
            this.instances.weight.destroy();
        }

        const health = Storage.getHealthData();
        const weightData = health.weight.slice(-14); // Last 14 entries

        this.instances.weight = new Chart(ctx, {
            type: 'line',
            data: {
                labels: weightData.map(d => {
                    const date = new Date(d.date);
                    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                }),
                datasets: [{
                    data: weightData.map(d => d.value),
                    borderColor: this.colors.blue,
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3
                }]
            },
            options: {
                ...this.defaultOptions,
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        ticks: {
                            callback: value => value + ' kg'
                        }
                    }
                }
            }
        });

        return this.instances.weight;
    },

    // Initialize sleep chart (Health)
    initSleepChart(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');
        
        if (this.instances.sleep) {
            this.instances.sleep.destroy();
        }

        const health = Storage.getHealthData();
        const sleepData = health.sleep.slice(-14);

        this.instances.sleep = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: sleepData.map(d => {
                    const date = new Date(d.date);
                    return date.toLocaleDateString('en-US', { weekday: 'short' });
                }),
                datasets: [{
                    data: sleepData.map(d => d.value),
                    backgroundColor: this.colors.purple,
                    borderRadius: 4
                }]
            },
            options: {
                ...this.defaultOptions,
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        max: 12,
                        ticks: {
                            callback: value => value + 'h'
                        }
                    }
                }
            }
        });

        return this.instances.sleep;
    },

    // Initialize mood chart (Health)
    initMoodChart(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');
        
        if (this.instances.mood) {
            this.instances.mood.destroy();
        }

        const health = Storage.getHealthData();
        const moodData = health.mood.slice(-14);

        const moodColors = {
            5: this.colors.green,
            4: '#86efac',
            3: this.colors.yellow,
            2: this.colors.orange,
            1: this.colors.red
        };

        this.instances.mood = new Chart(ctx, {
            type: 'line',
            data: {
                labels: moodData.map(d => {
                    const date = new Date(d.date);
                    return date.toLocaleDateString('en-US', { weekday: 'short' });
                }),
                datasets: [{
                    data: moodData.map(d => d.value),
                    borderColor: this.colors.pink,
                    backgroundColor: moodData.map(d => moodColors[d.value] || this.colors.primary),
                    fill: false,
                    tension: 0.4,
                    pointRadius: 6,
                    pointBackgroundColor: moodData.map(d => moodColors[d.value] || this.colors.primary)
                }]
            },
            options: {
                ...this.defaultOptions,
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        min: 0,
                        max: 5,
                        ticks: {
                            stepSize: 1,
                            callback: value => {
                                const moods = ['', '😢', '😕', '😐', '🙂', '😄'];
                                return moods[value] || '';
                            }
                        }
                    }
                }
            }
        });

        return this.instances.mood;
    },

    // Initialize time distribution chart (Time)
    initTimeChart(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');
        
        if (this.instances.time) {
            this.instances.time.destroy();
        }

        // Get today's time entries
        const entries = Storage.getTimeEntries();
        const todayStr = Storage.getTodayString();
        const todayEntries = entries.filter(e => e.date === todayStr);

        // Aggregate by category
        const timeByCategory = {};
        todayEntries.forEach(e => {
            timeByCategory[e.category] = (timeByCategory[e.category] || 0) + e.duration;
        });

        const categoryLabels = {
            work: '💼 Work',
            study: '📚 Study',
            exercise: '🏃 Exercise',
            leisure: '🎮 Leisure',
            other: '📌 Other'
        };

        const categoryColors = {
            work: this.colors.blue,
            study: this.colors.purple,
            exercise: this.colors.green,
            leisure: this.colors.pink,
            other: this.colors.cyan
        };

        const categories = Object.keys(timeByCategory);
        const durations = Object.values(timeByCategory);

        if (categories.length === 0) {
            this.instances.time = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['No data'],
                    datasets: [{
                        data: [1],
                        backgroundColor: ['#e2e8f0']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        } else {
            this.instances.time = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: categories.map(c => categoryLabels[c] || c),
                    datasets: [{
                        data: durations,
                        backgroundColor: categories.map(c => categoryColors[c] || this.colors.primary),
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom'
                        },
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    const minutes = context.raw;
                                    const hours = Math.floor(minutes / 60);
                                    const mins = minutes % 60;
                                    return `${hours}h ${mins}m`;
                                }
                            }
                        }
                    }
                }
            });
        }

        return this.instances.time;
    },

    // Update all charts
    updateAll() {
        // Get current view type from the active button
        const activeViewBtn = document.querySelector('.view-toggle .view-btn.active');
        const viewType = activeViewBtn ? activeViewBtn.dataset.viewType : 'daily';

        this.initWeeklyChart('weeklyChart', viewType);
        this.initExpensesChart('expensesChart');
        this.initWeightChart('weightChart');
        this.initSleepChart('sleepChart');
        this.initMoodChart('moodChart');
        this.initTimeChart('timeChart');
        this.initFinancialTrendsChart('financialTrendsChart');
        
        // Also initialize monthly chart if it exists
        const monthlyChartEl = document.getElementById('monthlyChart');
        if (monthlyChartEl) {
            this.initMonthlyChart('monthlyChart', viewType);
        }
    },
    
    // Update specific chart
    updateChart(chartId, viewType = 'daily') {
        switch(chartId) {
            case 'weeklyChart':
                this.initWeeklyChart(chartId, viewType);
                break;
            case 'expensesChart':
                this.initExpensesChart(chartId);
                break;
            case 'weightChart':
                this.initWeightChart(chartId);
                break;
            case 'sleepChart':
                this.initSleepChart(chartId);
                break;
            case 'moodChart':
                this.initMoodChart(chartId);
                break;
            case 'timeChart':
                this.initTimeChart(chartId);
                break;
        }
    },

    // Initialize monthly progress chart (Dashboard)
    initMonthlyChart(canvasId, viewType = 'monthly') {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');

        // Destroy existing instance
        if (this.instances.monthly) {
            this.instances.monthly.destroy();
        }

        // Get last 12 months data
        const labels = [];
        const habitData = [];
        const taskData = [];

        for (let i = 11; i >= 0; i--) {
            const date = new Date();
            date.setMonth(date.getMonth() - i);
            labels.push(date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }));

            // Calculate completion rate for habits for the month
            let monthlyHabitCompletions = 0;
            let totalPossibleHabitCompletions = 0;
            
            // Get number of days in the month
            const year = date.getFullYear();
            const month = date.getMonth();
            const daysInMonth = new Date(year, month + 1, 0).getDate();
            
            for (let day = 1; day <= daysInMonth; day++) {
                const checkDate = new Date(year, month, day);
                const dateStr = Storage.getDateString(checkDate);
                
                const logs = Storage.getHabitLogs();
                const habits = Storage.getHabits();
                const completedHabits = logs[dateStr]?.length || 0;
                
                monthlyHabitCompletions += completedHabits;
                totalPossibleHabitCompletions += habits.length;
            }
            
            const habitRate = totalPossibleHabitCompletions > 0 ? 
                (monthlyHabitCompletions / totalPossibleHabitCompletions) * 100 : 0;
            habitData.push(habitRate);

            // Calculate task completion for the month
            const tasks = Storage.getTasks();
            const monthStart = new Date(year, month, 1);
            const monthEnd = new Date(year, month + 1, 0);
            
            const completedTasks = tasks.filter(t => {
                if (!t.completed) return false;
                const taskDate = new Date(t.completedAt || t.createdAt);
                return taskDate >= monthStart && taskDate <= monthEnd;
            }).length;
            taskData.push(completedTasks);
        }

        this.instances.monthly = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Habits %',
                        data: habitData,
                        backgroundColor: this.getGradient(ctx, 'rgba(99, 102, 241, 0.8)', 'rgba(99, 102, 241, 0.4)'),
                        borderColor: this.colors.primary,
                        borderWidth: 1,
                        borderRadius: 4
                    },
                    {
                        label: 'Tasks',
                        data: taskData,
                        backgroundColor: this.getGradient(ctx, 'rgba(16, 185, 129, 0.8)', 'rgba(16, 185, 129, 0.4)'),
                        borderColor: this.colors.green,
                        borderWidth: 1,
                        borderRadius: 4
                    }
                ]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        max: 100,
                        ticks: {
                            callback: value => value + '%'
                        }
                    }
                }
            }
        });

        return this.instances.monthly;
    },

    // Initialize financial trends chart (Finances)
    initFinancialTrendsChart(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');

        // Destroy existing instance
        if (this.instances.financialTrends) {
            this.instances.financialTrends.destroy();
        }

        // Get last 6 months data
        const labels = [];
        const incomeData = [];
        const expenseData = [];

        for (let i = 5; i >= 0; i--) {
            const date = new Date();
            date.setMonth(date.getMonth() - i);
            labels.push(date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }));

            // Calculate income and expenses for the month
            const year = date.getFullYear();
            const month = date.getMonth();
            const transactions = Storage.getTransactions();
            
            const monthTransactions = transactions.filter(t => {
                const tDate = new Date(t.date || t.createdAt);
                return tDate.getFullYear() === year && tDate.getMonth() === month;
            });
            
            const monthlyIncome = monthTransactions
                .filter(t => t.type === 'income')
                .reduce((sum, t) => sum + t.amount, 0);
            
            const monthlyExpenses = monthTransactions
                .filter(t => t.type === 'expense')
                .reduce((sum, t) => sum + t.amount, 0);
            
            incomeData.push(monthlyIncome);
            expenseData.push(monthlyExpenses);
        }

        this.instances.financialTrends = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Income',
                        data: incomeData,
                        borderColor: this.colors.green,
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointBackgroundColor: this.colors.green
                    },
                    {
                        label: 'Expenses',
                        data: expenseData,
                        borderColor: this.colors.red,
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointBackgroundColor: this.colors.red
                    }
                ]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        ticks: {
                            callback: value => '$' + value.toLocaleString()
                        }
                    }
                }
            }
        });

        return this.instances.financialTrends;
    },

    // Destroy all chart instances
    destroyAll() {
        Object.values(this.instances).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.instances = {};
    },
    
    // Get current data state for change detection
    getCurrentDataState() {
        try {
            const habits = Storage.getHabits();
            const tasks = Storage.getTasks();
            const transactions = Storage.getTransactions();
            const health = Storage.getHealthData();
            const timeEntries = Storage.getTimeEntries();
            const habitLogs = Storage.getHabitLogs();
            
            return JSON.stringify({
                habitsCount: habits.length,
                tasksCount: tasks.length,
                completedTasks: tasks.filter(t => t.completed).length,
                transactionsCount: transactions.length,
                weightCount: health.weight.length,
                sleepCount: health.sleep.length,
                moodCount: health.mood.length,
                timeEntriesCount: timeEntries.length,
                habitLogsCount: Object.keys(habitLogs).length
            });
        } catch (error) {
            console.error('Error getting data state:', error);
            return null;
        }
    },
    
    // Check if data has changed
    hasDataChanged() {
        const currentState = this.getCurrentDataState();
        if (currentState === null || this.lastDataState === null) {
            this.lastDataState = currentState;
            return false;
        }
        
        const changed = currentState !== this.lastDataState;
        this.lastDataState = currentState;
        return changed;
    },
    
    // Start real-time updates
    startRealTimeUpdates() {
        // Don't start if already running
        if (this.updateInterval) {
            return;
        }
        
        // Initialize last data state
        this.lastDataState = this.getCurrentDataState();
        
        this.updateInterval = setInterval(() => {
            if (this.hasDataChanged()) {
                this.updateAll();
            }
        }, this.UPDATE_FREQUENCY);
        
        console.log('Real-time chart updates started');
    },
    
    // Stop real-time updates
    stopRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
            console.log('Real-time chart updates stopped');
        }
    },
    
    // Force immediate update (useful after data changes)
    forceUpdate() {
        this.lastDataState = this.getCurrentDataState();
        this.updateAll();
    },
    
    // Initialize charts with real-time updates
    initWithRealTime() {
        this.updateAll();
        this.startRealTimeUpdates();
    }
};

// Export for use in other modules
window.Charts = Charts;
