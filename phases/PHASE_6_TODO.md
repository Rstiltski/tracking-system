# 🧩 Phase 6: UI-Backend Integration - Chunked Todo

**Purpose:** Break down Phase 6 implementation into manageable 1-3 task chunks with detailed explanations.

**Total Sub-Phases:** 5 remaining (6.3-6.7)
**Current Focus:** Phase 6.3 - Habits Page - Habit Score UI

---

## 📈 Progress Tracking

**Phase:** 6 - UI-Backend Integration
**Overall Progress:** 4/7 sub-phases complete (57%)
**Current Focus:** Phase 6.5 (Intelligence Dashboard)
**Last Updated:** February 26, 2026

---

## ✅ Completed Sub-Phases

### Sub-Phase 6.1: Shared UI Components ✅
**Status:** `[x] Complete`
**Duration:** 1 day

- [x] Create `tracking_app/components/__init__.py`
- [x] Create `tracking_app/components/session.py`
- [x] Create `tracking_app/components/sidebar.py`
- [x] Create `tracking_app/components/metrics.py`
- [x] Create `tracking_app/components/charts.py`

### Sub-Phase 6.2: Dashboard Enhancement ✅
**Status:** `[x] Complete`
**Duration:** 1 day

- [x] Update `tracking_app/pages/dashboard.py` with habit scores
- [x] Add burnout risk indicator
- [x] Add activity feed
- [x] Add quick actions

---

### Sub-Phase 6.3: Habits Page - Habit Score UI ✅
**Status:** `[x] Complete`
**Duration:** 1 day

- [x] Import brain modules for habit scoring (`HabitScore`, `ScoreList`, `Frequency`, `EntryList`)
- [x] Create `calculate_habit_score()` function with exponential smoothing
- [x] Create `get_score_category()` helper for badge display
- [x] Create `get_trend_indicator()` helper for trend display
- [x] Update `render_habit_card()` to display score with category badge and trend
- [x] Display streak and 30-day completion rate alongside score

---

### Sub-Phase 6.4: Streak Freeze UI ✅
**Status:** `[x] Complete`
**Duration:** 1 day

- [x] Import `StreakFreeze`, `UserInventory` from `brain/models/streak.py`
- [x] Add session state for streak freeze inventory
- [x] Create `load_streak_freeze()` and `save_streak_freeze()` functions
- [x] Display streak freeze inventory in sidebar with progress bar
- [x] Implement purchase freeze button (100 XP cost)
- [x] Create `check_streak_break_yesterday()` helper function
- [x] Create `use_streak_freeze_for_habit()` function
- [x] Add "Use Streak Freeze" button for broken streaks
- [x] Show warning when streak was broken yesterday

---

## 🔄 Current Sub-Phase: 6.5 - Intelligence Dashboard
v
## 📋 Remaining Sub-Phases

### Sub-Phase 6.5: Intelligence Dashboard Page

**Status:** `[ ] Planning`
**Priority:** Medium
**Effort:** Medium

#### Chunk 1: Page Structure
- [ ] Create `tracking_app/pages/insights.py`
- [ ] Add navigation link to sidebar

#### Chunk 2: Correlation Display
- [ ] Implement correlation visualization
- [ ] Add natural language insights

#### Chunk 3: Burnout & PCS
- [ ] Add burnout risk dashboard
- [ ] Display PCS fragility scores

---

### Sub-Phase 6.6: Habit Stacking UI

**Status:** `[ ] Planning`
**Priority:** Medium
**Effort:** Medium

#### Chunk 1: Stack Creation
- [ ] Create stack creation interface
- [ ] Set anchor habits

#### Chunk 2: Stack Tracking
- [ ] Track stack completion
- [ ] Display stack progress

---

### Sub-Phase 6.7: Variable Rewards UI

**Status:** `[ ] Planning`
**Priority:** Low
**Effort:** Low

#### Chunk 1: Reward Display
- [ ] Add reward roll animation on completion
- [ ] Display rarity badges

#### Chunk 2: Inventory
- [ ] Display reward inventory
- [ ] Track collected rewards

---

## 🎯 Implementation Notes

### For AI Assistants

1. **Start with Chunk 1** of Phase 6.3 - it's the highest priority
2. **Use existing components** from `tracking_app/components/metrics.py`
3. **Follow the pattern** established in `tracking_app/pages/dashboard.py`
4. **Test after each task** to ensure functionality works

### Key Files to Reference

| File | Purpose |
|------|---------|
| `brain/models/habit.py` | HabitScore algorithm |
| `tracking_app/components/metrics.py` | Score display components |
| `tracking_app/pages/dashboard.py` | Example of score integration |
| `tracking_app/pages/habits.py` | File to modify |

### Backend Models Available

```python
# Scoring
from brain.models.habit import HabitScore, ScoreList, Habit
from brain.models.frequency import Frequency
from brain.models.entry import EntryList, Entry

# Streak Freeze
from brain.models.streak import StreakFreeze, UserInventory

# Analysis
from brain.analysis.correlation import CorrelationEngine
from brain.analysis.burnout import BurnoutPredictor
from brain.analysis.prediction import PCSEngine

# Behavioral
from brain.behavioral.habit_stacking import HabitStackingEngine
from brain.behavioral.rewards import RewardEngine
```

---

## 📊 Chunk Completion Log

| Date | Chunk | Tasks Completed | Notes |
|------|-------|-----------------|-------|
| Feb 26 | 6.1 Setup | 5 tasks | Components created |
| Feb 26 | 6.2 Dashboard | 4 tasks | Dashboard updated |
| Feb 26 | 6.3 Score UI | 6 tasks | Habit score integration complete |
| Feb 26 | 6.4 Streak Freeze | 9 tasks | Full streak freeze UI implemented |

---

*Last updated: February 26, 2026*
*Following CHUNKED_TODO_GUIDELINES.md*
