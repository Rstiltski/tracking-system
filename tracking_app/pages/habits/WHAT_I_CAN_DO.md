# 🎯 What I Can Do - Habits Page

## Purpose
Track daily and weekly habits, build streaks, monitor your progress with scientific scoring, and develop consistent behaviors over time.

---

## ✅ User Interactions

### Actions I Can Perform

| Action | How | Result |
|--------|-----|--------|
| **Mark habit complete** | Click ✓ button on a habit | Habit marked done for today, +10 XP earned |
| **Undo completion** | Click ↩️ button on completed habit | Habit unmarked, XP deducted |
| **Add new habit** | Click "Add Habit" button in Spreadsheet Grid | Form opens to create new habit |
| **Edit habit** | Click ✏️ button on a habit | Edit modal opens with habit details |
| **Delete habit** | Click 🗑️ button, then confirm | Habit permanently removed |
| **Use streak freeze** | Click "❄️ Use Streak Freeze" when streak broken | Streak preserved, freeze count decreases |
| **Archive habit** | Via edit form | Habit moved to archive, hidden from active list |
| **Unarchive habit** | Click ↩️ in Archived tab | Habit restored to active list |

### Forms I Can Fill

**Add Habit Form:**
- **Name**: What the habit is called
- **Description**: Optional details about the habit
- **Icon**: Emoji icon for visual identification
- **Color**: Color code for the habit card
- **Frequency**: Daily or weekly tracking
- **Category**: Organization category
- **Target Value**: Numeric goal (optional)

**Edit Habit Form:**
- All fields from Add Habit Form
- **Archive Toggle**: Move to archive

### Buttons I Can Click

| Button | What It Does |
|--------|--------------|
| ✓ (Checkmark) | Mark habit as complete for today |
| ↩️ (Undo) | Unmark a completed habit |
| ✏️ (Edit) | Open edit form for this habit |
| 🗑️ (Delete) | Delete habit (requires confirmation) |
| ❄️ Use Streak Freeze | Preserve a broken streak |
| Add Habit | Open form to create new habit |

---

## 📊 Data Displayed

### Habit Information
- **Habit Name & Icon**: Visual identification
- **Description**: Habit details (if set)
- **Habit Score**: 0-100% using exponential smoothing algorithm
  - Categories: Excellent (80%+), Strong (60-79%), Developing (40-59%), Building (20-39%), Starting (0-19%)
- **Trend Indicator**: ⬆️ Improving, ⬇️ Declining, ➡️ Stable
- **Current Streak**: Consecutive days completed
- **30-Day Completion Rate**: Percentage over last 30 days

### Views Available

| Tab | What It Shows |
|-----|---------------|
| **Spreadsheet Grid** | Matrix view with dates, completions, scores |
| **Card View** | Individual habit cards with full details |
| **Habit Stacks** | Grouped habits for chaining |
| **Today's Progress** | Quick view of today's habits |
| **Archived** | Previously archived habits |

### Additional Components
- **Burnout Risk Indicator**: Warns when habit may be causing burnout
- **Difficulty Widget**: Rate how hard the habit was today
- **Timing Indicator**: Best time to perform habit
- **Tips Section**: Environment tips for habit success
- **Suggestions**: Smart suggestions for improvement
- **Automaticity Badge**: Shows habit formation progress (SRBAI survey)

---

## 🔗 Navigation

### Where I Can Go From Here
- **Habit Analytics** (`habit_analytics.py`) - Detailed insights for specific habits
- **Habit Reminders** (`habit_reminders.py`) - Set up reminders for habits
- **Habit Experiments** (`habit_experiments.py`) - Run experiments on habits
- **Stacks** (`stacks.py`) - Create habit stacks/chains
- **Dashboard** - Overview of all tracking

### Related Sidebar Links
- Main navigation to all tracking pages
- Streak freeze counter (shows available freezes)

---

## ⚡ Quick Tips

1. **Build Streaks**: Consistency builds habits - try not to break your streak!
2. **Use Freezes Wisely**: You have limited streak freezes - save them for emergencies
3. **Check Your Score**: The habit score is forgiving - one missed day won't ruin progress
4. **Sort & Filter**: Use the sorting options to find habits quickly
5. **Archive Instead of Delete**: Archive habits you want to pause without losing history
6. **Review Burnout Warnings**: If you see burnout warnings, consider reducing habit load

---

## 📋 Sorting & Filtering Options

| Option | Values |
|--------|--------|
| **Sort by** | Name, Score, Streak, Completion Rate |
| **Status** | All Habits, Active Only, Archived Only |
| **Order** | Ascending/Descending toggle |

---

## 🎮 Gamification

- **XP Earned**: +10 XP per habit completion
- **Level Up**: Earn enough XP to increase your level
- **Achievements**: Unlock achievements for habit milestones
- **Streak Milestones**: Achievements at 7, 30, 100 day streaks

---

**Related Files:** `habits.py`, `card_view.py`, `spreadsheet.py`, `add_form.py`, `edit_form.py`, `helpers.py`