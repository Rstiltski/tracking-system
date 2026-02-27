/**
 * Habits Module - Enhanced Habit Tracking System
 * Features:
 * - Dynamic date display with month boundaries
 * - Frozen habit and progress columns
 * - Anti-cheating (locked past/future days)
 * - 24-hour auto-refresh with countdown
 * - Progress bar visualization
 * - Weekend and month boundary styling
 * - Streak indicators
 * - Week/Month view toggle
 */

const Habits = {
    // Default habit icons
    icons: ['🏃', '📚', '💧', '🧘', '💪', '🎯', '✍️', '🛏️', '🥗', '💊', '🎨', '🎵', '💻', '🌱', '🙏'],

    // Default habit colors
    colors: ['#6366f1', '#ec4899', '#10b981', '#f59e0b', '#3b82f6', '#ef4444', '#8b5cf6', '#06b6d4'],

    // Current view mode ('card' or 'table')
    currentViewMode: 'table',

    // Current view period ('week' or 'month')
    currentPeriodMode: 'week',

    // Current week offset (0 = current week, -1 = previous week, etc.)
    currentWeekOffset: 0,

    // Current month offset (0 = current month, -1 = previous month, etc.)
    currentMonthOffset: 0,

    // Countdown timer interval
    countdownInterval: null,

    // Last recorded date for auto-refresh
    lastRecordedDate: null,

    // Initialize habits module
    init() {
        // Reset to current period when opening habits page
        this.currentWeekOffset = 0;
        this.currentMonthOffset = 0;
        this.bindEvents();
        this.startCountdownTimer();
        this.checkForDateChange();
        this.render();
        // Scroll to current day after render
        if (this.currentViewMode === 'table') {
            setTimeout(() => this.scrollToCurrentDay(), 200);
        }
    },

    // Check if date has changed (for auto-refresh)
    checkForDateChange() {
        const today = new Date();
        const todayStr = this.formatDate(today);
        
        if (this.lastRecordedDate && this.lastRecordedDate !== todayStr) {
            // Date changed - refresh the view
            this.currentWeekOffset = 0;
            this.currentMonthOffset = 0;
            this.render();
            App.showToast('🌅 New day! Habits have been refreshed.', 'success');
        }
        
        this.lastRecordedDate = todayStr;
        
        // Check every minute for date change
        setInterval(() => this.checkForDateChange(), 60000);
    },

    // Start countdown timer to midnight
    startCountdownTimer() {
        const updateCountdown = () => {
            const now = new Date();
            const midnight = new Date();
            midnight.setHours(24, 0, 0, 0);
            
            const diff = midnight - now;
            const hours = Math.floor(diff / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);
            
            const countdownEl = document.getElementById('resetCountdown');
            if (countdownEl) {
                countdownEl.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
        };

        // Update immediately and then every second
        updateCountdown();
        if (this.countdownInterval) clearInterval(this.countdownInterval);
        this.countdownInterval = setInterval(updateCountdown, 1000);
    },

    // Bind event listeners
    bindEvents() {
        // Add habit button
        document.getElementById('addHabitBtn')?.addEventListener('click', () => {
            this.showAddModal();
        });

        // View mode toggle buttons
        document.querySelectorAll('.view-mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.view-mode-btn').forEach(b => {
                    b.classList.remove('active');
                    b.classList.add('bg-gray-800', 'text-gray-400');
                });
                e.target.classList.add('active', 'bg-emerald-600', 'text-white');
                e.target.classList.remove('bg-gray-800', 'text-gray-400');
                this.currentViewMode = e.target.dataset.mode;
                this.render();
            });
        });

        // Period mode toggle (week/month)
        document.querySelectorAll('.period-mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.period-mode-btn').forEach(b => {
                    b.classList.remove('active', 'bg-emerald-600', 'text-white');
                    b.classList.add('bg-gray-800', 'text-gray-400');
                });
                e.target.classList.add('active', 'bg-emerald-600', 'text-white');
                e.target.classList.remove('bg-gray-800', 'text-gray-400');
                this.currentPeriodMode = e.target.dataset.period;
                this.currentWeekOffset = 0;
                this.currentMonthOffset = 0;
                this.render();
            });
        });

        // Page visibility - refresh when tab becomes active
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.checkForDateChange();
            }
        });
    },

    // Render habits list
    render() {
        if (this.currentViewMode === 'table') {
            this.renderHabitsTable();
        } else {
            this.renderHabitsList();
        }
        this.renderQuickHabits();
    },

    // Scroll to current day in the table
    scrollToCurrentDay() {
        const container = document.querySelector('.habit-table-container');
        const todayCell = document.querySelector('.today-column');
        if (container && todayCell) {
            const containerWidth = container.offsetWidth;
            const cellOffset = todayCell.offsetLeft;
            const cellWidth = todayCell.offsetWidth;
            
            // Center the current day
            container.scrollTo({
                left: cellOffset - (containerWidth / 2) + (cellWidth / 2),
                behavior: 'smooth'
            });
        }
    },

    // Get dates for the current view period
    getViewDates() {
        if (this.currentPeriodMode === 'week') {
            return this.getWeekDates(this.currentWeekOffset);
        } else {
            return this.getMonthDates(this.currentMonthOffset);
        }
    },

    // Get week start and end dates
    getWeekDates(offset = 0) {
        const today = new Date();
        const currentDay = today.getDay();
        const weekStart = new Date(today);
        weekStart.setDate(today.getDate() - currentDay + (offset * 7));
        weekStart.setHours(0, 0, 0, 0);
        
        const dates = [];
        for (let i = 0; i < 7; i++) {
            const date = new Date(weekStart);
            date.setDate(weekStart.getDate() + i);
            dates.push(date);
        }
        return dates;
    },

    // Get all dates in a month
    getMonthDates(offset = 0) {
        const today = new Date();
        const monthStart = new Date(today.getFullYear(), today.getMonth() + offset, 1);
        const monthEnd = new Date(today.getFullYear(), today.getMonth() + offset + 1, 0);
        
        const dates = [];
        for (let d = new Date(monthStart); d <= monthEnd; d.setDate(d.getDate() + 1)) {
            dates.push(new Date(d));
        }
        return dates;
    },

    // Format date as YYYY-MM-DD
    formatDate(date) {
        return date.toISOString().split('T')[0];
    },

    // Format date for display (e.g., "Mon 12/23")
    formatDisplayDate(date) {
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const month = date.getMonth() + 1;
        const day = date.getDate();
        return `${days[date.getDay()]} ${month}/${day}`;
    },

    // Get month name
    getMonthName(monthIndex) {
        const months = ['January', 'February', 'March', 'April', 'May', 'June', 
                        'July', 'August', 'September', 'October', 'November', 'December'];
        return months[monthIndex];
    },

    // Check if date is today
    isToday(date) {
        const today = new Date();
        return date.toDateString() === today.toDateString();
    },

    // Check if date is in the past
    isPast(date) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const compareDate = new Date(date);
        compareDate.setHours(0, 0, 0, 0);
        return compareDate < today;
    },

    // Check if date is in the future
    isFuture(date) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const compareDate = new Date(date);
        compareDate.setHours(0, 0, 0, 0);
        return compareDate > today;
    },

    // Check if date is a weekend
    isWeekend(date) {
        const day = date.getDay();
        return day === 0 || day === 6;
    },

    // Check if date crosses month boundary from previous date
    isMonthBoundary(date, prevDate) {
        if (!prevDate) return false;
        return date.getMonth() !== prevDate.getMonth();
    },

    // Render habits table view (weekly/monthly)
    renderHabitsTable() {
        const container = document.getElementById('habitsContainer');
        if (!container) return;

        const habits = Storage.getHabits();
        const viewDates = this.getViewDates();
        const today = new Date();

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

        // Build navigation and header
        const periodLabel = this.currentPeriodMode === 'week' 
            ? `Week of ${this.formatDisplayDate(viewDates[0])} - ${this.formatDisplayDate(viewDates[6])}`
            : `${this.getMonthName(viewDates[0].getMonth())} ${viewDates[0].getFullYear()}`;

        // Build table HTML
        let html = `
            <!-- Enhanced Header with Navigation and Countdown -->
            <div class="habit-header-enhanced">
                <div class="habit-header-left">
                    <button id="prevYearBtn" class="nav-btn year-nav" title="Previous Year">⏪</button>
                    <button id="prevPeriodBtn" class="nav-btn" title="Previous ${this.currentPeriodMode === 'week' ? 'Week' : 'Month'}">◀</button>
                    <span class="period-label">${periodLabel}</span>
                    <button id="nextPeriodBtn" class="nav-btn" title="Next ${this.currentPeriodMode === 'week' ? 'Week' : 'Month'}">▶</button>
                    <button id="nextYearBtn" class="nav-btn year-nav" title="Next Year">⏩</button>
                    <button id="todayBtn" class="nav-btn today-btn" title="Go to Today">📍 Today</button>
                </div>
                <div class="habit-header-right">
                    <div class="view-toggle-enhanced">
                        <button class="period-mode-btn ${this.currentPeriodMode === 'week' ? 'active bg-emerald-600 text-white' : 'bg-gray-800 text-gray-400'}" data-period="week">📅 Week</button>
                        <button class="period-mode-btn ${this.currentPeriodMode === 'month' ? 'active bg-emerald-600 text-white' : 'bg-gray-800 text-gray-400'}" data-period="month">📆 Month</button>
                    </div>
                    <div class="countdown-timer">
                        <span class="countdown-icon">⏰</span>
                        <span class="countdown-label">Resets in:</span>
                        <span id="resetCountdown" class="countdown-value">00:00:00</span>
                    </div>
                </div>
            </div>

            <!-- Habit Table Container -->
            <div class="habit-table-container">
                <table class="habit-table">
                    <thead>
                        <tr>
                            <th class="habit-name-header">Habit</th>
                            ${this.renderDateHeaders(viewDates)}
                            <th class="progress-header">Progress</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${habits.map(habit => this.createHabitTableRow(habit, viewDates)).join('')}
                    </tbody>
                    <tfoot>
                        <tr class="summary-row">
                            <td class="summary-label">Daily Completion</td>
                            ${viewDates.map(date => this.renderDailySummary(habits, date)).join('')}
                            <td class="summary-total">
                                <span class="total-label">Overall:</span>
                                <span class="total-value">${this.calculateOverallProgress(habits, viewDates)}%</span>
                            </td>
                        </tr>
                    </tfoot>
                </table>
            </div>

            <!-- Legend -->
            <div class="habit-legend">
                <div class="legend-item"><span class="legend-icon completed">✓</span> Completed</div>
                <div class="legend-item"><span class="legend-icon missed">✗</span> Missed</div>
                <div class="legend-item"><span class="legend-icon pending">○</span> Pending</div>
                <div class="legend-item"><span class="legend-icon locked">🔒</span> Locked</div>
                <div class="legend-item"><span class="legend-icon weekend">🌟</span> Weekend</div>
                <div class="legend-item"><span class="legend-icon today-pill">TODAY</span> Current Day</div>
            </div>
        `;

        container.innerHTML = html;

        // Bind habit check events (only for today's checkboxes)
        container.querySelectorAll('.habit-check.editable').forEach(checkbox => {
            checkbox.addEventListener('click', (e) => {
                e.stopPropagation();
                const habitId = e.currentTarget.dataset.habitId;
                const date = e.currentTarget.dataset.date;
                this.toggleHabitOnDate(habitId, date);
            });
        });

        // Bind navigation events
        this.bindNavigationEvents();

        // Scroll to current day on initial load
        if (this.currentWeekOffset === 0 && this.currentMonthOffset === 0) {
            setTimeout(() => this.scrollToCurrentDay(), 100);
        }
        
        // Restart countdown timer
        this.startCountdownTimer();
    },

    // Bind navigation events
    bindNavigationEvents() {
        document.getElementById('prevPeriodBtn')?.addEventListener('click', () => {
            if (this.currentPeriodMode === 'week') {
                this.currentWeekOffset--;
            } else {
                this.currentMonthOffset--;
            }
            this.render();
        });

        document.getElementById('nextPeriodBtn')?.addEventListener('click', () => {
            if (this.currentPeriodMode === 'week') {
                this.currentWeekOffset++;
            } else {
                this.currentMonthOffset++;
            }
            this.render();
        });

        document.getElementById('todayBtn')?.addEventListener('click', () => {
            this.currentWeekOffset = 0;
            this.currentMonthOffset = 0;
            this.render();
            setTimeout(() => this.scrollToCurrentDay(), 100);
        });

        document.getElementById('prevYearBtn')?.addEventListener('click', () => {
            if (this.currentPeriodMode === 'week') {
                this.currentWeekOffset -= 52;
            } else {
                this.currentMonthOffset -= 12;
            }
            this.render();
        });

        document.getElementById('nextYearBtn')?.addEventListener('click', () => {
            if (this.currentPeriodMode === 'week') {
                this.currentWeekOffset += 52;
            } else {
                this.currentMonthOffset += 12;
            }
            this.render();
        });

        // Period mode toggle
        document.querySelectorAll('.period-mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.period-mode-btn').forEach(b => {
                    b.classList.remove('active', 'bg-emerald-600', 'text-white');
                    b.classList.add('bg-gray-800', 'text-gray-400');
                });
                e.target.classList.add('active', 'bg-emerald-600', 'text-white');
                e.target.classList.remove('bg-gray-800', 'text-gray-400');
                this.currentPeriodMode = e.target.dataset.period;
                this.currentWeekOffset = 0;
                this.currentMonthOffset = 0;
                this.render();
            });
        });
    },

    // Render date headers with month boundary indicators
    renderDateHeaders(dates) {
        let prevDate = null;
        return dates.map((date, index) => {
            const isToday = this.isToday(date);
            const isWeekend = this.isWeekend(date);
            const isMonthBound = this.isMonthBoundary(date, prevDate);
            const monthIndicator = isMonthBound ? `<span class="month-boundary">${this.getMonthName(date.getMonth()).substring(0, 3)} →</span>` : '';
            
            let classes = [];
            if (isToday) classes.push('today-column', 'today-header');
            if (isWeekend) classes.push('weekend-column');
            if (isMonthBound) classes.push('month-boundary-column');
            
            prevDate = date;
            
            return `
                <th class="${classes.join(' ')}">
                    ${monthIndicator}
                    <div class="date-header-content">
                        <span class="date-day">${this.formatDisplayDate(date).split(' ')[0]}</span>
                        <span class="date-number">${date.getDate()}</span>
                        ${isToday ? '<span class="today-pill">TODAY</span>' : ''}
                    </div>
                </th>
            `;
        }).join('');
    },

    // Create habit table row
    createHabitTableRow(habit, viewDates) {
        const completedDates = Storage.getHabitCompletions(habit.id) || [];
        const streak = Storage.getHabitStreak(habit.id);
        
        return `
            <tr data-habit-id="${habit.id}">
                <td class="habit-name-cell">
                    <div class="habit-info-wrapper">
                        <span class="habit-icon" style="color: ${habit.color}">${habit.icon}</span>
                        <div class="habit-details">
                            <span class="habit-name">${habit.name}</span>
                            <span class="habit-streak">${streak > 0 ? `🔥 ${streak} day streak` : 'Start your streak!'}</span>
                        </div>
                    </div>
                </td>
                ${viewDates.map((date, index) => this.renderHabitCell(habit.id, date, completedDates, index > 0 ? viewDates[index - 1] : null)).join('')}
                <td class="progress-cell">
                    ${this.renderProgressBar(habit.id, viewDates)}
                </td>
            </tr>
        `;
    },

    // Render individual habit cell with anti-cheating
    renderHabitCell(habitId, date, completedDates, prevDate) {
        const dateStr = this.formatDate(date);
        const isCompleted = completedDates.includes(dateStr);
        const isToday = this.isToday(date);
        const isPast = this.isPast(date);
        const isFuture = this.isFuture(date);
        const isWeekend = this.isWeekend(date);
        const isMonthBound = this.isMonthBoundary(date, prevDate);
        
        let cellClass = 'habit-cell';
        let content = '';
        let isEditable = false;
        
        // Determine cell state
        if (isToday) {
            // Today - editable
            cellClass += ' today-column editable';
            isEditable = true;
            content = `<div class="habit-check ${isCompleted ? 'checked' : ''}" data-habit-id="${habitId}" data-date="${dateStr}">${isCompleted ? '✓' : '○'}</div>`;
        } else if (isPast) {
            // Past - locked (read-only)
            cellClass += ' past-column locked';
            if (isCompleted) {
                content = `<span class="habit-status completed">✓</span>`;
            } else {
                content = `<span class="habit-status missed">✗</span>`;
            }
        } else {
            // Future - locked (read-only)
            cellClass += ' future-column locked';
            content = `<span class="habit-status pending">○</span>`;
        }
        
        // Add weekend styling
        if (isWeekend) {
            cellClass += ' weekend-column';
        }
        
        // Add month boundary styling
        if (isMonthBound) {
            cellClass += ' month-boundary-column';
        }
        
        return `
            <td class="${cellClass}">
                ${content}
            </td>
        `;
    },

    // Render progress bar with percentage
    renderProgressBar(habitId, viewDates) {
        const progress = this.calculateProgress(habitId, viewDates);
        const progressClass = progress < 30 ? 'low' : progress < 70 ? 'medium' : 'high';
        
        return `
            <div class="progress-bar-container">
                <div class="progress-bar">
                    <div class="progress-fill ${progressClass}" style="width: ${progress}%"></div>
                </div>
                <span class="progress-text ${progressClass}">${progress}%</span>
            </div>
        `;
    },

    // Render daily summary for footer
    renderDailySummary(habits, date) {
        const dateStr = this.formatDate(date);
        let completed = 0;
        
        habits.forEach(habit => {
            const completions = Storage.getHabitCompletions(habit.id) || [];
            if (completions.includes(dateStr)) completed++;
        });
        
        const percentage = habits.length > 0 ? Math.round((completed / habits.length) * 100) : 0;
        const isToday = this.isToday(date);
        const isWeekend = this.isWeekend(date);
        
        let classes = ['summary-cell'];
        if (isToday) classes.push('today-column');
        if (isWeekend) classes.push('weekend-column');
        
        return `
            <td class="${classes.join(' ')}">
                <div class="daily-summary">
                    <span class="summary-completed">${completed}/${habits.length}</span>
                    <span class="summary-percentage">${percentage}%</span>
                </div>
            </td>
        `;
    },

    // Calculate progress for a habit in the current view period
    calculateProgress(habitId, viewDates) {
        const completedDates = Storage.getHabitCompletions(habitId) || [];
        
        // Only count days that have passed or are today
        const relevantDates = viewDates.filter(date => {
            return !this.isFuture(date);
        });
        
        if (relevantDates.length === 0) return 0;
        
        const completedCount = relevantDates.filter(date => {
            const dateStr = this.formatDate(date);
            return completedDates.includes(dateStr);
        }).length;
        
        return Math.round((completedCount / relevantDates.length) * 100);
    },

    // Calculate overall progress for all habits
    calculateOverallProgress(habits, viewDates) {
        if (habits.length === 0) return 0;
        
        const totalProgress = habits.reduce((sum, habit) => {
            return sum + this.calculateProgress(habit.id, viewDates);
        }, 0);
        
        return Math.round(totalProgress / habits.length);
    },

    // Toggle habit on specific date (only for today)
    toggleHabitOnDate(habitId, date) {
        // Verify it's today (anti-cheating)
        const today = new Date();
        const todayStr = this.formatDate(today);
        
        if (date !== todayStr) {
            App.showToast('⚠️ You can only modify today\'s habits!', 'error');
            return;
        }

        const isCompleted = Storage.isHabitCompletedOnDate(habitId, date);

        if (isCompleted) {
            Storage.unlogHabitCompletion(habitId, date);
            App.showToast('Habit unmarked', 'warning');
        } else {
            Storage.logHabitCompletion(habitId, date);
            App.showToast('🎉 Habit completed! +10 XP', 'success');
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

        // Update only the specific checkbox and progress cell without re-rendering
        this.updateHabitCell(habitId, date);
    },

    // Update a single habit cell and progress without full re-render
    updateHabitCell(habitId, date) {
        const checkbox = document.querySelector(`.habit-check[data-habit-id="${habitId}"][data-date="${date}"]`);
        const isCompleted = Storage.isHabitCompletedOnDate(habitId, date);
        
        if (checkbox) {
            if (isCompleted) {
                checkbox.classList.add('checked');
                checkbox.textContent = '✓';
            } else {
                checkbox.classList.remove('checked');
                checkbox.textContent = '○';
            }
        }

        // Update the progress cell for this habit
        const row = document.querySelector(`tr[data-habit-id="${habitId}"]`);
        if (row) {
            const progressCell = row.querySelector('.progress-cell');
            if (progressCell) {
                const viewDates = this.getViewDates();
                progressCell.innerHTML = this.renderProgressBar(habitId, viewDates);
            }
        }

        // Update the daily summary
        this.updateDailySummary(date);

        // Update dashboard stats
        App.updateDashboard();
    },

    // Update daily summary in footer
    updateDailySummary(date) {
        const habits = Storage.getHabits();
        const dateStr = this.formatDate(date);
        const isToday = this.isToday(date);
        
        if (!isToday) return; // Only update today's summary
        
        let completed = 0;
        habits.forEach(habit => {
            const completions = Storage.getHabitCompletions(habit.id) || [];
            if (completions.includes(dateStr)) completed++;
        });
        
        const summaryCell = document.querySelector('.today-column.summary-cell .daily-summary');
        if (summaryCell) {
            const percentage = habits.length > 0 ? Math.round((completed / habits.length) * 100) : 0;
            summaryCell.querySelector('.summary-completed').textContent = `${completed}/${habits.length}`;
            summaryCell.querySelector('.summary-percentage').textContent = `${percentage}%`;
        }
        
        // Update overall progress
        const viewDates = this.getViewDates();
        const overallCell = document.querySelector('.summary-total .total-value');
        if (overallCell) {
            overallCell.textContent = `${this.calculateOverallProgress(habits, viewDates)}%`;
        }
    },

    // Render main habits list (card view)
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

        container.innerHTML = `
            <div class="habits-header-card">
                <h3>Your Habits</h3>
                <div class="countdown-timer-mini">
                    <span>⏰ Resets in:</span>
                    <span id="resetCountdown" class="countdown-value">00:00:00</span>
                </div>
            </div>
            <div class="habits-card-grid">
                ${habits.map(habit => this.createHabitCard(habit)).join('')}
            </div>
        `;
        
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

        // Restart countdown timer
        this.startCountdownTimer();
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

    // Toggle habit completion (for card view - today only)
    toggleHabit(habitId) {
        const today = new Date();
        const todayStr = this.formatDate(today);
        const isCompleted = Storage.isHabitCompletedOnDate(habitId, todayStr);
        
        if (isCompleted) {
            Storage.unlogHabitCompletion(habitId, todayStr);
            App.showToast('Habit unmarked', 'warning');
        } else {
            Storage.logHabitCompletion(habitId, todayStr);
            App.showToast('🎉 Habit completed! +10 XP', 'success');
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