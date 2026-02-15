/**
 * App - Main Application Controller
 * Handles navigation, modals, and initialization
 */

const App = {
    // Current view
    currentView: 'dashboard',

    // Motivational quotes
    quotes: [
        '"The secret of getting ahead is getting started." - Mark Twain',
        '"Success is the sum of small efforts repeated day in and day out." - Robert Collier',
        '"The only way to do great work is to love what you do." - Steve Jobs',
        '"Believe you can and you\'re halfway there." - Theodore Roosevelt',
        '"Your limitation—it\'s only your imagination." - Unknown',
        '"Great things never come from comfort zones." - Unknown',
        '"Dream it. Wish it. Do it." - Unknown',
        '"Success doesn\'t just find you. You have to go out and get it." - Unknown',
        '"The harder you work for something, the greater you\'ll feel when you achieve it." - Unknown',
        '"Dream bigger. Do bigger." - Unknown',
        '"Don\'t stop when you\'re tired. Stop when you\'re done." - Unknown',
        '"Wake up with determination. Go to bed with satisfaction." - Unknown',
        '"Do something today that your future self will thank you for." - Unknown',
        '"Little things make big days." - Unknown',
        '"It\'s going to be hard, but hard does not mean impossible." - Unknown',
        '"Don\'t wait for opportunity. Create it." - Unknown',
        '"Sometimes we\'re tested not to show our weaknesses, but to discover our strengths." - Unknown',
        '"The key to success is to focus on goals, not obstacles." - Unknown',
        '"Dream it. Believe it. Achieve it." - Unknown',
        '"Make yourself proud." - Unknown'
    ],

    // Initialize the application
    init() {
        this.setupNavigation();
        this.setupSidebar();
        this.setupTheme();
        this.setupDate();
        this.setupModals();
        this.setupViewToggle();
        this.setupDataButtons();
        this.setupKeyboardShortcuts(); // Add keyboard shortcuts
        this.updateAll();
        this.showRandomQuote();

        // Set initial view
        this.navigateTo('dashboard');

        // Initialize notifications
        if ('Notification' in window) {
            Notifications.init();
        }
    },

    // Setup navigation
    setupNavigation() {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = link.dataset.view;
                this.navigateTo(view);
            });
        });
    },

    // Setup sidebar toggle
    setupSidebar() {
        const sidebar = document.getElementById('sidebar');
        const menuBtn = document.getElementById('menuBtn');
        const sidebarToggle = document.getElementById('sidebarToggle');

        menuBtn?.addEventListener('click', () => {
            sidebar?.classList.toggle('open');
        });

        sidebarToggle?.addEventListener('click', () => {
            sidebar?.classList.toggle('collapsed');
        });
    },

    // Setup theme toggle
    setupTheme() {
        const themeToggle = document.getElementById('themeToggle');
        
        // Load saved theme
        const settings = Storage.getSettings();
        if (settings.theme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        }

        themeToggle?.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            
            // Save preference
            const settings = Storage.getSettings();
            settings.theme = newTheme;
            Storage.saveSettings(settings);
        });
    },

    // Setup date display
    setupDate() {
        const dateDisplay = document.getElementById('dateDisplay');
        if (dateDisplay) {
            const today = new Date();
            dateDisplay.textContent = today.toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
    },

    // Setup modals
    setupModals() {
        const modalOverlay = document.getElementById('modalOverlay');
        const modalClose = document.getElementById('modalClose');

        modalClose?.addEventListener('click', () => {
            this.closeModal();
        });

        modalOverlay?.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                this.closeModal();
            }
        });

        // Close modal on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    },

    // Setup view toggle (daily/weekly/monthly)
    setupViewToggle() {
        document.querySelectorAll('.view-toggle .view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.view-toggle .view-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');

                // Get the selected view type
                const viewType = e.target.dataset.viewType;

                // Update dashboard based on view type
                this.updateDashboardForView(viewType);
            });
        });
    },
    
    // Setup data export/import buttons
    setupDataButtons() {
        document.getElementById('exportBtn')?.addEventListener('click', () => {
            DataExport.showExportModal();
        });

        document.getElementById('importBtn')?.addEventListener('click', () => {
            DataExport.showImportModal();
        });
        
        // Add event listener for backup/restore button if it exists
        document.getElementById('backupRestoreBtn')?.addEventListener('click', () => {
            DataExport.showBackupRestoreModal();
        });
    },

    // Setup keyboard shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + S: Save/export data
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                DataExport.showExportModal();
            }
            
            // Ctrl/Cmd + O: Import data
            if ((e.ctrlKey || e.metaKey) && e.key === 'o') {
                e.preventDefault();
                DataExport.showImportModal();
            }
            
            // Escape: Close modal
            if (e.key === 'Escape') {
                const modalOverlay = document.getElementById('modalOverlay');
                if (modalOverlay?.classList.contains('active')) {
                    this.closeModal();
                }
            }
            
            // Navigation shortcuts
            if (e.altKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        this.navigateTo('dashboard');
                        break;
                    case '2':
                        e.preventDefault();
                        this.navigateTo('habits');
                        break;
                    case '3':
                        e.preventDefault();
                        this.navigateTo('tasks');
                        break;
                    case '4':
                        e.preventDefault();
                        this.navigateTo('finances');
                        break;
                    case '5':
                        e.preventDefault();
                        this.navigateTo('health');
                        break;
                    case '6':
                        e.preventDefault();
                        this.navigateTo('time');
                        break;
                    case '7':
                        e.preventDefault();
                        this.navigateTo('goals');
                        break;
                    case '8':
                        e.preventDefault();
                        this.navigateTo('achievements');
                        break;
                }
            }
        });
    },
    
    // Update dashboard based on view type (daily/weekly/monthly)
    updateDashboardForView(viewType) {
        // Update the weekly chart based on view type
        Charts.initWeeklyChart('weeklyChart', viewType);

        // Update other charts that might need to reflect the view type
        if (this.currentView === 'dashboard') {
            // Update monthly chart if it exists
            const monthlyChartEl = document.getElementById('monthlyChart');
            if (monthlyChartEl) {
                Charts.initMonthlyChart('monthlyChart', viewType);
            }
        } else if (this.currentView === 'finances') {
            // Update financial trends chart if it exists
            const financialTrendsChartEl = document.getElementById('financialTrendsChart');
            if (financialTrendsChartEl) {
                Charts.initFinancialTrendsChart('financialTrendsChart');
            }
        } else if (this.currentView === 'health') {
            // Update health charts if they exist
            const weightChartEl = document.getElementById('weightChart');
            const sleepChartEl = document.getElementById('sleepChart');
            const moodChartEl = document.getElementById('moodChart');
            
            if (weightChartEl) Charts.initWeightChart('weightChart');
            if (sleepChartEl) Charts.initSleepChart('sleepChart');
            if (moodChartEl) Charts.initMoodChart('moodChart');
        } else if (this.currentView === 'time') {
            // Update time chart if it exists
            const timeChartEl = document.getElementById('timeChart');
            if (timeChartEl) {
                Charts.initTimeChart('timeChart');
            }
        } else if (this.currentView === 'habits') {
            // Update dashboard charts when returning to dashboard
            if (document.getElementById('weeklyChart')) {
                Charts.initWeeklyChart('weeklyChart', viewType);
            }
        }

        // Update other parts of the dashboard as needed
        switch(this.currentView) {
            case 'dashboard':
                this.updateDashboard();
                break;
            case 'habits':
                Habits.render();
                break;
            case 'tasks':
                Tasks.render();
                break;
            case 'finances':
                Finances.render();
                break;
            case 'health':
                Health.render();
                break;
            case 'time':
                Time.render();
                break;
            case 'goals':
                Goals.render();
                break;
            case 'achievements':
                Achievements.render();
                break;
        }
    },

    // Navigate to a view
    navigateTo(view) {
        // Update nav items
        document.querySelectorAll('.nav-link').forEach(link => {
            const parentLi = link.closest('.nav-item');
            if (parentLi) {
                parentLi.classList.toggle('active', link.dataset.view === view);
            }
        });

        // Update views
        document.querySelectorAll('.view').forEach(v => {
            v.classList.remove('active');
        });

        const targetView = document.getElementById(`${view}View`);
        if (targetView) {
            targetView.classList.add('active');
        }

        // Update page title
        const pageTitle = document.getElementById('pageTitle');
        if (pageTitle) {
            const titles = {
                dashboard: 'Dashboard',
                habits: 'Daily Habits',
                tasks: 'Tasks & Todos',
                finances: 'Finances & Budget',
                health: 'Health Metrics',
                time: 'Time & Productivity',
                goals: 'Goals & Progress',
                achievements: 'Achievements & Rewards'
            };
            pageTitle.textContent = titles[view] || 'Dashboard';
        }

        this.currentView = view;

        // Initialize module if needed
        switch (view) {
            case 'habits':
                Habits.init();
                break;
            case 'tasks':
                Tasks.init();
                break;
            case 'finances':
                Finances.init();
                break;
            case 'health':
                Health.init();
                break;
            case 'time':
                Time.init();
                break;
            case 'goals':
                Goals.init();
                break;
            case 'achievements':
                Achievements.init();
                break;
            case 'dashboard':
                this.updateDashboard();
                break;
        }

        // Close mobile sidebar
        document.getElementById('sidebar')?.classList.remove('open');
    },

    // Show modal
    showModal(content) {
        const modalOverlay = document.getElementById('modalOverlay');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const modalFooter = document.getElementById('modalFooter');

        if (modalTitle) modalTitle.textContent = content.title || 'Modal';
        if (modalBody) modalBody.innerHTML = content.body || '';
        if (modalFooter) modalFooter.innerHTML = content.footer || '';

        modalOverlay?.classList.add('active');
        modalOverlay?.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        
        // Focus on the modal for accessibility
        const firstFocusableElement = modalOverlay?.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (firstFocusableElement) {
            firstFocusableElement.focus();
        }
    },

    // Close modal
    closeModal() {
        const modalOverlay = document.getElementById('modalOverlay');
        modalOverlay?.classList.remove('active');
        modalOverlay?.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        
        // Return focus to the trigger element if possible
        const activeElement = document.activeElement;
        if (activeElement && activeElement.tagName === 'BUTTON') {
            activeElement.focus();
        }
    },

    // Show toast notification
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');

        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <span class="toast-message">${message}</span>
        `;

        container.appendChild(toast);

        // Auto remove
        setTimeout(() => {
            toast.style.animation = 'toastSlideIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    // Celebration effect (confetti)
    celebrate() {
        const canvas = document.getElementById('confettiCanvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const confetti = [];
        const colors = ['#6366f1', '#ec4899', '#10b981', '#f59e0b', '#3b82f6', '#a855f7'];

        for (let i = 0; i < 150; i++) {
            confetti.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height - canvas.height,
                w: Math.random() * 10 + 5,
                h: Math.random() * 6 + 3,
                color: colors[Math.floor(Math.random() * colors.length)],
                speed: Math.random() * 3 + 2,
                angle: Math.random() * 360,
                spin: Math.random() * 10 - 5
            });
        }

        let frame = 0;
        const maxFrames = 150;

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            confetti.forEach(c => {
                ctx.save();
                ctx.translate(c.x, c.y);
                ctx.rotate((c.angle * Math.PI) / 180);
                ctx.fillStyle = c.color;
                ctx.fillRect(-c.w / 2, -c.h / 2, c.w, c.h);
                ctx.restore();

                c.y += c.speed;
                c.angle += c.spin;
            });

            frame++;
            if (frame < maxFrames) {
                requestAnimationFrame(animate);
            } else {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
        }

        animate();
    },

    // Show random motivational quote
    showRandomQuote() {
        const quoteElement = document.getElementById('motivationText');
        if (quoteElement) {
            const randomQuote = this.quotes[Math.floor(Math.random() * this.quotes.length)];
            quoteElement.textContent = randomQuote;
        }
    },

    // Update dashboard
    updateDashboard() {
        this.updateUserStats();
        Habits.renderQuickHabits();
        Tasks.renderQuickTasks();
        Goals.renderGoalsOverview();
        Charts.initWeeklyChart('weeklyChart');
    },

    // Update user stats
    updateUserStats() {
        const userData = Storage.getUserData();
        
        // Level badge
        const levelBadge = document.getElementById('levelBadge');
        if (levelBadge) {
            levelBadge.textContent = `Level ${userData.level}`;
        }

        // XP bar
        const xpFill = document.getElementById('xpFill');
        const xpText = document.getElementById('xpText');
        const xpPercentage = Storage.getXpProgressToNextLevel();
        
        // Calculate XP needed for next level
        const currentLevelXP = Storage.getXPForLevel(userData.level);
        const nextLevelXP = Storage.getXPForLevel(userData.level + 1);
        const xpNeededForNextLevel = nextLevelXP - currentLevelXP;
        
        if (xpFill) {
            xpFill.style.width = `${xpPercentage}%`;
        }
        if (xpText) {
            xpText.textContent = `${userData.xp} / ${xpNeededForNextLevel} XP`;
        }

        // Stats
        const totalStreaks = document.getElementById('totalStreaks');
        if (totalStreaks) {
            totalStreaks.textContent = Habits.getTotalStreaks();
        }

        const tasksCompleted = document.getElementById('tasksCompleted');
        if (tasksCompleted) {
            tasksCompleted.textContent = Tasks.getCompletedTodayCount();
        }

        const currentBalance = document.getElementById('currentBalance');
        if (currentBalance) {
            currentBalance.textContent = Finances.formatCurrency(Finances.getTotalBalance());
        }

        const healthScore = document.getElementById('healthScore');
        if (healthScore) {
            healthScore.textContent = Health.getHealthScore() || '--';
        }
    },

    // Update all modules
    updateAll() {
        Habits.init();
        Tasks.init();
        Finances.init();
        Health.init();
        Time.init();
        Goals.init();
        Achievements.init();
        this.updateDashboard();
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

// Export for use in other modules
window.App = App;

