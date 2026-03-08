# 📁 Phase 10: Granular Refactoring - Habits Field

**Last Updated:** March 8, 2026  
**Status:** Ready to Begin

---

## 🎯 Current Task

Phase 10 Granular Refactoring - Habits Field

---

## 📂 Habits Module - File Categories

Based on `tracking_app/pages/habits/` directory analysis:

### 1. **Core Module** (Foundation)
| File | Size | Purpose |
|------|------|---------|
| [`__init__.py`](tracking-system/tracking_app/pages/habits/__init__.py) | 2794 | Module initialization |
| [`constants.py`](tracking-system/tracking_app/pages/habits/constants.py) | 2313 | Habit constants & config |

### 2. **Forms (User Input)** ✏️
| File | Size | Purpose |
|------|------|---------|
| [`add_form.py`](tracking-system/tracking_app/pages/habits/add_form.py) | 5142 | Add new habit form |
| [`edit_form.py`](tracking-system/tracking_app/pages/habits/edit_form.py) | 3864 | Edit existing habit |

### 3. **Views (Display)** 👁️
| File | Size | Purpose |
|------|------|---------|
| [`card_view.py`](tracking-system/tracking_app/pages/habits/card_view.py) | 17524 | Card-based habit display |
| [`spreadsheet.py`](tracking-system/tracking_app/pages/habits/spreadsheet.py) | 9878 | Spreadsheet/grid view |
| [`progress_rings.py`](tracking-system/tracking_app/pages/habits/progress_rings.py) | 7820 | Progress ring visualizations |

### 4. **State & Helpers** ⚙️
| File | Size | Purpose |
|------|------|---------|
| [`helpers.py`](tracking-system/tracking_app/pages/habits/helpers.py) | 9863 | Utility functions |
| [`session_state.py`](tracking-system/tracking_app/pages/habits/session_state.py) | 3801 | Session state management |

### 5. **Navigation** 🧭
| File | Size | Purpose |
|------|------|---------|
| [`navigation.py`](tracking-system/tracking_app/pages/habits/navigation.py) | 5909 | Navigation logic |
| [`header.py`](tracking-system/tracking_app/pages/habits/header.py) | 330 | Page header |

### 6. **Documentation** 📚
| File | Purpose |
|------|---------|
| [`README.md`](tracking-system/tracking_app/pages/habits/README.md) | Module documentation |
| [`WHAT_I_CAN_DO.md`](tracking-system/tracking_app/pages/habits/WHAT_I_CAN_DO.md) | User capabilities |

---

## 🔄 Refactoring Workflow

For each file, follow this 4-step loop:

1. **AUDIT:** Scan for performance bottlenecks, N+1 queries, lack of caching, UI clutter
2. **PLAN:** Propose specific changes
3. **REFINE:** Generate optimized code block
4. **VERIFY:** Match CORE_RULES.md and SECURITY_PLAYBOOK.md

---

## ✅ To Do - Habits Field

- [x] Tasks (constants.py) ✅ REFACTORED
- [x] Goals (constants.py) ✅ REFACTORED
- [ ] Views (card_view.py, spreadsheet.py, progress_rings.py)
- [ ] State & Helpers (helpers.py, session_state.py)
- [ ] Navigation (navigation.py, header.py)

---

## ✅ Completed Refactoring - Multiple Fields

### Tasks Field
- Added `@st.cache_data` for priority lookup
- Added `get_priority_index_map()` and `get_priority_index()` functions
- Added type hints

### Goals Field
- Added `@st.cache_data` for icon lookup
- Added `get_goal_icon_index_map()` and `get_goal_icon_index()` functions

---

## ✅ Completed Refactoring

### constants.py
- Added `@st.cache_data` decorator for icon lookup
- Added `get_icon_index_map()` for O(1) dict lookup
- Added `get_icon_index()` helper function
- Added type hints

### edit_form.py
- Replaced O(n) `list.index()` with O(1) cached `get_icon_index()`
- Added import for new function

### add_form.py
- Added type hints import

### helpers.py
- Added `get_habits_batch_data()` - batch loading pattern for N+1 fix
- Added type hints (List import)

---

## 📋 Views Category - Next Steps

**Critical Issue:** card_view.py makes 4+ DB calls per habit card (N+1 problem)

**Solution in progress:**
1. Added batch loading pattern in helpers.py
2. Next: Update card_view.py to use batch loading

---

## � AUDIT COMPLETE: Forms Category (Score: 7/10)

### add_form.py Findings:
| Issue | Severity | Location | Fix |
|-------|----------|----------|-----|
| **Duplicate DB Query** | Medium | Line 28 & 89 | Cache in session_state |
| **No Caching on HABIT_ICONS** | Low | Line 10, 38, 99 | Add @st.cache_data |
| **Missing Type Hints** | Low | All functions | Add type hints |

### edit_form.py Findings:
| Issue | Severity | Location | Fix |
|-------|----------|----------|-----|
| **Duplicate DB Query** | Medium | Line 32 | Cache in session_state |
| **List.index() O(n)** | Low | Line 43 | Use dict lookup |
| **No Cache on HABIT_ICONS** | Low | Line 10, 44 | Add @st.cache_data |
| **Missing Type Hints** | Low | All functions | Add type hints |

---

## 🔍 AUDIT: Views Category (IN PROGRESS)

### card_view.py Findings (17524 bytes):
| Issue | Severity | Location | Impact |
|-------|----------|----------|--------|
| **N+1 Query Problem** | 🔴 HIGH | Lines 53-66 | 4+ DB calls per card = 40+ for 10 habits |
| **No Card Caching** | 🔴 HIGH | Entire function | Re-renders on every interaction |
| **BurnoutDetector in Loop** | 🟠 MEDIUM | Line 64-66 | New instance per card |
| **Inline Component Imports** | 🟠 MEDIUM | Line 64 | Late binding pattern |
| **Multiple Sub-components** | 🟠 MEDIUM | Lines 112,115,118 | Extra DB queries per card |

---

## 📋 Next Priority

**Views category has CRITICAL performance issues (N+1 queries).**

The card_view.py needs:
1. Batch data loading (get all data for cards in one query)
2. Add @st.cache_data for expensive computations
3. Move BurnoutDetector initialization outside the loop

---

## ❓ Selection Required

Which category should we start with?

1. **Forms** - User input validation & UX
2. **Views** - Visual performance optimization
3. **State & Helpers** - Logic optimization
4. **Navigation** - UX flow improvements
5. **Core Module** - Foundation refactoring
