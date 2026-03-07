# 🎯 What I Can Do - Tasks Page

## Purpose
Manage your todos and tasks with priorities, categories, and deadlines. Track completion and earn XP for finishing tasks.

---

## ✅ User Interactions

### Actions I Can Perform

| Action | How | Result |
|--------|-----|--------|
| **Add new task** | Fill form at top, click "Add Task" | Task created and added to list |
| **Mark task complete** | Click ✓ button on a task | Task marked done, XP earned based on priority |
| **Edit task** | Click ✏️ button on a task | Edit form opens with task details |
| **Delete task** | Click 🗑️ button on a task | Task permanently removed |
| **Filter tasks** | Use dropdown filters | List updates to show matching tasks |

### Forms I Can Fill

**Add Task Form:**
- **Task Title**: Name of the task (required)
- **Description**: Optional details about the task
- **Category**: Organization category (Work, Personal, Health, etc.)
- **Priority**: Low, Medium, High, or Urgent
- **Due Date**: When the task should be completed (optional)
- **Due Time**: Specific time deadline (optional)

**Edit Task Form:**
- All fields from Add Task Form
- Save Changes / Cancel buttons

### Buttons I Can Click

| Button | What It Does |
|--------|--------------|
| ✓ (Checkmark) | Mark task as complete |
| ✏️ (Edit) | Open edit form for this task |
| 🗑️ (Delete) | Delete task immediately |
| Add Task | Create new task |
| Save Changes | Save edited task details |
| Cancel | Close edit form without saving |

---

## 📊 Data Displayed

### Task Information
- **Task Title**: Name of the task
- **Description**: Task details (truncated if long)
- **Priority Icon**: Visual indicator (🔴 Urgent, 🟠 High, 🟡 Medium, 🟢 Low)
- **Due Date**: When task is due
  - **Overdue**: Red warning with date
  - **Today**: "Today" badge
  - **Future**: Formatted date
- **Category**: Folder icon with category name
- **Completion Status**: Strikethrough + ✅ for completed tasks

### Summary Stats
- **Total**: Number of tasks in current view
- **Completed**: Number of completed tasks
- **Overdue**: Number of overdue tasks (highlighted)

---

## 🔍 Filtering Options

| Filter | Options |
|--------|---------|
| **Status** | All, Active, Completed, Overdue |
| **Priority** | All Priorities, Low, Medium, High, Urgent |
| **Category** | All Categories, or specific category |

---

## 🔗 Navigation

### Where I Can Go From Here
- **Dashboard** - Overview with task summary
- **Task Alerts** (`task_alerts.py`) - Set up deadline notifications
- **Calendar** (`calendar.py`) - View tasks on calendar
- **Weekly Review** (`weekly_review.py`) - Review task completion

---

## ⚡ Quick Tips

1. **Set Priorities**: Higher priority tasks give more XP when completed
2. **Use Due Dates**: Helps track overdue tasks and plan your day
3. **Categorize**: Organize tasks by area of life for easier filtering
4. **Check Overdue**: Filter by "Overdue" to catch missed deadlines
5. **Add Details**: Use descriptions to capture important context

---

## 🎮 Gamification

### XP Rewards by Priority

| Priority | XP Earned |
|----------|-----------|
| Low | +5 XP |
| Medium | +10 XP |
| High | +15 XP |
| Urgent | +20 XP |

- **Level Up**: Earn enough XP to increase your level
- **Achievements**: Unlock achievements for task milestones

---

## 📋 Priority Levels

| Priority | Icon | Meaning |
|----------|------|---------|
| **Urgent** | 🔴 | Must do today |
| **High** | 🟠 | Important, do soon |
| **Medium** | 🟡 | Normal priority |
| **Low** | 🟢 | Can wait, nice to have |

---

## 📁 Categories Available

- Work
- Personal
- Health
- Finance
- Learning
- Home
- Other

---

**Related Files:** `tasks.py`, `components.py`, `helpers.py`, `constants.py`, `session_state.py`