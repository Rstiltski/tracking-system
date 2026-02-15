/**
 * Notifications Module - Handles browser notifications for reminders
 */

const Notifications = {
    // Default settings
    defaultSettings: {
        enabled: false,
        sound: 'default',
        style: 'default',
        habitReminders: true,
        taskReminders: true,
        goalReminders: true
    },
    
    // Storage key for settings
    SETTINGS_KEY: 'tracklife_notification_settings',
    
    // Check if notifications are supported
    isSupported() {
        return 'Notification' in window;
    },
    
    // Get notification settings
    getSettings() {
        try {
            const settings = localStorage.getItem(this.SETTINGS_KEY);
            return settings ? { ...this.defaultSettings, ...JSON.parse(settings) } : { ...this.defaultSettings };
        } catch (error) {
            console.error('Error loading notification settings:', error);
            return { ...this.defaultSettings };
        }
    },
    
    // Save notification settings
    saveSettings(settings) {
        try {
            const mergedSettings = { ...this.getSettings(), ...settings };
            localStorage.setItem(this.SETTINGS_KEY, JSON.stringify(mergedSettings));
            return true;
        } catch (error) {
            console.error('Error saving notification settings:', error);
            return false;
        }
    },
    
    // Open settings modal
    openSettingsModal() {
        const modal = document.getElementById('notificationsSettingsModal');
        if (!modal) return;
        
        // Load current settings into form
        const settings = this.getSettings();
        
        const enabledCheckbox = document.getElementById('enableDesktopNotifications');
        const soundSelect = document.getElementById('notificationSound');
        const styleDefault = document.getElementById('notificationStyleDefault');
        const styleUrgent = document.getElementById('notificationStyleUrgent');
        
        if (enabledCheckbox) {
            enabledCheckbox.checked = settings.enabled;
        }
        if (soundSelect) {
            soundSelect.value = settings.sound;
        }
        if (styleDefault && styleUrgent) {
            if (settings.style === 'urgent') {
                styleUrgent.checked = true;
            } else {
                styleDefault.checked = true;
            }
        }
        
        // Show modal
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    },
    
    // Close settings modal
    closeSettingsModal() {
        const modal = document.getElementById('notificationsSettingsModal');
        if (!modal) return;
        
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    },
    
    // Save settings from form
    saveSettingsFromForm() {
        const enabledCheckbox = document.getElementById('enableDesktopNotifications');
        const soundSelect = document.getElementById('notificationSound');
        const styleUrgent = document.getElementById('notificationStyleUrgent');
        
        const settings = {
            enabled: enabledCheckbox ? enabledCheckbox.checked : false,
            sound: soundSelect ? soundSelect.value : 'default',
            style: styleUrgent && styleUrgent.checked ? 'urgent' : 'default'
        };
        
        if (this.saveSettings(settings)) {
            App.showToast('Notification settings saved!', 'success');
            
            // If enabling notifications, request permission
            if (settings.enabled && Notification.permission !== 'granted') {
                this.requestPermission();
            }
            
            this.closeSettingsModal();
        } else {
            App.showToast('Failed to save settings', 'error');
        }
    },
    
    // Setup settings modal event listeners
    setupSettingsModal() {
        // Open settings button
        document.getElementById('notificationsSettingsBtn')?.addEventListener('click', () => {
            this.openSettingsModal();
        });
        
        // Close button
        document.getElementById('notificationsSettingsClose')?.addEventListener('click', () => {
            this.closeSettingsModal();
        });
        
        // Cancel button
        document.getElementById('notificationsSettingsCancel')?.addEventListener('click', () => {
            this.closeSettingsModal();
        });
        
        // Save button
        document.getElementById('notificationsSettingsSave')?.addEventListener('click', () => {
            this.saveSettingsFromForm();
        });
        
        // Close on overlay click
        const modal = document.getElementById('notificationsSettingsModal');
        modal?.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeSettingsModal();
            }
        });
        
        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const modal = document.getElementById('notificationsSettingsModal');
                if (modal?.classList.contains('active')) {
                    this.closeSettingsModal();
                }
            }
        });
    },

    // Request notification permission
    async requestPermission() {
        if (!this.isSupported()) {
            App.showToast('Browser notifications are not supported', 'error');
            return false;
        }

        if (Notification.permission === 'granted') {
            return true;
        }

        if (Notification.permission !== 'denied') {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        }

        return false;
    },

    // Show notification
    show(title, options = {}) {
        const settings = this.getSettings();
        
        if (!this.isSupported() || Notification.permission !== 'granted' || !settings.enabled) {
            return;
        }

        const notification = new Notification(title, {
            body: options.body || '',
            icon: options.icon || 'assets/icons/icon.png',
            tag: options.tag || 'tracklife-notification',
            requireInteraction: settings.style === 'urgent' || options.requireInteraction || false,
            ...options
        });

        // Close notification after 5 seconds if not requiring interaction
        if (settings.style !== 'urgent' && !options.requireInteraction) {
            setTimeout(() => {
                notification.close();
            }, 5000);
        }

        return notification;
    },

    // Schedule habit reminder
    scheduleHabitReminder(habit) {
        const settings = this.getSettings();
        
        if (!this.isSupported() || !settings.enabled || !settings.habitReminders) return;

        // Check if it's time to remind the user about this habit
        const now = new Date();
        const currentHour = now.getHours();

        // Only show reminders during waking hours (8 AM to 9 PM)
        if (currentHour < 8 || currentHour > 21) {
            return;
        }

        // Check if the habit hasn't been completed today
        if (!Storage.isHabitCompletedOnDate(habit.id)) {
            setTimeout(() => {
                this.show(
                    `Habit Reminder: ${habit.name}`,
                    {
                        body: `Don't forget to complete your "${habit.name}" habit today!`,
                        icon: 'assets/icons/icon.png',
                        tag: `habit-reminder-${habit.id}`
                    }
                );
            }, 1000); // Small delay to allow UI to settle
        }
    },

    // Schedule task reminder
    scheduleTaskReminder(task) {
        const settings = this.getSettings();
        
        if (!this.isSupported() || !settings.enabled || !settings.taskReminders || !task.dueDate) return;

        const now = new Date();
        const dueDate = new Date(task.dueDate);
        const timeDiff = dueDate.getTime() - now.getTime();
        const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));

        // Remind 1 day before due date if not completed
        if (daysDiff === 1 && !task.completed) {
            setTimeout(() => {
                this.show(
                    `Task Due Soon: ${task.title}`,
                    {
                        body: `Your task "${task.title}" is due tomorrow.`,
                        icon: 'assets/icons/icon.png',
                        tag: `task-reminder-${task.id}`
                    }
                );
            }, 1000);
        }

        // Remind on due date if not completed
        if (daysDiff === 0 && !task.completed) {
            setTimeout(() => {
                this.show(
                    `Task Due Today: ${task.title}`,
                    {
                        body: `Your task "${task.title}" is due today. Don't forget to complete it!`,
                        icon: 'assets/icons/icon.png',
                        tag: `task-reminder-${task.id}`
                    }
                );
            }, 1000);
        }
    },

    // Schedule goal reminder
    scheduleGoalReminder(goal) {
        const settings = this.getSettings();
        
        if (!this.isSupported() || !settings.enabled || !settings.goalReminders || !goal.deadline) return;

        const now = new Date();
        const deadline = new Date(goal.deadline);
        const timeDiff = deadline.getTime() - now.getTime();
        const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));

        // Remind 3 days before deadline if not completed
        if (daysDiff === 3 && goal.progress < 100) {
            setTimeout(() => {
                this.show(
                    `Goal Deadline Approaching: ${goal.title}`,
                    {
                        body: `Your goal "${goal.title}" is due in 3 days. Current progress: ${goal.progress || 0}%`,
                        icon: 'assets/icons/icon.png',
                        tag: `goal-reminder-${goal.id}`
                    }
                );
            }, 1000);
        }

        // Remind on deadline if not completed
        if (daysDiff === 0 && goal.progress < 100) {
            setTimeout(() => {
                this.show(
                    `Goal Deadline: ${goal.title}`,
                    {
                        body: `Your goal "${goal.title}" is due today. Current progress: ${goal.progress || 0}%`,
                        icon: 'assets/icons/icon.png',
                        tag: `goal-reminder-${goal.id}`
                    }
                );
            }, 1000);
        }
    },

    // Check and schedule all reminders
    async checkAndScheduleReminders() {
        const settings = this.getSettings();
        
        if (!settings.enabled) {
            return;
        }
        
        if (!await this.requestPermission()) {
            return;
        }

        // Check habits
        const habits = Storage.getHabits();
        habits.forEach(habit => {
            this.scheduleHabitReminder(habit);
        });

        // Check tasks
        const tasks = Storage.getTasks();
        tasks.forEach(task => {
            this.scheduleTaskReminder(task);
        });

        // Check goals
        const goals = Storage.getGoals();
        goals.forEach(goal => {
            this.scheduleGoalReminder(goal);
        });
    },

    // Initialize notifications
    async init() {
        if (!this.isSupported()) {
            console.warn('Browser notifications are not supported');
            return;
        }
        
        // Setup settings modal
        this.setupSettingsModal();

        // Request permission on first use if settings are enabled
        const settings = this.getSettings();
        if (settings.enabled && Notification.permission === 'default') {
            await this.requestPermission();
        }

        // Check for reminders periodically (every hour)
        setInterval(() => {
            this.checkAndScheduleReminders();
        }, 60 * 60 * 1000); // Every hour

        // Also check immediately on initialization
        this.checkAndScheduleReminders();
    }
};

// Export for use in other modules
window.Notifications = Notifications;