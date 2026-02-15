/**
 * Achievements Module - Handles achievements and rewards
 */

const Achievements = {
    // All available achievements
    achievements: [
        // Habits
        {
            id: 'first_habit',
            name: 'First Step',
            description: 'Create your first habit',
            icon: '🌱',
            points: 50,
            category: 'habits'
        },
        {
            id: 'streak_7',
            name: 'Week Warrior',
            description: 'Maintain a 7-day streak',
            icon: '🔥',
            points: 100,
            category: 'habits'
        },
        {
            id: 'streak_30',
            name: 'Monthly Master',
            description: 'Maintain a 30-day streak',
            icon: '💎',
            points: 500,
            category: 'habits'
        },
        {
            id: 'habits_5',
            name: 'Habit Builder',
            description: 'Create 5 different habits',
            icon: '🏗️',
            points: 75,
            category: 'habits'
        },

        // Tasks
        {
            id: 'first_task',
            name: 'Task Starter',
            description: 'Create your first task',
            icon: '📝',
            points: 50,
            category: 'tasks'
        },
        {
            id: 'tasks_10',
            name: 'Productive',
            description: 'Complete 10 tasks',
            icon: '⭐',
            points: 100,
            category: 'tasks'
        },
        {
            id: 'tasks_50',
            name: 'Super Productive',
            description: 'Complete 50 tasks',
            icon: '🌟',
            points: 300,
            category: 'tasks'
        },

        // Finances
        {
            id: 'first_transaction',
            name: 'Money Tracker',
            description: 'Log your first transaction',
            icon: '💰',
            points: 50,
            category: 'finances'
        },
        {
            id: 'transactions_10',
            name: 'Finance Pro',
            description: 'Log 10 transactions',
            icon: '📊',
            points: 100,
            category: 'finances'
        },

        // Health
        {
            id: 'mood_week',
            name: 'Mood Master',
            description: 'Log mood for 7 days',
            icon: '😊',
            points: 100,
            category: 'health'
        },
        {
            id: 'health_weight',
            name: 'Weight Watcher',
            description: 'Log weight 5 times',
            icon: '⚖️',
            points: 75,
            category: 'health'
        },

        // Time
        {
            id: 'time_10',
            name: 'Time Tracker',
            description: 'Log 10 time entries',
            icon: '⏱️',
            points: 100,
            category: 'time'
        },

        // Goals
        {
            id: 'first_goal',
            name: 'Goal Setter',
            description: 'Create your first goal',
            icon: '🎯',
            points: 50,
            category: 'goals'
        },
        {
            id: 'goal_completed',
            name: 'Goal Crusher',
            description: 'Complete a goal',
            icon: '🏆',
            points: 200,
            category: 'goals'
        },

        // Level
        {
            id: 'level_5',
            name: 'Rising Star',
            description: 'Reach level 5',
            icon: '⭐⭐⭐',
            points: 0,
            category: 'level'
        },
        {
            id: 'level_10',
            name: 'Superstar',
            description: 'Reach level 10',
            icon: '🌟🌟🌟',
            points: 0,
            category: 'level'
        },
        
        // New achievements added
        {
            id: 'streak_7_consecutive',
            name: 'Consistency King',
            description: 'Complete any habit for 7 consecutive days',
            icon: '👑',
            points: 150,
            category: 'habits'
        },
        {
            id: 'habits_10',
            name: 'Habit Collector',
            description: 'Create 10 different habits',
            icon: '📚',
            points: 150,
            category: 'habits'
        },
        {
            id: 'tasks_100',
            name: 'Task Titan',
            description: 'Complete 100 tasks',
            icon: '🚀',
            points: 500,
            category: 'tasks'
        },
        {
            id: 'finance_saver',
            name: 'Savings Guru',
            description: 'Have more income than expenses for 3 months',
            icon: '🏦',
            points: 300,
            category: 'finances'
        },
        {
            id: 'finance_budget',
            name: 'Budget Master',
            description: 'Set and stick to a budget for 1 month',
            icon: '📈',
            points: 250,
            category: 'finances'
        },
        {
            id: 'health_sleep',
            name: 'Sleep Expert',
            description: 'Log sleep for 30 days',
            icon: '😴',
            points: 200,
            category: 'health'
        },
        {
            id: 'time_100',
            name: 'Time Lord',
            description: 'Log 100 time entries',
            icon: '⏳',
            points: 250,
            category: 'time'
        },
        {
            id: 'goals_5',
            name: 'Goal Getter',
            description: 'Create 5 goals',
            icon: '🎯🎯',
            points: 150,
            category: 'goals'
        },
        {
            id: 'goals_3_completed',
            name: 'Goal Achiever',
            description: 'Complete 3 goals',
            icon: '🏆🏆',
            points: 400,
            category: 'goals'
        },
        {
            id: 'level_15',
            name: 'Legend',
            description: 'Reach level 15',
            icon: '⭐⭐⭐⭐',
            points: 0,
            category: 'level'
        },
        {
            id: 'level_20',
            name: 'Master',
            description: 'Reach level 20',
            icon: '👑',
            points: 0,
            category: 'level'
        },
        {
            id: 'early_bird',
            name: 'Early Bird',
            description: 'Complete 10 tasks before 8 AM',
            icon: '🌅',
            points: 200,
            category: 'productivity'
        },
        {
            id: 'night_owl',
            name: 'Night Owl',
            description: 'Complete 10 tasks after 10 PM',
            icon: '🦉',
            points: 200,
            category: 'productivity'
        },
        {
            id: 'perfect_week',
            name: 'Perfect Week',
            description: 'Complete all habits for 7 consecutive days',
            icon: '⭐',
            points: 300,
            category: 'habits'
        },
        {
            id: 'year_round',
            name: 'Year Round',
            description: 'Maintain a habit for 365 days',
            icon: '📅',
            points: 1000,
            category: 'habits'
        }
    ],

    // Initialize achievements module
    init() {
        this.render();
    },

    // Render achievements view
    render() {
        this.renderAchievementsStats();
        this.renderAchievementsList();
    },

    // Render achievements stats
    renderAchievementsStats() {
        const unlocked = Storage.getAchievements();
        const totalPoints = Storage.getUserData().totalPoints || 0;

        document.getElementById('totalPoints').textContent = totalPoints;
        document.getElementById('badgesEarned').textContent = unlocked.length;
    },

    // Render achievements list
    renderAchievementsList() {
        const container = document.getElementById('achievementsGrid');
        if (!container) return;

        const unlocked = Storage.getAchievements();
        const unlockedIds = unlocked.map(a => a.id);

        container.innerHTML = this.achievements.map(achievement => {
            const isUnlocked = unlockedIds.includes(achievement.id);
            return this.createAchievementBadge(achievement, isUnlocked);
        }).join('');
    },

    // Create achievement badge HTML
    createAchievementBadge(achievement, isUnlocked) {
        return `
            <div class="achievement-badge ${isUnlocked ? '' : 'locked'}">
                <div class="achievement-badge-icon">${achievement.icon}</div>
                <div class="achievement-badge-name">${achievement.name}</div>
                <div class="achievement-badge-desc">${achievement.description}</div>
                ${achievement.points > 0 ? `<div class="achievement-badge-points">+${achievement.points} XP</div>` : ''}
            </div>
        `;
    },

    // Unlock achievement
    unlock(achievementId) {
        const alreadyUnlocked = Storage.isAchievementUnlocked(achievementId);
        
        if (alreadyUnlocked) {
            return false;
        }

        const achievement = this.achievements.find(a => a.id === achievementId);
        if (!achievement) {
            return false;
        }

        Storage.unlockAchievement(achievementId);
        
        if (achievement.points > 0) {
            Storage.addXP(achievement.points);
        }

        App.showToast(`🏆 Achievement Unlocked: ${achievement.name}!`, 'success');
        
        // Re-render
        this.render();
        App.updateUserStats();
        
        // Celebrate
        App.celebrate();

        return true;
    },

    // Check for achievements
    checkAchievements() {
        const habits = Storage.getHabits();
        const tasks = Storage.getTasks().filter(t => t.completed);
        const transactions = Storage.getTransactions();
        const health = Storage.getHealthData();
        const timeEntries = Storage.getTimeEntries();
        const goals = Storage.getGoals();
        const userData = Storage.getUserData();

        // Habits
        if (habits.length >= 1) this.unlock('first_habit');
        if (habits.length >= 5) this.unlock('habits_5');
        if (habits.length >= 10) this.unlock('habits_10');

        // Tasks
        if (tasks.length >= 1) this.unlock('first_task');
        if (tasks.length >= 10) this.unlock('tasks_10');
        if (tasks.length >= 50) this.unlock('tasks_50');
        if (tasks.length >= 100) this.unlock('tasks_100');

        // Finances
        if (transactions.length >= 1) this.unlock('first_transaction');
        if (transactions.length >= 10) this.unlock('transactions_10');

        // Health
        if (health.mood.length >= 7) this.unlock('mood_week');
        if (health.weight.length >= 5) this.unlock('health_weight');
        if (health.sleep.length >= 30) this.unlock('health_sleep');

        // Time
        if (timeEntries.length >= 10) this.unlock('time_10');
        if (timeEntries.length >= 100) this.unlock('time_100');

        // Goals
        if (goals.length >= 1) this.unlock('first_goal');
        if (goals.length >= 5) this.unlock('goals_5');
        const completedGoals = goals.filter(g => g.progress >= 100);
        if (completedGoals.length > 0) this.unlock('goal_completed');
        if (completedGoals.length >= 3) this.unlock('goals_3_completed');

        // Level
        if (userData.level >= 5) this.unlock('level_5');
        if (userData.level >= 10) this.unlock('level_10');
        if (userData.level >= 15) this.unlock('level_15');
        if (userData.level >= 20) this.unlock('level_20');
    }
};

// Export for use in other modules
window.Achievements = Achievements;

