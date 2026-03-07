# 🎯 What I Can Do - Dashboard Page

## Purpose
Your central hub for viewing all tracking metrics at a glance. Get an overview of habits, tasks, goals, and progress with quick access to key actions.

---

## ✅ User Interactions

### Actions I Can Perform

| Action | How | Result |
|--------|-----|--------|
| **View overview** | Open dashboard | See all metrics at a glance |
| **Quick add habit** | Use quick actions | Jump to habits page to add |
| **Quick add task** | Use quick actions | Jump to tasks page to add |
| **Complete habit** | Click on today's habits | Mark habit complete |
| **Complete task** | Click on active tasks | Mark task complete |
| **View details** | Click section headers | Navigate to detailed pages |

### Quick Actions Available
- Add new habit
- Add new task
- Set new goal
- View all habits
- View all tasks

---

## 📊 Data Displayed

### Welcome Section
- **Greeting**: Personalized greeting based on time of day
- **Current date**: Today's date
- **User level/XP**: Current gamification status

### Quick Stats
| Metric | Description |
|--------|-------------|
| **Today's Habits** | Completed / Total habits for today |
| **Active Tasks** | Tasks not yet completed |
| **Goals Progress** | Overall goal completion percentage |
| **Current Streak** | Best current habit streak |

### Habit Scores Section
- **Score Overview**: All habit scores displayed
- **Trend Indicators**: Improving/Declining trends
- **Score Categories**: Excellent, Strong, Developing, Building, Starting

### Today's Habits
- List of habits for today
- Completion status (✓ or ⬜)
- Quick complete button

### Active Tasks
- Tasks not yet completed
- Priority indicators
- Due date information
- Quick complete button

### Goals Progress
- Active goals summary
- Progress bars for each goal
- Days remaining indicators

### Weekly Chart
- Visual representation of habit completions
- 7-day trend line
- Completion rate percentage

### Wellbeing Indicators
- **Burnout Risk**: Warning if system detects potential burnout
- **Activity Feed**: Recent actions and achievements

### Motivational Quote
- Daily motivational quote
- Refresh for new quote

---

## 🔗 Navigation

### Quick Navigation Links
| Section | Navigates To |
|---------|--------------|
| Habits section | Habits page (`habits.py`) |
| Tasks section | Tasks page (`tasks.py`) |
| Goals section | Goals page (`goals.py`) |
| Charts | Insights page (`insights.py`) |

### Sidebar Navigation
- Dashboard (current)
- Habits
- Tasks
- Goals
- Health
- Finances
- Time
- Calendar
- Achievements
- And more...

---

## ⚡ Quick Tips

1. **Start Here**: Dashboard is the best landing page to see everything at once
2. **Quick Actions**: Use quick action buttons to jump directly to adding items
3. **Monitor Burnout**: Check the burnout indicator regularly
4. **Daily Review**: Make dashboard part of your daily routine
5. **Check Streaks**: Keep an eye on your current streaks for motivation

---

## 📈 Dashboard Sections

| Section | What It Shows |
|---------|---------------|
| **Welcome** | Greeting, date, level/XP |
| **Quick Stats** | 4 key metrics at a glance |
| **Habit Scores** | Scientific habit scores with trends |
| **Quick Actions** | Buttons to add items quickly |
| **Today's Habits** | Habits for today with quick complete |
| **Active Tasks** | Pending tasks with priority |
| **Goals Progress** | Active goals with progress bars |
| **Weekly Chart** | 7-day completion visualization |
| **Burnout Risk** | Wellbeing warning indicator |
| **Activity Feed** | Recent actions and achievements |
| **Motivational Quote** | Daily inspiration |

---

## 🎮 Gamification Display

- **Current Level**: Your user level
- **Total XP**: Experience points earned
- **Progress to Next Level**: XP progress bar
- **Recent Achievements**: Latest unlocked achievements

---

## 📱 Layout

The dashboard uses a responsive layout:
- **Full width**: Welcome, Quick Stats, Quick Actions
- **Two columns**: Habits/Tasks, Goals/Charts
- **Full width**: Burnout, Activity Feed, Quote

---

**Related Files:** `dashboard.py`, `components.py`, `helpers.py`, `session_state.py`