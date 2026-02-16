/**
 * Storage Module - Handles all LocalStorage operations
 * Provides a centralized data persistence layer
 */

const Storage = {
    // Storage keys
    KEYS: {
        HABITS: 'tracklife_habits',
        HABIT_LOGS: 'tracklife_habit_logs',
        TASKS: 'tracklife_tasks',
        TRANSACTIONS: 'tracklife_transactions',
        BUDGETS: 'tracklife_budgets',
        HEALTH: 'tracklife_health',
        TIME_ENTRIES: 'tracklife_time_entries',
        GOALS: 'tracklife_goals',
        ACHIEVEMENTS: 'tracklife_achievements',
        USER_DATA: 'tracklife_user',
        SETTINGS: 'tracklife_settings'
    },

    // Generic save method
    save(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Storage save error:', error);
            return false;
        }
    },

    // Generic load method
    load(key, defaultValue = null) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : defaultValue;
        } catch (error) {
            console.error('Storage load error:', error);
            return defaultValue;
        }
    },

    // Generic delete method
    remove(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Storage remove error:', error);
            return false;
        }
    },

    // Clear all app data
    clearAll() {
        Object.values(this.KEYS).forEach(key => {
            localStorage.removeItem(key);
        });
    },

    // Generate unique ID
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },

    // Get today's date string (YYYY-MM-DD)
    getTodayString() {
        return new Date().toISOString().split('T')[0];
    },

    // Get date string for any date
    getDateString(date) {
        return new Date(date).toISOString().split('T')[0];
    },

    // Check if same day
    isSameDay(date1, date2) {
        const d1 = new Date(date1);
        const d2 = new Date(date2);
        return d1.toDateString() === d2.toDateString();
    },

    // Get days between two dates
    getDaysBetween(date1, date2) {
        const d1 = new Date(date1);
        const d2 = new Date(date2);
        const diffTime = Math.abs(d2 - d1);
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    },

    // User Data Methods
    getUserData() {
        return this.load(this.KEYS.USER_DATA, {
            level: 1,
            xp: 0,
            totalPoints: 0,
            createdAt: new Date().toISOString()
        });
    },

    saveUserData(data) {
        return this.save(this.KEYS.USER_DATA, data);
    },

    addXP(amount) {
        const userData = this.getUserData();
        userData.xp += amount;
        userData.totalPoints += amount;

        // Level up check based on progressive XP requirements
        // Level 1: 0 XP, Level 2: 100 XP, Level 3: 250 XP, Level 4: 400 XP, etc.
        // Each level after level 2 requires 150 more XP than the previous
        let xpForNextLevel = this.getXPForLevel(userData.level + 1);
        
        while (userData.xp >= xpForNextLevel) {
            userData.xp -= xpForNextLevel;
            userData.level++;
            xpForNextLevel = this.getXPForLevel(userData.level + 1);
        }

        this.saveUserData(userData);
        return userData;
    },

    // Calculate total XP required for a specific level
    getXPForLevel(level) {
        if (level <= 1) return 0;
        if (level === 2) return 100;
        // Level 3: 250, Level 4: 400, Level 5: 550, etc.
        return 100 + (level - 2) * 150;
    },
    
    // Calculate progress percentage to next level
    getXpProgressToNextLevel() {
        const userData = this.getUserData();
        const currentLevelXP = this.getXPForLevel(userData.level);
        const nextLevelXP = this.getXPForLevel(userData.level + 1);
        
        if (nextLevelXP === currentLevelXP) return 0; // Level 1 (both are 0)
        
        const xpNeededForNextLevel = nextLevelXP - currentLevelXP;
        const xpEarnedThisLevel = userData.xp;
        
        return (xpEarnedThisLevel / xpNeededForNextLevel) * 100;
    },

    // Settings Methods
    getSettings() {
        return this.load(this.KEYS.SETTINGS, {
            theme: 'light',
            notifications: true,
            soundEffects: true
        });
    },

    saveSettings(settings) {
        return this.save(this.KEYS.SETTINGS, settings);
    },

    // Habits Methods
    getHabits() {
        return this.load(this.KEYS.HABITS, []);
    },

    saveHabits(habits) {
        return this.save(this.KEYS.HABITS, habits);
    },

    addHabit(habit) {
        const habits = this.getHabits();
        habit.id = this.generateId();
        habit.createdAt = new Date().toISOString();
        habits.push(habit);
        this.saveHabits(habits);
        return habit;
    },

    updateHabit(id, updates) {
        const habits = this.getHabits();
        const index = habits.findIndex(h => h.id === id);
        if (index !== -1) {
            habits[index] = { ...habits[index], ...updates };
            this.saveHabits(habits);
            return habits[index];
        }
        return null;
    },

    deleteHabit(id) {
        const habits = this.getHabits();
        const filtered = habits.filter(h => h.id !== id);
        this.saveHabits(filtered);
        return true;
    },

    // Habit Logs Methods
    getHabitLogs() {
        return this.load(this.KEYS.HABIT_LOGS, {});
    },

    saveHabitLogs(logs) {
        return this.save(this.KEYS.HABIT_LOGS, logs);
    },

    logHabitCompletion(habitId, date = null) {
        const logs = this.getHabitLogs();
        const dateStr = date || this.getTodayString();
        
        if (!logs[dateStr]) {
            logs[dateStr] = [];
        }
        
        if (!logs[dateStr].includes(habitId)) {
            logs[dateStr].push(habitId);
            this.saveHabitLogs(logs);
        }
        
        return logs;
    },

    unlogHabitCompletion(habitId, date = null) {
        const logs = this.getHabitLogs();
        const dateStr = date || this.getTodayString();
        
        if (logs[dateStr]) {
            logs[dateStr] = logs[dateStr].filter(id => id !== habitId);
            this.saveHabitLogs(logs);
        }
        
        return logs;
    },

    isHabitCompletedOnDate(habitId, date = null) {
        const logs = this.getHabitLogs();
        const dateStr = date || this.getTodayString();
        return logs[dateStr]?.includes(habitId) || false;
    },

    getHabitStreak(habitId) {
        const logs = this.getHabitLogs();
        let streak = 0;
        let currentDate = new Date();
        
        // Check if completed today, if not start from yesterday
        const todayStr = this.getTodayString();
        if (!logs[todayStr]?.includes(habitId)) {
            currentDate.setDate(currentDate.getDate() - 1);
        }
        
        while (true) {
            const dateStr = this.getDateString(currentDate);
            if (logs[dateStr]?.includes(habitId)) {
                streak++;
                currentDate.setDate(currentDate.getDate() - 1);
            } else {
                break;
            }
        }
        
        return streak;
    },

    // Tasks Methods
    getTasks() {
        return this.load(this.KEYS.TASKS, []);
    },

    saveTasks(tasks) {
        return this.save(this.KEYS.TASKS, tasks);
    },

    addTask(task) {
        const tasks = this.getTasks();
        task.id = this.generateId();
        task.createdAt = new Date().toISOString();
        task.completed = false;
        tasks.push(task);
        this.saveTasks(tasks);
        return task;
    },

    updateTask(id, updates) {
        const tasks = this.getTasks();
        const index = tasks.findIndex(t => t.id === id);
        if (index !== -1) {
            tasks[index] = { ...tasks[index], ...updates };
            this.saveTasks(tasks);
            return tasks[index];
        }
        return null;
    },

    deleteTask(id) {
        const tasks = this.getTasks();
        const filtered = tasks.filter(t => t.id !== id);
        this.saveTasks(filtered);
        return true;
    },

    // Transactions Methods
    getTransactions() {
        return this.load(this.KEYS.TRANSACTIONS, []);
    },

    saveTransactions(transactions) {
        return this.save(this.KEYS.TRANSACTIONS, transactions);
    },

    addTransaction(transaction) {
        const transactions = this.getTransactions();
        transaction.id = this.generateId();
        transaction.createdAt = new Date().toISOString();
        transactions.unshift(transaction);
        this.saveTransactions(transactions);
        return transaction;
    },

    deleteTransaction(id) {
        const transactions = this.getTransactions();
        const filtered = transactions.filter(t => t.id !== id);
        this.saveTransactions(filtered);
        return true;
    },

    // Budgets Methods
    getBudgets() {
        return this.load(this.KEYS.BUDGETS, []);
    },

    saveBudgets(budgets) {
        return this.save(this.KEYS.BUDGETS, budgets);
    },

    // Health Methods
    getHealthData() {
        return this.load(this.KEYS.HEALTH, {
            weight: [],
            sleep: [],
            mood: []
        });
    },

    saveHealthData(data) {
        return this.save(this.KEYS.HEALTH, data);
    },

    addHealthEntry(type, value, date = null) {
        const health = this.getHealthData();
        const entry = {
            value,
            date: date || this.getTodayString(),
            timestamp: new Date().toISOString()
        };
        
        // Remove existing entry for same date
        health[type] = health[type].filter(e => e.date !== entry.date);
        health[type].push(entry);
        
        // Sort by date
        health[type].sort((a, b) => new Date(a.date) - new Date(b.date));
        
        this.saveHealthData(health);
        return entry;
    },

    // Time Entries Methods
    getTimeEntries() {
        return this.load(this.KEYS.TIME_ENTRIES, []);
    },

    saveTimeEntries(entries) {
        return this.save(this.KEYS.TIME_ENTRIES, entries);
    },

    addTimeEntry(entry) {
        const entries = this.getTimeEntries();
        entry.id = this.generateId();
        entry.createdAt = new Date().toISOString();
        entries.unshift(entry);
        this.saveTimeEntries(entries);
        return entry;
    },

    deleteTimeEntry(id) {
        const entries = this.getTimeEntries();
        const filtered = entries.filter(e => e.id !== id);
        this.saveTimeEntries(filtered);
        return true;
    },

    // Goals Methods
    getGoals() {
        return this.load(this.KEYS.GOALS, []);
    },

    saveGoals(goals) {
        return this.save(this.KEYS.GOALS, goals);
    },

    addGoal(goal) {
        const goals = this.getGoals();
        goal.id = this.generateId();
        goal.createdAt = new Date().toISOString();
        goal.progress = goal.progress || 0;
        goal.streak = goal.streak || 0;
        goal.conditions = goal.conditions || [];
        goal.currentValue = goal.currentValue || 0;
        goals.push(goal);
        this.saveGoals(goals);
        return goal;
    },

    updateGoal(id, updates) {
        const goals = this.getGoals();
        const index = goals.findIndex(g => g.id === id);
        if (index !== -1) {
            // Preserve existing conditions if not provided in updates
            const existingGoal = goals[index];
            const updatedGoal = { ...existingGoal, ...updates };
            
            // Ensure conditions array exists
            updatedGoal.conditions = updates.conditions !== undefined 
                ? (updates.conditions || []) 
                : (existingGoal.conditions || []);
                
            // Ensure streak and progress are maintained appropriately
            updatedGoal.streak = updates.streak !== undefined 
                ? (updates.streak || 0) 
                : (existingGoal.streak || 0);
                
            updatedGoal.progress = updates.progress !== undefined 
                ? (updates.progress || 0) 
                : (existingGoal.progress || 0);
                
            updatedGoal.currentValue = updates.currentValue !== undefined 
                ? (updates.currentValue || 0) 
                : (existingGoal.currentValue || 0);

            goals[index] = updatedGoal;
            this.saveGoals(goals);
            return goals[index];
        }
        return null;
    },

    deleteGoal(id) {
        const goals = this.getGoals();
        const filtered = goals.filter(g => g.id !== id);
        this.saveGoals(filtered);
        return true;
    },

    // Achievements Methods
    getAchievements() {
        return this.load(this.KEYS.ACHIEVEMENTS, []);
    },

    saveAchievements(achievements) {
        return this.save(this.KEYS.ACHIEVEMENTS, achievements);
    },

    unlockAchievement(achievementId) {
        const achievements = this.getAchievements();
        if (!achievements.includes(achievementId)) {
            achievements.push({
                id: achievementId,
                unlockedAt: new Date().toISOString()
            });
            this.saveAchievements(achievements);
            return true;
        }
        return false;
    },

    isAchievementUnlocked(achievementId) {
        const achievements = this.getAchievements();
        return achievements.some(a => a.id === achievementId);
    }
};

// Export for use in other modules
window.Storage = Storage;