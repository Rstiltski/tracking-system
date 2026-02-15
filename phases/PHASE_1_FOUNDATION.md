# Phase 1: Foundation Strengthening

**Duration:** 2 weeks  
**Status:** 🟡 In Progress  
**Dependencies:** None

---

## Overview

Phase 1 focuses on strengthening the foundational elements of TrackLife by:
1. Replacing rigid streaks with a scientific Habit Score algorithm
2. Adding Streak Freeze to prevent user churn
3. Implementing Event Sourcing for data integrity
4. Migrating from LocalStorage to IndexedDB

---

## Goals

| Goal | Success Metric |
|------|----------------|
| Scientific habit measurement | Habit Score displays for all habits (0-100%) |
| Reduce churn from broken streaks | Streak Freeze can be earned and consumed |
| Data integrity and audit trail | All operations emit immutable events |
| Better storage foundation | Data persists in IndexedDB with migration |

---

## Phase 1.1: Habit Score Algorithm

**Priority:** High  
**Effort:** Low  
**Duration:** 2-3 days

### Problem

Current streak system is binary and demotivating:
- User with 100-day streak misses one day → streak resets to 0
- This causes users to quit entirely ("what-the-hell" effect)
- Doesn't show actual habit strength

### Solution

Implement Loop's weighted moving average algorithm:
- Score from 0.0 to 1.0 (display as 0-100%)
- Recent days have higher weight
- Gradual decay on misses, not reset to zero
- More forgiving and scientifically accurate

### Algorithm

```
Habit Score = Σ(completion[i] × weight[i]) / Σ(weight[i])

Where:
- completion[i] = 1 if completed on day i, 0 if not
- weight[i] = exp(-λ × i)  (exponential decay)
- λ = decay rate (default: 0.05)
- i = days ago (0 = today, 1 = yesterday, etc.)
```

### Tasks

- [ ] Research Loop's weighted moving average algorithm
- [ ] Design TrackLife's Habit Score formula
- [ ] Create `js/habit-score.js` module
- [ ] Update `js/habits.js` to use Habit Score
- [ ] Add Habit Score visualization to UI
- [ ] Write tests for Habit Score calculation

### Implementation

```javascript
// js/habit-score.js
const HabitScore = {
    config: {
        decayRate: 0.05,  // λ - controls how quickly old days lose weight
        lookbackDays: 60  // How many days to consider
    },
    
    /**
     * Calculate habit score from completion history
     * @param {Array<boolean>} completions - Array of completion status (newest first)
     * @returns {number} Score from 0.0 to 1.0
     */
    calculate(completions) {
        if (!completions || completions.length === 0) return 0;
        
        let weightedSum = 0;
        let totalWeight = 0;
        
        const daysToConsider = Math.min(completions.length, this.config.lookbackDays);
        
        for (let i = 0; i < daysToConsider; i++) {
            const weight = Math.exp(-this.config.decayRate * i);
            totalWeight += weight;
            
            if (completions[i]) {
                weightedSum += weight;
            }
        }
        
        return totalWeight > 0 ? weightedSum / totalWeight : 0;
    },
    
    /**
     * Get score as percentage (0-100)
     */
    getPercentage(completions) {
        return Math.round(this.calculate(completions) * 100);
    },
    
    /**
     * Get score category for display
     */
    getCategory(score) {
        if (score >= 0.85) return { label: 'Excellent', color: '#4CAF50', emoji: '🌟' };
        if (score >= 0.70) return { label: 'Strong', color: '#8BC34A', emoji: '💪' };
        if (score >= 0.50) return { label: 'Developing', color: '#FFC107', emoji: '🌱' };
        if (score >= 0.30) return { label: 'Building', color: '#FF9800', emoji: '🔧' };
        return { label: 'Starting', color: '#F44336', emoji: '🆕' };
    }
};

window.HabitScore = HabitScore;
```

### UI Changes

```html
<!-- Replace streak display with score -->
<div class="habit-score">
    <div class="score-ring" style="--score: 75%">
        <span class="score-value">75%</span>
    </div>
    <div class="score-label">
        <span class="emoji">💪</span>
        <span class="text">Strong</span>
    </div>
</div>
```

### Reference

- [docs/specs/HABIT_SCORE_SPEC.md](../docs/specs/HABIT_SCORE_SPEC.md)
- [docs/research/OPEN_SOURCE_PROJECTS.md](../docs/research/OPEN_SOURCE_PROJECTS.md) - Loop section

---

## Phase 1.2: Streak Freeze Mechanic

**Priority:** High  
**Effort:** Low  
**Duration:** 2-3 days

### Problem

When users break a streak:
1. They feel discouraged
2. "What-the-hell" effect kicks in
3. They abandon the habit entirely

### Solution

Streak Freeze is an item that:
- Preserves streak on a missed day
- Is consumed automatically when needed
- Can be earned through consistent tracking or purchased with XP

### Tasks

- [ ] Design streak freeze inventory system
- [ ] Add freeze data to user schema
- [ ] Implement freeze consumption logic
- [ ] Add freeze earning mechanisms (XP purchase, achievements)
- [ ] Update streak calculation to respect freezes
- [ ] Add freeze management UI

### Data Model

```javascript
// Add to user data
const userData = {
    // ... existing fields
    inventory: {
        streakFreezes: 3,  // Current count
        maxFreezes: 10     // Maximum allowed
    },
    freezeHistory: [
        { habitId: 'abc123', date: '2026-02-10', used: true }
    ]
};
```

### Implementation

```javascript
// js/streak-freeze.js
const StreakFreeze = {
    config: {
        maxFreezes: 10,
        xpCost: 100,
        earnThreshold: 7  // Days of consistency to earn one
    },
    
    /**
     * Check if streak freeze is available
     */
    hasFreeze() {
        const userData = Storage.getUserData();
        return userData.inventory?.streakFreezes > 0;
    },
    
    /**
     * Use a streak freeze for a habit
     */
    useFreeze(habitId, date) {
        const userData = Storage.getUserData();
        
        if (!this.hasFreeze()) return false;
        
        userData.inventory.streakFreezes--;
        userData.freezeHistory = userData.freezeHistory || [];
        userData.freezeHistory.push({
            habitId,
            date,
            used: true,
            timestamp: new Date().toISOString()
        });
        
        Storage.saveUserData(userData);
        return true;
    },
    
    /**
     * Purchase a streak freeze with XP
     */
    purchaseFreeze() {
        const userData = Storage.getUserData();
        
        if (userData.xp < this.config.xpCost) return false;
        if (userData.inventory.streakFreezes >= this.config.maxFreezes) return false;
        
        userData.xp -= this.config.xpCost;
        userData.inventory.streakFreezes++;
        
        Storage.saveUserData(userData);
        return true;
    },
    
    /**
     * Award a freeze for consistency
     */
    awardFreeze() {
        const userData = Storage.getUserData();
        
        if (userData.inventory.streakFreezes >= this.config.maxFreezes) return false;
        
        userData.inventory.streakFreezes++;
        Storage.saveUserData(userData);
        
        // Show notification
        Notifications.show('❄️ Streak Freeze earned!', 'Keep up the great work!');
        return true;
    }
};

window.StreakFreeze = StreakFreeze;
```

### UI

```html
<!-- Streak freeze display -->
<div class="streak-freeze-widget">
    <span class="freeze-icon">❄️</span>
    <span class="freeze-count">3</span>
    <button class="purchase-freeze" onclick="StreakFreeze.purchaseFreeze()">
        Buy (100 XP)
    </button>
</div>
```

### Reference

- [docs/specs/STREAK_FREEZE_SPEC.md](../docs/specs/STREAK_FREEZE_SPEC.md)
- [docs/research/BEHAVIORAL_SCIENCE.md](../docs/research/BEHAVIORAL_SCIENCE.md) - Loss Aversion section

---

## Phase 1.3: Event Sourcing Foundation

**Priority:** Medium  
**Effort:** Medium  
**Duration:** 3-4 days

### Problem

Current system stores only current state:
- No audit trail of changes
- Can't reconstruct past states
- Difficult to debug issues
- Limited analytics capability

### Solution

Store all changes as immutable events:
- Complete history of all operations
- Can replay to any point in time
- Rich data for analytics
- Natural undo/redo support

### Tasks

- [ ] Design event schema (immutable events)
- [ ] Create `js/event-store.js` module
- [ ] Update data operations to emit events
- [ ] Add event replay capability
- [ ] Migrate existing data to events

### Event Schema

```javascript
// Base event structure
const event = {
    id: 'uuid-v4',
    type: 'HABIT_COMPLETED',
    timestamp: '2026-02-14T10:00:00Z',
    version: '1.0',
    payload: {
        habitId: 'abc123',
        date: '2026-02-14'
    },
    metadata: {
        source: 'web-ui',
        userId: 'user-123'
    }
};
```

### Event Types

| Event Type | Payload |
|------------|---------|
| `HABIT_CREATED` | `{ id, name, frequency, ... }` |
| `HABIT_UPDATED` | `{ id, changes }` |
| `HABIT_COMPLETED` | `{ id, date }` |
| `HABIT_MISSED` | `{ id, date }` |
| `HABIT_DELETED` | `{ id }` |
| `STREAK_FREEZE_USED` | `{ habitId, date }` |
| `TASK_CREATED` | `{ id, title, priority, ... }` |
| `TASK_COMPLETED` | `{ id, date }` |

### Implementation

```javascript
// js/event-store.js
const EventStore = {
    events: [],
    
    init() {
        this.loadEvents();
    },
    
    /**
     * Emit a new event
     */
    emit(type, payload, metadata = {}) {
        const event = {
            id: crypto.randomUUID(),
            type,
            timestamp: new Date().toISOString(),
            version: '1.0',
            payload,
            metadata: {
                source: 'web-ui',
                ...metadata
            }
        };
        
        this.events.push(event);
        this.saveEvents();
        
        // Notify subscribers
        this.notifySubscribers(event);
        
        return event;
    },
    
    /**
     * Get events by type
     */
    getByType(type) {
        return this.events.filter(e => e.type === type);
    },
    
    /**
     * Get events for an entity
     */
    getByEntity(entityType, entityId) {
        return this.events.filter(e => 
            e.payload.id === entityId || 
            e.payload[entityType + 'Id'] === entityId
        );
    },
    
    /**
     * Replay events to reconstruct state
     */
    replay(upToTimestamp = null) {
        const state = {};
        const events = upToTimestamp 
            ? this.events.filter(e => e.timestamp <= upToTimestamp)
            : this.events;
        
        for (const event of events) {
            this.applyEvent(state, event);
        }
        
        return state;
    },
    
    /**
     * Apply event to state
     */
    applyEvent(state, event) {
        switch (event.type) {
            case 'HABIT_CREATED':
                state.habits = state.habits || [];
                state.habits.push({ id: event.payload.id, ...event.payload });
                break;
            case 'HABIT_COMPLETED':
                // Update completion state
                break;
            // ... other event types
        }
    },
    
    saveEvents() {
        localStorage.setItem('tracklife_events', JSON.stringify(this.events));
    },
    
    loadEvents() {
        const stored = localStorage.getItem('tracklife_events');
        this.events = stored ? JSON.parse(stored) : [];
    }
};

window.EventStore = EventStore;
```

### Reference

- [docs/schemas/EVENT_SCHEMA.md](../docs/schemas/EVENT_SCHEMA.md)
- [docs/research/TECHNICAL_ARCHITECTURES.md](../docs/research/TECHNICAL_ARCHITECTURES.md) - Event Sourcing section

---

## Phase 1.4: IndexedDB Migration

**Priority:** Medium  
**Effort:** Medium  
**Duration:** 3-4 days

### Problem

LocalStorage limitations:
- 5-10MB storage limit
- Synchronous API (blocks UI)
- No query capability
- String-only storage

### Solution

Migrate to IndexedDB via Dexie.js:
- Unlimited storage
- Asynchronous API
- Query and index support
- Structured data storage

### Tasks

- [ ] Add Dexie.js library
- [ ] Define database schema
- [ ] Create migration script from LocalStorage
- [ ] Update all modules to use IndexedDB
- [ ] Test data persistence and performance

### Database Schema

```javascript
// js/db.js
import Dexie from 'dexie';

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
    
    // User data
    userData: 'key'
});

window.db = db;
```

### Migration Script

```javascript
// js/migration.js
const Migration = {
    async migrateFromLocalStorage() {
        console.log('Starting migration from LocalStorage to IndexedDB...');
        
        try {
            // Check if already migrated
            const existingData = await db.userData.get('migrated');
            if (existingData?.value) {
                console.log('Already migrated, skipping.');
                return true;
            }
            
            // Migrate habits
            const habits = JSON.parse(localStorage.getItem('habits') || '[]');
            if (habits.length > 0) {
                await db.habits.bulkAdd(habits);
                console.log(`Migrated ${habits.length} habits`);
            }
            
            // Migrate tasks
            const tasks = JSON.parse(localStorage.getItem('tasks') || '[]');
            if (tasks.length > 0) {
                await db.tasks.bulkAdd(tasks);
                console.log(`Migrated ${tasks.length} tasks`);
            }
            
            // Migrate other data...
            
            // Mark as migrated
            await db.userData.put({ key: 'migrated', value: true, timestamp: new Date().toISOString() });
            
            console.log('Migration completed successfully!');
            return true;
        } catch (error) {
            console.error('Migration failed:', error);
            return false;
        }
    }
};

window.Migration = Migration;
```

### Reference

- [docs/guides/INDEXEDDB_MIGRATION.md](../docs/guides/INDEXEDDB_MIGRATION.md)
- [docs/research/TECHNICAL_ARCHITECTURES.md](../docs/research/TECHNICAL_ARCHITECTURES.md) - Local-First section

---

## Success Criteria

| Criteria | How to Verify |
|----------|---------------|
| Habit Score works | All habits show 0-100% score |
| Streak Freeze works | Can earn, use, and purchase freezes |
| Event Sourcing works | Events recorded for all operations |
| IndexedDB works | Data persists after migration |

---

## Dependencies

| Dependency | Purpose | Install |
|------------|---------|---------|
| Dexie.js | IndexedDB wrapper | `npm install dexie` or CDN |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Data loss during migration | Keep LocalStorage backup, verify before clearing |
| Performance regression | Test with large datasets, optimize queries |
| User confusion with new score | Add explanation tooltips, gradual rollout |

---

## Next Phase

After completing Phase 1, proceed to:
- [Phase 2: Intelligence Layer](PHASE_2_INTELLIGENCE.md)

---

*Last updated: February 2026*