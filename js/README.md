# 📜 JavaScript Modules - Frontend Logic

**Client-side JavaScript modules for the tracking system.**

---

## Overview

The `js/` directory contains all JavaScript modules that power the frontend of the tracking system. Each module follows a consistent pattern and handles a specific domain.

---

## Modules

| File | Purpose |
|------|---------|
| `app.js` | Main application controller |
| `storage.js` | Data persistence layer |
| `habits.js` | Habits tracking module |
| `tasks.js` | Tasks/todos module |
| `finances.js` | Finances/budget module |
| `health.js` | Health metrics module |
| `time.js` | Time tracking module |
| `goals.js` | Goals module |
| `achievements.js` | Achievements/gamification |
| `charts.js` | Chart visualization |
| `notifications.js` | Notification system |
| `dataExport.js` | Import/export functionality |

---

## Module Pattern

All modules follow this consistent pattern:

```javascript
const ModuleName = {
    // 1. Configuration
    config: {
        // module-specific settings
    },

    // 2. State
    items: [],
    currentId: null,

    // 3. Initialization
    init() {
        this.loadData();
        this.render();
        this.setupEventListeners();
    },

    // 4. Data methods
    loadData() { },
    saveData() { },
    addItem(item) { },
    updateItem(id, updates) { },
    deleteItem(id) { },

    // 5. Rendering
    render() { },
    renderList() { },
    renderItem(item) { },

    // 6. Event handlers
    setupEventListeners() { },
    handleAdd() { },
    handleEdit(id) { },
    handleDelete(id) { },

    // 7. Utilities
    validate(data) { },
    format(data) { }
};

window.ModuleName = ModuleName;
```

---

## App Module (`app.js`)

Main application controller:

```javascript
const App = {
    currentView: 'dashboard',
    
    init() {
        this.setupNavigation();
        this.setupTheme();
        this.updateAll();
    },
    
    navigateTo(view) {
        // Switch views
    },
    
    showToast(message, type) {
        // Show notification
    },
    
    celebrate() {
        // Confetti effect
    }
};
```

---

## Storage Module (`storage.js`)

Data persistence layer:

```javascript
const Storage = {
    // User data
    getUserData() { },
    saveUserData(data) { },
    
    // Habits
    getHabits() { },
    saveHabits(habits) { },
    
    // Tasks
    getTasks() { },
    saveTasks(tasks) { },
    
    // Settings
    getSettings() { },
    saveSettings(settings) { }
};
```

---

## Habits Module (`habits.js`)

Habit tracking:

```javascript
const Habits = {
    items: [],
    
    init() { },
    addHabit(habit) { },
    completeHabit(id) { },
    calculateStreak(id) { },
    getTotalStreaks() { }
};
```

---

## Tasks Module (`tasks.js`)

Task management:

```javascript
const Tasks = {
    items: [],
    
    init() { },
    addTask(task) { },
    completeTask(id) { },
    getCompletedTodayCount() { },
    renderQuickTasks() { }
};
```

---

## Finances Module (`finances.js`)

Financial tracking:

```javascript
const Finances = {
    transactions: [],
    
    init() { },
    addTransaction(tx) { },
    getTotalBalance() { },
    formatCurrency(amount) { }
};
```

---

## Health Module (`health.js`)

Health metrics:

```javascript
const Health = {
    entries: [],
    
    init() { },
    addEntry(entry) { },
    getHealthScore() { }
};
```

---

## Goals Module (`goals.js`)

Goal tracking:

```javascript
const Goals = {
    items: [],
    
    init() { },
    addGoal(goal) { },
    updateProgress(id, value) { },
    renderGoalsOverview() { }
};
```

---

## Achievements Module (`achievements.js`)

Gamification:

```javascript
const Achievements = {
    unlocked: [],
    
    init() { },
    checkAchievements() { },
    unlock(id) { },
    render() { }
};
```

---

## Charts Module (`charts.js`)

Data visualization:

```javascript
const Charts = {
    initWeeklyChart(canvasId) { },
    updateChart(canvasId, data) { }
};
```

---

## Coding Standards

1. **Use const/let, never var**
2. **Arrow functions for callbacks**
3. **Template literals for HTML**
4. **Optional chaining for DOM elements**
5. **JSDoc comments for complex functions**

---

## Cross-References

| Topic | File |
|-------|------|
| Project rules | `PROJECT_RULES.md` |
| CSS styles | `css/README.md` |
| Main README | `README.md` |

---

**Last Updated:** February 2026