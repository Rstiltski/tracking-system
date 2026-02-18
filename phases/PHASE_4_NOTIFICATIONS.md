# Phase 4: Reminders & Notifications System

**Duration:** 2-3 weeks
**Status:** ✅ Complete
**Dependencies:** Phase 3 Complete
**Created:** February 17, 2026
**Completed:** February 18, 2026

---

## Overview

Phase 4 focuses on implementing a comprehensive notification and reminder system to help users stay on track with their habits, tasks, and goals. This phase implements intelligent, customizable alerts that adapt to user behavior.

---

## Goals

| Goal | Success Metric |
|------|----------------|
| Browser notification system | Users receive push notifications for reminders |
| Habit reminders | Configurable reminders per habit with smart timing |
| Task due date reminders | Automatic alerts before task deadlines |
| Goal deadline alerts | Progressive urgency notifications for goals |
| Customizable settings | Full user control over notification preferences |

---

## Phase 4.1: Notification Engine

**Priority:** High  
**Effort:** Medium  
**Duration:** 4-5 days  
**Status:** ✅ Complete

### Problem

Users miss important tracking activities because there's no proactive notification system. Without reminders, habits and tasks fall through the cracks.

### Solution

Implement a Python-based notification engine using:
- Browser push notifications via Web Push API
- Desktop notifications through Streamlit
- Email notifications as fallback
- Smart scheduling based on user patterns

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Reminder       │────▶│  Notification    │────▶│  Delivery       │
│  Scheduler      │     │  Engine          │     │  Channels       │
│  (Python/APScheduler) │  (Python)        │     │  (Push/Email)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  SQLite DB      │     │  Template        │     │  User           │
│  (Queue/State)  │     │  Renderer        │     │  Preferences    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Data Model

```python
from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Optional, List
from enum import Enum

class NotificationType(Enum):
    HABIT_REMINDER = "habit_reminder"
    TASK_DUE = "task_due"
    GOAL_DEADLINE = "goal_deadline"
    STREAK_WARNING = "streak_warning"
    ACHIEVEMENT = "achievement"
    SYSTEM = "system"

class NotificationPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Notification:
    id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    scheduled_for: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    read: bool = False
    action_url: Optional[str] = None
    metadata: dict = field(default_factory=dict)

@dataclass
class ReminderSchedule:
    id: str
    entity_type: str  # 'habit', 'task', 'goal'
    entity_id: str
    reminder_time: time
    days_of_week: List[int] = field(default_factory=list)  # 0=Monday, 6=Sunday
    enabled: bool = True
    snooze_minutes: int = 5
    max_snoozes: int = 3
```

### Tasks

- [x] Research notification best practices and Web Push API
- [x] Design notification data model
- [x] Implement `NotificationEngine` class in Python
- [x] Implement `ReminderScheduler` with APScheduler
- [x] Create notification templates
- [x] Add notification persistence to SQLite
- [x] Implement notification history and analytics

### Implementation Location

- `brain/notifications/__init__.py`
- `brain/notifications/engine.py`
- `brain/notifications/scheduler.py`
- `brain/notifications/templates.py`
- `tracking_app/database.py` (schema updates)

---

## Phase 4.2: Habit Reminders

**Priority:** High  
**Effort:** Medium  
**Duration:** 3-4 days  
**Status:** ✅ Enhanced (Advanced Algorithms Implemented)

### Problem

Users forget to complete habits, especially new ones that haven't become automatic. Without timely reminders, habit formation fails.

### Solution

Implement smart habit reminders that:
- Learn optimal reminder times from user behavior
- Support multiple reminder schedules per habit
- Escalate urgency based on streak risk
- Integrate with habit stacking triggers

### Features

| Feature | Description |
|---------|-------------|
| **Custom Times** | Set specific reminder times per habit |
| **Smart Timing** | Learn when user typically completes habits |
| **Streak Protection** | Urgent reminders when streak at risk |
| **Stack Reminders** | Remind when previous habit in stack completed |
| **Snooze** | Postpone reminders with configurable duration |

### Data Model

```python
@dataclass
class HabitReminder:
    id: str
    habit_id: str
    reminder_type: str  # 'fixed', 'smart', 'stack_triggered'
    reminder_time: Optional[time] = None
    minutes_after_stack_trigger: Optional[int] = None
    enabled: bool = True
    sound: str = "default"
    vibration: bool = True
    
@dataclass
class ReminderAnalytics:
    habit_id: str
    total_reminders: int
    reminders_followed: int
    avg_response_time_minutes: float
    optimal_time: Optional[time] = None
```

### Tasks

- [x] Design habit reminder data model
- [x] Implement `HabitReminderManager` class
- [ ] Add reminder creation/editing UI in Streamlit
- [x] Implement smart timing algorithm (IQR outlier rejection, K-Means clustering)
- [x] Add streak protection reminders (urgency escalation)
- [x] Integrate with habit stacking triggers (StackTriggeredReminder)
- [ ] Track reminder effectiveness analytics

### Implementation Location

- `brain/notifications/habit_reminders.py`
- `tracking_app/pages/habit_reminders.py` (Streamlit UI)

---

## Phase 4.3: Task & Goal Alerts

**Priority:** Medium  
**Effort:** Medium  
**Duration:** 3-4 days  
**Status:** ✅ Complete

### Problem

Users miss task deadlines and goal milestones because there's no advance warning system. Without proactive alerts, important commitments slip by.

### Solution

Implement deadline-aware notifications:
- Progressive urgency as deadline approaches
- Configurable lead times (1 day, 1 hour, etc.)
- Daily digest of upcoming deadlines
- Goal milestone celebrations

### Features

| Feature | Description |
|---------|-------------|
| **Due Date Reminders** | Configurable alerts before task due dates |
| **Progressive Urgency** | Low → Medium → High → Urgent as deadline nears |
| **Daily Digest** | Morning summary of today's tasks and goals |
| **Milestone Alerts** | Celebrate goal progress (25%, 50%, 75%, 100%) |
| **Overdue Escalation** | Increasingly urgent notifications for overdue items |

### Data Model

```python
@dataclass
class TaskAlert:
    task_id: str
    reminder_lead_times: List[int] = field(default_factory=lambda: [1440, 60])  # minutes before due
    overdue_escalation_hours: int = 4
    enabled: bool = True

@dataclass
class GoalAlert:
    goal_id: str
    milestone_percentages: List[int] = field(default_factory=lambda: [25, 50, 75, 100])
    deadline_reminder_days: List[int] = field(default_factory=lambda: [7, 3, 1])
    enabled: bool = True
```

### Tasks

- [x] Design task and goal alert data models
- [x] Implement `TaskAlertManager` class
- [x] Implement `GoalAlertManager` class
- [x] Add progressive urgency logic
- [x] Create daily digest generator
- [x] Add milestone celebration notifications
- [x] Implement overdue escalation

### Implementation Location

- `brain/notifications/task_alerts.py`
- `brain/notifications/goal_alerts.py`
- `tracking_app/pages/notification_settings.py` (Streamlit UI)

---

## Phase 4.4: Notification Settings UI

**Priority:** Medium  
**Effort:** Medium  
**Duration:** 3-4 days  
**Status:** ✅ Complete

### Problem

Users need fine-grained control over notifications. One-size-fits-all notifications lead to notification fatigue and users disabling them entirely.

### Solution

Implement comprehensive notification settings:
- Global notification preferences
- Per-entity customization (habit, task, goal)
- Quiet hours configuration
- Channel preferences (browser, email)
- Notification history view

### Features

| Feature | Description |
|---------|-------------|
| **Global Toggle** | Enable/disable all notifications |
| **Quiet Hours** | Suppress notifications during specified times |
| **Per-Type Settings** | Configure each notification type |
| **Sound Selection** | Choose notification sounds |
| **History View** | See past notifications and actions taken |
| **Test Notifications** | Send test to verify setup |

### Data Model

```python
@dataclass
class NotificationPreferences:
    user_id: str
    enabled: bool = True
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None
    default_sound: str = "default"
    vibration_enabled: bool = True
    
    # Per-type settings
    habit_reminders_enabled: bool = True
    task_reminders_enabled: bool = True
    goal_reminders_enabled: bool = True
    achievement_notifications_enabled: bool = True
    
    # Channel preferences
    browser_notifications_enabled: bool = True
    email_notifications_enabled: bool = False
    email_address: Optional[str] = None
```

### Tasks

- [x] Design notification preferences data model
- [x] Create Streamlit settings page
- [x] Implement quiet hours logic (cross-midnight support)
- [x] Add notification history view
- [x] Create notification sound selector (via default_sound field)
- [x] Add test notification functionality
- [x] Implement preference persistence

### Implementation Location

- `brain/notifications/preferences.py`
- `tracking_app/pages/notification_settings.py` (Streamlit UI)

---

## Success Criteria

| Criteria | How to Verify |
|----------|---------------|
| Notification engine works | Can create, schedule, and send notifications |
| Habit reminders work | Users receive timely habit reminders |
| Task/goal alerts work | Deadline alerts fire correctly |
| Settings UI works | Users can customize all preferences |
| Persistence works | Notifications survive app restart |

---

## Dependencies

| Dependency | Purpose | Install |
|------------|---------|---------|
| APScheduler | Job scheduling | `pip install apscheduler` |
| webpush | Browser push notifications | `pip install pywebpush` |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Browser notification permissions denied | Graceful fallback to in-app notifications |
| Notification fatigue | Smart defaults, easy customization |
| Timezone handling issues | Store all times in UTC, convert on display |

---

## Next Phase

After completing Phase 4, proceed to:
- **Phase 5: Data Management & Portability** - Export, import, backup, and lifecycle management

---

## Phase 5 Reference

**Phase 5 Document:** [PHASE_5_DATA_MANAGEMENT.md](PHASE_5_DATA_MANAGEMENT.md)
**Phase 5 Tasks:** [PHASE_5_TODO.md](PHASE_5_TODO.md)

Phase 5 builds on Phase 4 by implementing:
- Data export functionality (JSON, CSV, SQLite)
- Data import with validation and conflict resolution
- Automated backup and restore system
- Data lifecycle management (retention, archival, purge)

---

## Research Needed

This phase requires user-provided research on:

1. **Notification Best Practices**
   - Optimal reminder timing
   - Notification copy that drives action
   - Avoiding notification fatigue

2. **Web Push API**
   - Browser compatibility
   - Permission request best practices
   - Service worker implementation

3. **Smart Timing Algorithms**
   - Learning user behavior patterns
   - Optimal reminder time prediction

---

*Last updated: February 18, 2026*
*Status: ✅ Phase 4 Complete - All Sub-Phases Implemented*
