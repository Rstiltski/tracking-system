# Phase 6: UI-Backend Integration

**Duration:** 3-4 weeks
**Status:** 🔄 In Progress (~25% Complete)
**Dependencies:** Phases 1-5 Complete
**Created:** February 26, 2026

---

## Overview

Phase 6 bridges the gap between the fully implemented backend systems (Phases 1-5) and the Streamlit UI. The backend features for habit scoring, correlation analysis, burnout prediction, and behavioral science techniques are implemented but NOT fully connected to the user interface.

**Goal:** Expose all backend capabilities through the Streamlit UI.

**Implementation Language:** Python 3.10+
**Key Libraries:** Streamlit, brain modules

---

## Phase Status Summary

| Sub-Phase | Feature | Status | Completion |
|-----------|---------|--------|------------|
| **6.1** | Shared UI Components | ✅ Complete | 100% |
| **6.2** | Dashboard Enhancement | ✅ Complete | 100% |
| **6.3** | Habits Page - Habit Score UI | 📋 Planned | 0% |
| **6.4** | Habits Page - Streak Freeze UI | 📋 Planned | 0% |
| **6.5** | Intelligence Dashboard Page | 📋 Planned | 0% |
| **6.6** | Habit Stacking UI | 📋 Planned | 0% |
| **6.7** | Variable Rewards UI | 📋 Planned | 0% |

---

## Sub-Phase 6.1: Shared UI Components ✅ COMPLETE

**Status:** ✅ **COMPLETE**
**Duration:** 1 day

### Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `tracking_app/components/__init__.py` | Module exports | ~40 |
| `tracking_app/components/session.py` | Session state management | ~130 |
| `tracking_app/components/sidebar.py` | Unified navigation | ~110 |
| `tracking_app/components/metrics.py` | Metric cards and displays | ~200 |
| `tracking_app/components/charts.py` | Chart components | ~130 |

**Total:** ~610 lines of Python code

### Features Implemented

- ✅ Unified session state management
- ✅ Consistent sidebar navigation across all pages
- ✅ Habit score card component with category badges
- ✅ Streak card component
- ✅ Burnout risk card component
- ✅ Progress card component
- ✅ Weekly chart component
- ✅ Score trend chart component

---

## Sub-Phase 6.2: Dashboard Enhancement ✅ COMPLETE

**Status:** ✅ **COMPLETE**
**Duration:** 1 day

### Files Modified

| File | Changes |
|------|---------|
| `tracking_app/pages/dashboard.py` | Complete rewrite with backend integration |

### Features Implemented

- ✅ Real habit scores using `brain/models/habit.py` algorithm
- ✅ Burnout risk indicator using `brain/analysis/burnout.py`
- ✅ Activity feed with recent completions
- ✅ Wellbeing check section
- ✅ Quick actions with 4 buttons
- ✅ XP progress bar in sidebar
- ✅ Connection to storage for all metrics

---

## Sub-Phase 6.3: Habits Page - Habit Score UI 📋 PLANNED

**Status:** 📋 **PLANNED**
**Priority:** High
**Effort:** Low-Medium
**Duration:** 1-2 days

### Problem

The habits page currently shows a basic streak counter and 30-day completion rate, but does not utilize the sophisticated habit scoring algorithm implemented in `brain/models/habit.py`. Users cannot see:

- Their habit score (0-100%)
- Score category (Excellent, Strong, Developing, Building, Starting)
- Trend indicators (improving, declining, stable)
- Score history over time

### Solution

Integrate the `HabitScore` and `ScoreList` classes from `brain/models/habit.py` into the habits page UI:

1. **Score Display** - Show score percentage for each habit
2. **Category Badges** - Visual indicators for score category
3. **Trend Indicators** - Show if habit is improving/declining
4. **Score History Chart** - Track score over time

### Backend Connection

```python
from brain.models.habit import HabitScore, ScoreList
from brain.models.frequency import Frequency
from brain.models.entry import EntryList
```

### Implementation Tasks

**Chunk 1: Basic Score Display (1-2 tasks)**
- [ ] Add habit score calculation to habits page
- [ ] Display score percentage with category badge

**Chunk 2: Enhanced Score Features (1-2 tasks)**
- [ ] Add trend indicator to each habit card
- [ ] Create score history chart component

### Files to Modify

| File | Changes |
|------|---------|
| `tracking_app/pages/habits.py` | Add score integration |
| `tracking_app/components/charts.py` | Add score history chart (if needed) |

---

## Sub-Phase 6.4: Habits Page - Streak Freeze UI 📋 PLANNED

**Status:** 📋 **PLANNED**
**Priority:** High
**Effort:** Low-Medium
**Duration:** 1-2 days

### Problem

The backend has a complete streak freeze system (`brain/models/streak.py`) but users cannot:
- See their streak freeze inventory
- Purchase streak freezes with XP
- Use streak freezes to preserve streaks

### Solution

Add streak freeze UI to the habits page:

1. **Inventory Display** - Show available streak freezes
2. **Purchase Button** - Buy freezes for 100 XP
3. **Use Freeze** - Apply freeze to broken streaks
4. **Freeze History** - Track freeze usage

### Backend Connection

```python
from brain.models.streak import StreakFreeze, UserInventory
```

### Implementation Tasks

**Chunk 1: Basic Freeze Display (1-2 tasks)**
- [ ] Display streak freeze inventory count
- [ ] Add freeze indicator to streak cards

**Chunk 2: Freeze Actions (1-2 tasks)**
- [ ] Implement purchase freeze button
- [ ] Implement use freeze functionality

---

## Sub-Phase 6.5: Intelligence Dashboard Page 📋 PLANNED

**Status:** 📋 **PLANNED**
**Priority:** Medium
**Effort:** Medium
**Duration:** 2-3 days

### Problem

The backend has powerful analysis capabilities that are not exposed to users:
- Correlation engine (`brain/analysis/correlation.py`)
- Predictive Context Sensitivity (`brain/analysis/prediction.py`)
- Burnout prediction (`brain/analysis/burnout.py`)

### Solution

Create a new Intelligence/Insights page:

1. **Correlation Visualization** - Show relationships between habits/health
2. **PCS Fragility Scores** - Display habit predictability
3. **Burnout Risk Dashboard** - Risk assessment with recommendations

### Backend Connections

```python
from brain.analysis.correlation import CorrelationEngine
from brain.analysis.prediction import PCSEngine
from brain.analysis.burnout import BurnoutPredictor
```

### Implementation Tasks

**Chunk 1: Page Structure (1-2 tasks)**
- [ ] Create `tracking_app/pages/insights.py`
- [ ] Add navigation link to sidebar

**Chunk 2: Correlation Display (1-2 tasks)**
- [ ] Implement correlation visualization
- [ ] Add natural language insights

**Chunk 3: Burnout & PCS (1-2 tasks)**
- [ ] Add burnout risk dashboard
- [ ] Display PCS fragility scores

---

## Sub-Phase 6.6: Habit Stacking UI 📋 PLANNED

**Status:** 📋 **PLANNED**
**Priority:** Medium
**Effort:** Medium
**Duration:** 2-3 days

### Problem

The backend has a complete habit stacking system (`brain/behavioral/habit_stacking.py`) but there's no UI for users to:
- Create habit stacks
- Set anchor habits
- Track stack completion

### Solution

Add habit stacking UI:

1. **Stack Creation** - Interface to create stacks
2. **Anchor Display** - Show anchor habits
3. **Stack Tracking** - Track completion of stacks

### Backend Connection

```python
from brain.behavioral.habit_stacking import HabitStackingEngine
```

---

## Sub-Phase 6.7: Variable Rewards UI 📋 PLANNED

**Status:** 📋 **PLANNED**
**Priority:** Low
**Effort:** Low
**Duration:** 1-2 days

### Problem

The backend has a variable reward system (`brain/behavioral/rewards.py`) but users don't experience:
- Random loot drops on completion
- Rarity badges
- Reward inventory

### Solution

Add variable rewards to habit completion:

1. **Reward Roll** - Random reward animation on completion
2. **Rarity Display** - Show rarity badges
3. **Inventory** - Display collected rewards

### Backend Connection

```python
from brain.behavioral.rewards import RewardEngine
```

---

## Architecture

### Component Structure

```
tracking_app/
├── components/
│   ├── __init__.py         # Exports
│   ├── session.py          # State management
│   ├── sidebar.py          # Navigation
│   ├── metrics.py          # Display cards
│   └── charts.py           # Visualizations
│
├── pages/
│   ├── dashboard.py        # ✅ Updated
│   ├── habits.py           # 📋 To update (Phase 6.3)
│   ├── insights.py         # 📋 To create (Phase 6.5)
│   └── ... (other pages)
│
└── storage.py              # Data layer
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI                              │
│  (dashboard.py, habits.py, insights.py, components/)        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                   Storage Layer                              │
│  (tracking_app/storage.py)                                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
┌───────────┐ ┌───────────┐ ┌───────────────┐
│   Brain   │ │  Brain    │ │    Brain      │
│  Models   │ │ Analysis  │ │  Behavioral   │
├───────────┤ ├───────────┤ ├───────────────┤
│ HabitScore│ │Correlation│ │HabitStacking  │
│ Streak    │ │PCS        │ │Rewards        │
│ Entry     │ │Burnout    │ │Accountability │
└───────────┘ └───────────┘ └───────────────┘
```

---

## Success Criteria

| Criteria | Measurement | Status |
|----------|-------------|--------|
| Shared components work | All pages use components | ✅ Complete |
| Dashboard shows real scores | Habit scores displayed | ✅ Complete |
| Dashboard shows burnout risk | Risk indicator shown | ✅ Complete |
| Habits page shows scores | Per-habit score cards | 📋 Pending |
| Streak freezes work | Can earn/use freezes | 📋 Pending |
| Insights page exists | Correlation/PCS shown | 📋 Pending |
| Test coverage | >80% for components | 📋 Pending |

---

## Dependencies

| Dependency | Purpose | Module |
|------------|---------|--------|
| **Streamlit** | UI framework | `streamlit` |
| **brain.models.habit** | Habit scoring | `HabitScore`, `ScoreList` |
| **brain.models.streak** | Streak freezes | `StreakFreeze`, `UserInventory` |
| **brain.analysis.correlation** | Correlations | `CorrelationEngine` |
| **brain.analysis.burnout** | Burnout prediction | `BurnoutPredictor` |
| **brain.behavioral.rewards** | Variable rewards | `RewardEngine` |

---

## Testing Strategy

### Unit Tests
- Component rendering tests
- Score calculation tests
- UI interaction tests

### Integration Tests
- Full page workflows
- Backend integration tests
- Cross-page consistency

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [PHASE_5_DATA_MANAGEMENT.md](PHASE_5_DATA_MANAGEMENT.md) | Previous phase |
| [TODO.md](../TODO.md) | Task tracking |
| [brain/models/habit.py](../brain/models/habit.py) | Habit score algorithm |
| [brain/analysis/burnout.py](../brain/analysis/burnout.py) | Burnout prediction |

---

*Last updated: February 26, 2026*
*Status: 🔄 In Progress - 25% Complete*