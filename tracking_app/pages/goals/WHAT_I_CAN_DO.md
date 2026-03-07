# 🎯 What I Can Do - Goals Page

## Purpose
Set personal goals, track your progress toward targets, and celebrate achievements when you reach milestones.

---

## ✅ User Interactions

### Actions I Can Perform

| Action | How | Result |
|--------|-----|--------|
| **Add new goal** | Fill form at top, click "Add Goal" | Goal created and added to list |
| **Update progress** | Enter new value, click "📝 Update" | Progress saved, percentage recalculated |
| **Complete goal** | Update progress to reach target | Goal marked complete, +50 XP earned |
| **Edit goal** | Click "✏️ Edit" button | Edit form opens with goal details |
| **Delete goal** | Click 🗑️ button | Goal permanently removed |

### Forms I Can Fill

**Add Goal Form:**
- **Goal Title**: Name of the goal (required)
- **Description**: Why this goal is important (optional)
- **Icon**: Visual icon for the goal (🎯, 💪, 📚, 💰, etc.)
- **Target Value**: Numeric target to reach
- **Unit**: Unit of measurement (books, kg, hours, $, etc.)
- **Deadline**: Optional deadline date

**Edit Goal Form:**
- All fields from Add Goal Form
- Save Changes / Cancel buttons

### Buttons I Can Click

| Button | What It Does |
|--------|--------------|
| 📝 Update | Save new progress value |
| ✏️ Edit | Open edit form for this goal |
| 🗑️ (Delete) | Delete goal immediately |
| Add Goal | Create new goal |
| Save Changes | Save edited goal details |
| Cancel | Close edit form without saving |

---

## 📊 Data Displayed

### Goal Information
- **Goal Title**: Name of the goal
- **Description**: Why this goal matters
- **Icon**: Visual representation
- **Progress Circle**: Visual progress indicator (color-coded)
- **Progress Bar**: Percentage complete
- **Current/Target**: Numeric progress display (e.g., "25 / 50 books")
- **Status**: Days remaining, overdue, or completed

### Summary Stats
- **Active Goals**: Goals in progress
- **Completed**: Goals achieved
- **Overdue**: Goals past deadline (highlighted)

### Views Available

| Tab | What It Shows |
|-----|---------------|
| **Active** | Goals currently in progress |
| **Completed** | Goals that have been achieved |
| **All** | All goals regardless of status |

---

## 🔗 Navigation

### Where I Can Go From Here
- **Dashboard** - Overview with goal summary
- **Goal Alerts** (`goal_alerts.py`) - Set up deadline notifications
- **Calendar** (`calendar.py`) - View goal deadlines
- **Achievements** (`achievements.py`) - See goal-related achievements

---

## ⚡ Quick Tips

1. **Set Realistic Targets**: Break big goals into smaller milestones
2. **Use Deadlines**: Deadlines create urgency and help with planning
3. **Update Regularly**: Keep progress current for accurate tracking
4. **Celebrate Wins**: Completing goals earns significant XP!
5. **Review Periodically**: Check overdue goals and adjust as needed

---

## 🎮 Gamification

### XP Rewards
- **Goal Completed**: +50 XP

- **Level Up**: Earn enough XP to increase your level
- **Achievements**: Unlock achievements for goal milestones

---

## 📈 Progress Status Indicators

| Status | Meaning |
|--------|---------|
| **On Track** | Making good progress toward deadline |
| **Behind** | Progress is lagging for deadline |
| **Overdue** | Past deadline but not yet complete |
| **Completed** | Goal achieved! 🎉 |

---

## 🎨 Goal Icons Available

| Icon | Common Use |
|------|------------|
| 🎯 | General goals |
| 💪 | Fitness/Health |
| 📚 | Learning/Reading |
| 💰 | Financial |
| 🏃 | Exercise |
| 💼 | Career/Work |
| 🏠 | Home/Personal |
| ✈️ | Travel |

---

**Related Files:** `goals.py`, `components.py`, `helpers.py`, `constants.py`, `session_state.py`