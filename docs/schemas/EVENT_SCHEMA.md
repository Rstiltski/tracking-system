# Event Schema Specification

**Feature:** Event Sourcing Data Model  
**Phase:** 1.3  
**Priority:** Medium  
**Effort:** Medium

---

## Overview

This document defines the event schema for TrackLife's event sourcing system. All data changes are stored as immutable events, enabling audit trails, time travel, and rich analytics.

---

## Base Event Structure

All events follow this base structure:

```typescript
interface Event {
    id: string;           // UUID v4
    type: string;         // Event type (e.g., "HABIT_COMPLETED")
    timestamp: string;    // ISO 8601 datetime
    version: string;      // Schema version (e.g., "1.0")
    payload: object;      // Event-specific data
    metadata: {
        source: string;   // Where event originated (e.g., "web-ui", "api")
        userId?: string;  // User identifier (if multi-user)
        correlationId?: string;  // For linking related events
    };
}
```

---

## Event Types

### Habit Events

#### HABIT_CREATED

```typescript
{
    type: "HABIT_CREATED",
    payload: {
        id: string;
        name: string;
        description?: string;
        frequency: "daily" | "weekly" | "custom";
        targetDays?: number[];  // [0,1,2,3,4,5,6] for custom
        reminder?: {
            enabled: boolean;
            time?: string;  // "HH:MM"
        };
        color?: string;
        icon?: string;
    }
}
```

#### HABIT_UPDATED

```typescript
{
    type: "HABIT_UPDATED",
    payload: {
        id: string;
        changes: {
            name?: string;
            description?: string;
            frequency?: string;
            targetDays?: number[];
            reminder?: object;
            color?: string;
            icon?: string;
        }
    }
}
```

#### HABIT_COMPLETED

```typescript
{
    type: "HABIT_COMPLETED",
    payload: {
        habitId: string;
        date: string;  // "YYYY-MM-DD"
        completedAt: string;  // ISO 8601
        notes?: string;
    }
}
```

#### HABIT_MISSED

```typescript
{
    type: "HABIT_MISSED",
    payload: {
        habitId: string;
        date: string;
        reason?: string;
    }
}
```

#### HABIT_DELETED

```typescript
{
    type: "HABIT_DELETED",
    payload: {
        id: string;
        deletedAt: string;
    }
}
```

### Streak Freeze Events

#### STREAK_FREEZE_USED

```typescript
{
    type: "STREAK_FREEZE_USED",
    payload: {
        habitId: string;
        date: string;
        previousStreak: number;
    }
}
```

#### STREAK_FREEZE_PURCHASED

```typescript
{
    type: "STREAK_FREEZE_PURCHASED",
    payload: {
        quantity: number;
        xpCost: number;
    }
}
```

#### STREAK_FREEZE_EARNED

```typescript
{
    type: "STREAK_FREEZE_EARNED",
    payload: {
        reason: "consistency" | "achievement";
        relatedId?: string;  // Achievement ID if applicable
    }
}
```

### Task Events

#### TASK_CREATED

```typescript
{
    type: "TASK_CREATED",
    payload: {
        id: string;
        title: string;
        description?: string;
        priority: "low" | "medium" | "high";
        dueDate?: string;
        tags?: string[];
    }
}
```

#### TASK_COMPLETED

```typescript
{
    type: "TASK_COMPLETED",
    payload: {
        id: string;
        completedAt: string;
    }
}
```

#### TASK_UPDATED

```typescript
{
    type: "TASK_UPDATED",
    payload: {
        id: string;
        changes: object;
    }
}
```

#### TASK_DELETED

```typescript
{
    type: "TASK_DELETED",
    payload: {
        id: string;
    }
}
```

### Health Events

#### HEALTH_LOGGED

```typescript
{
    type: "HEALTH_LOGGED",
    payload: {
        metric: "sleep" | "weight" | "steps" | "water" | "mood" | "energy";
        value: number;
        unit: string;
        date: string;
        time?: string;
        notes?: string;
    }
}
```

### Financial Events

#### TRANSACTION_CREATED

```typescript
{
    type: "TRANSACTION_CREATED",
    payload: {
        id: string;
        type: "income" | "expense";
        amount: number;
        category: string;
        description?: string;
        date: string;
    }
}
```

### Goal Events

#### GOAL_CREATED

```typescript
{
    type: "GOAL_CREATED",
    payload: {
        id: string;
        title: string;
        description?: string;
        deadline?: string;
        milestones?: Array<{
            id: string;
            title: string;
            target: number;
        }>;
    }
}
```

#### GOAL_PROGRESS_UPDATED

```typescript
{
    type: "GOAL_PROGRESS_UPDATED",
    payload: {
        goalId: string;
        milestoneId?: string;
        progress: number;
        previousProgress: number;
    }
}
```

### Gamification Events

#### XP_EARNED

```typescript
{
    type: "XP_EARNED",
    payload: {
        amount: number;
        source: "habit" | "task" | "achievement" | "bonus";
        relatedId?: string;
    }
}
```

#### LEVEL_UP

```typescript
{
    type: "LEVEL_UP",
    payload: {
        newLevel: number;
        previousLevel: number;
    }
}
```

#### ACHIEVEMENT_UNLOCKED

```typescript
{
    type: "ACHIEVEMENT_UNLOCKED",
    payload: {
        achievementId: string;
        name: string;
        description: string;
        xpReward: number;
    }
}
```

---

## Event Store API

### Storage

```javascript
// IndexedDB schema for events
db.version(1).stores({
    events: '++id, type, timestamp, *payload.habitId, *payload.id'
});
```

### Query Patterns

```javascript
// Get all events for a habit
const habitEvents = await db.events
    .where('payload.habitId').equals(habitId)
    .toArray();

// Get events by type
const completions = await db.events
    .where('type').equals('HABIT_COMPLETED')
    .toArray();

// Get events in date range
const recentEvents = await db.events
    .where('timestamp')
    .between(startDate, endDate)
    .toArray();
```

---

## Event Replay

### Reconstructing State

```javascript
function replayEvents(events) {
    const state = {
        habits: [],
        tasks: [],
        goals: [],
        xp: 0,
        level: 1
    };
    
    for (const event of events) {
        applyEvent(state, event);
    }
    
    return state;
}

function applyEvent(state, event) {
    switch (event.type) {
        case 'HABIT_CREATED':
            state.habits.push({
                id: event.payload.id,
                ...event.payload,
                completions: {},
                streak: 0
            });
            break;
            
        case 'HABIT_COMPLETED':
            const habit = state.habits.find(h => h.id === event.payload.habitId);
            if (habit) {
                habit.completions[event.payload.date] = true;
                // Recalculate streak
            }
            break;
            
        case 'XP_EARNED':
            state.xp += event.payload.amount;
            // Check for level up
            break;
            
        // ... other event types
    }
}
```

---

## Event Versioning

When event schemas change:

1. **Add new fields as optional** - Don't break old events
2. **Increment version** - Track schema version
3. **Handle both versions** - Support old and new formats

```javascript
function applyEvent(state, event) {
    // Handle version differences
    const payload = migratePayload(event);
    
    // Apply event logic
    // ...
}

function migratePayload(event) {
    if (event.version === '1.0') {
        // Handle v1.0 format
        return event.payload;
    }
    // Future versions
    return event.payload;
}
```

---

## Implementation Checklist

- [ ] Create EventStore module
- [ ] Define all event types
- [ ] Implement emit() function
- [ ] Implement query functions
- [ ] Implement replay function
- [ ] Add event versioning support
- [ ] Create migration utilities

---

## References

- **Source:** ActivityWatch (ActivityWatch/activitywatch)
- **Research:** [docs/research/TECHNICAL_ARCHITECTURES.md](../research/TECHNICAL_ARCHITECTURES.md)
- **Phase:** [phases/PHASE_1_FOUNDATION.md](../../phases/PHASE_1_FOUNDATION.md)

---

*Last updated: February 2026*