# IndexedDB Migration Guide

**Feature:** LocalStorage to IndexedDB Migration  
**Phase:** 1.4  
**Priority:** Medium  
**Effort:** Medium

---

## Overview

This guide covers migrating TrackLife from LocalStorage to IndexedDB using Dexie.js, enabling better performance, larger storage capacity, and query capabilities.

---

## Why Migrate?

### LocalStorage Limitations

| Limitation | Impact |
|------------|--------|
| 5-10MB limit | Can't store large datasets |
| Synchronous API | Blocks UI thread |
| String-only | Must serialize/deserialize |
| No queries | Must load all data to filter |
| No indexing | Slow lookups |

### IndexedDB Benefits

| Benefit | Impact |
|---------|--------|
| Unlimited storage | Store years of data |
| Asynchronous API | Non-blocking operations |
| Structured data | Store objects directly |
| Indexed queries | Fast filtering and sorting |
| Transactions | Data integrity |

---

## Setup

### Add Dexie.js

**Option 1: CDN**
```html
<script src="https://unpkg.com/dexie@latest/dist/dexie.min.js"></script>
```

**Option 2: NPM**
```bash
npm install dexie
```

```javascript
import Dexie from 'dexie';
```

---

## Database Schema

### Define Schema

```javascript
// js/db.js
const db = new Dexie('TrackLifeDB');

db.version(1).stores({
    // Core entities
    habits: '++id, name, createdAt, updatedAt',
    tasks: '++id, title, priority, dueDate, completed, createdAt',
    goals: '++id, title, deadline, createdAt',
    
    // Tracking data
    habitCompletions: '++id, habitId, date, completed, score',
    healthEntries: '++id, type, date, value, unit',
    timeEntries: '++id, category, startTime, endTime, duration',
    financialTransactions: '++id, type, category, amount, date',
    
    // Events and logs
    events: '++id, type, timestamp',
    achievements: '++id, name, unlockedAt',
    
    // User data (key-value store)
    userData: 'key'
});

// Make globally available
window.db = db;

export default db;
```

### Schema Syntax

| Prefix | Meaning |
|--------|---------|
| `++id` | Auto-incrementing primary key |
| `id` | Primary key (not auto) |
| `&id` | Unique constraint |
| `*tags` | Multi-entry index (arrays) |

---

## Migration Process

### Step 1: Create Migration Module

```javascript
// js/migration.js
const Migration = {
    version: 1,
    
    async run() {
        console.log('Starting migration to IndexedDB...');
        
        // Check if already migrated
        const migrated = await db.userData.get('migrated');
        if (migrated?.value) {
            console.log('Already migrated, skipping.');
            return true;
        }
        
        try {
            // Backup LocalStorage
            this.backupLocalStorage();
            
            // Migrate each data type
            await this.migrateHabits();
            await this.migrateTasks();
            await this.migrateGoals();
            await this.migrateHealthData();
            await this.migrateFinancialData();
            await this.migrateUserData();
            
            // Mark as migrated
            await db.userData.put({
                key: 'migrated',
                value: true,
                version: this.version,
                timestamp: new Date().toISOString()
            });
            
            console.log('Migration completed successfully!');
            return true;
        } catch (error) {
            console.error('Migration failed:', error);
            // Restore from backup
            this.restoreLocalStorage();
            return false;
        }
    },
    
    backupLocalStorage() {
        const backup = {};
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            backup[key] = localStorage.getItem(key);
        }
        localStorage.setItem('tracklife_backup', JSON.stringify(backup));
        console.log('LocalStorage backed up.');
    },
    
    restoreLocalStorage() {
        const backup = JSON.parse(localStorage.getItem('tracklife_backup') || '{}');
        for (const [key, value] of Object.entries(backup)) {
            localStorage.setItem(key, value);
        }
        console.log('LocalStorage restored from backup.');
    },
    
    async migrateHabits() {
        const habits = JSON.parse(localStorage.getItem('habits') || '[]');
        if (habits.length === 0) return;
        
        // Transform data
        const transformed = habits.map(h => ({
            ...h,
            createdAt: h.createdAt || new Date().toISOString(),
            updatedAt: new Date().toISOString()
        }));
        
        await db.habits.bulkAdd(transformed);
        console.log(`Migrated ${habits.length} habits`);
    },
    
    async migrateTasks() {
        const tasks = JSON.parse(localStorage.getItem('tasks') || '[]');
        if (tasks.length === 0) return;
        
        const transformed = tasks.map(t => ({
            ...t,
            createdAt: t.createdAt || new Date().toISOString()
        }));
        
        await db.tasks.bulkAdd(transformed);
        console.log(`Migrated ${tasks.length} tasks`);
    },
    
    async migrateGoals() {
        const goals = JSON.parse(localStorage.getItem('goals') || '[]');
        if (goals.length === 0) return;
        
        await db.goals.bulkAdd(goals);
        console.log(`Migrated ${goals.length} goals`);
    },
    
    async migrateHealthData() {
        const health = JSON.parse(localStorage.getItem('healthData') || '[]');
        if (health.length === 0) return;
        
        const transformed = health.map(h => ({
            ...h,
            date: h.date || new Date().toISOString().split('T')[0]
        }));
        
        await db.healthEntries.bulkAdd(transformed);
        console.log(`Migrated ${health.length} health entries`);
    },
    
    async migrateFinancialData() {
        const transactions = JSON.parse(localStorage.getItem('transactions') || '[]');
        if (transactions.length === 0) return;
        
        await db.financialTransactions.bulkAdd(transactions);
        console.log(`Migrated ${transactions.length} transactions`);
    },
    
    async migrateUserData() {
        const userData = {
            xp: parseInt(localStorage.getItem('xp') || '0'),
            level: parseInt(localStorage.getItem('level') || '1'),
            achievements: JSON.parse(localStorage.getItem('achievements') || '[]'),
            settings: JSON.parse(localStorage.getItem('settings') || '{}')
        };
        
        await db.userData.bulkPut([
            { key: 'xp', value: userData.xp },
            { key: 'level', value: userData.level },
            { key: 'achievements', value: userData.achievements },
            { key: 'settings', value: userData.settings }
        ]);
        
        console.log('Migrated user data');
    }
};

window.Migration = Migration;
```

### Step 2: Run Migration on App Start

```javascript
// js/app.js
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize database
    await db.open();
    
    // Run migration
    await Migration.run();
    
    // Initialize app
    App.init();
});
```

---

## Update Storage Module

### Before (LocalStorage)

```javascript
// js/storage.js (old)
const Storage = {
    getHabits() {
        return JSON.parse(localStorage.getItem('habits') || '[]');
    },
    
    saveHabits(habits) {
        localStorage.setItem('habits', JSON.stringify(habits));
    },
    
    addHabit(habit) {
        const habits = this.getHabits();
        habits.push(habit);
        this.saveHabits(habits);
    }
};
```

### After (IndexedDB)

```javascript
// js/storage.js (new)
const Storage = {
    // Habits
    async getHabits() {
        return await db.habits.toArray();
    },
    
    async getHabit(id) {
        return await db.habits.get(id);
    },
    
    async addHabit(habit) {
        const habitWithTimestamp = {
            ...habit,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };
        const id = await db.habits.add(habitWithTimestamp);
        
        // Emit event
        EventStore.emit('HABIT_CREATED', { id, ...habitWithTimestamp });
        
        return id;
    },
    
    async updateHabit(id, changes) {
        await db.habits.update(id, {
            ...changes,
            updatedAt: new Date().toISOString()
        });
        
        EventStore.emit('HABIT_UPDATED', { id, changes });
    },
    
    async deleteHabit(id) {
        await db.habits.delete(id);
        EventStore.emit('HABIT_DELETED', { id });
    },
    
    // Habit Completions
    async getCompletions(habitId, startDate, endDate) {
        return await db.habitCompletions
            .where('habitId').equals(habitId)
            .and(c => c.date >= startDate && c.date <= endDate)
            .toArray();
    },
    
    async markComplete(habitId, date) {
        const existing = await db.habitCompletions
            .where('[habitId+date]').equals([habitId, date])
            .first();
        
        if (existing) {
            await db.habitCompletions.update(existing.id, { completed: true });
        } else {
            await db.habitCompletions.add({
                habitId,
                date,
                completed: true,
                score: 1
            });
        }
        
        EventStore.emit('HABIT_COMPLETED', { habitId, date });
    },
    
    // Tasks
    async getTasks(filter = {}) {
        let query = db.tasks;
        
        if (filter.completed !== undefined) {
            query = query.where('completed').equals(filter.completed);
        }
        
        return await query.toArray();
    },
    
    async addTask(task) {
        const id = await db.tasks.add({
            ...task,
            createdAt: new Date().toISOString()
        });
        
        EventStore.emit('TASK_CREATED', { id, ...task });
        return id;
    },
    
    // User Data
    async getUserData() {
        const data = await db.userData.toArray();
        const result = {};
        for (const item of data) {
            result[item.key] = item.value;
        }
        return result;
    },
    
    async saveUserData(key, value) {
        await db.userData.put({ key, value });
    }
};

window.Storage = Storage;
```

---

## Query Examples

### Get Recent Habits

```javascript
const recentHabits = await db.habits
    .orderBy('updatedAt')
    .reverse()
    .limit(10)
    .toArray();
```

### Get Tasks Due Today

```javascript
const today = new Date().toISOString().split('T')[0];
const dueToday = await db.tasks
    .where('dueDate').equals(today)
    .and(t => !t.completed)
    .toArray();
```

### Get Completions for Date Range

```javascript
const completions = await db.habitCompletions
    .where('date')
    .between('2026-02-01', '2026-02-14')
    .toArray();
```

### Get Health Metrics by Type

```javascript
const sleepData = await db.healthEntries
    .where('type').equals('sleep')
    .orderBy('date')
    .reverse()
    .limit(30)
    .toArray();
```

---

## Performance Tips

### Use Bulk Operations

```javascript
// Slow - individual operations
for (const habit of habits) {
    await db.habits.add(habit);
}

// Fast - bulk operation
await db.habits.bulkAdd(habits);
```

### Use Indexes for Queries

```javascript
// Indexed query (fast)
await db.tasks.where('dueDate').equals(today).toArray();

// Non-indexed query (slow)
await db.tasks.filter(t => t.dueDate === today).toArray();
```

### Use Transactions

```javascript
await db.transaction('rw', db.habits, db.habitCompletions, async () => {
    await db.habits.update(habitId, { streak: newStreak });
    await db.habitCompletions.add({ habitId, date, completed: true });
});
```

---

## Testing

### Test Migration

```javascript
// js/tests/migration.test.js
describe('Migration', () => {
    beforeEach(async () => {
        // Clear database
        await db.delete();
        await db.open();
    });
    
    test('migrates habits correctly', async () => {
        // Setup LocalStorage data
        localStorage.setItem('habits', JSON.stringify([
            { id: 1, name: 'Exercise' },
            { id: 2, name: 'Read' }
        ]));
        
        await Migration.run();
        
        const habits = await db.habits.toArray();
        expect(habits.length).toBe(2);
    });
    
    test('backs up LocalStorage', async () => {
        localStorage.setItem('test', 'value');
        Migration.backupLocalStorage();
        
        const backup = localStorage.getItem('tracklife_backup');
        expect(backup).toBeTruthy();
    });
});
```

---

## Rollback Plan

If migration fails:

1. **Automatic restore** - Migration module restores from backup
2. **Manual restore** - User can restore from `tracklife_backup` in LocalStorage
3. **Fresh start** - Clear IndexedDB and re-import data

```javascript
async function rollbackMigration() {
    await db.delete();
    Migration.restoreLocalStorage();
    location.reload();
}
```

---

## Implementation Checklist

- [ ] Add Dexie.js to project
- [ ] Create database schema
- [ ] Create migration module
- [ ] Update Storage module
- [ ] Update all modules to use async Storage
- [ ] Test migration with sample data
- [ ] Test rollback procedure
- [ ] Update documentation

---

## References

- **Dexie.js Documentation:** https://dexie.org/
- **IndexedDB API:** https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API
- **Research:** [docs/research/TECHNICAL_ARCHITECTURES.md](../research/TECHNICAL_ARCHITECTURES.md)
- **Phase:** [phases/PHASE_1_FOUNDATION.md](../../phases/PHASE_1_FOUNDATION.md)

---

*Last updated: February 2026*