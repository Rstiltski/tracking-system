# 🎯 What I Can Do - Task Alerts Page

## Purpose
Set up alerts for task deadlines. Get notified before tasks are due and when they become overdue.

---

## ✅ User Interactions

### Actions I Can Perform

| Action | How | Result |
|--------|-----|--------|
| **Create alert** | Click "Add Alert" | Alert setup form opens |
| **Edit alert** | Click edit on alert | Modify alert settings |
| **Delete alert** | Click delete on alert | Alert removed |
| **Toggle alert** | Click toggle switch | Enable/disable alert |

---

## 📊 Data Displayed

### Alert Settings
- **Task/Category**: Which tasks trigger alerts
- **Timing**: When to alert (before deadline)
- **Type**: Overdue, due soon, or both
- **Status**: Active/Inactive

### Alert Timing Options
- **1 hour before**: Alert 1 hour before deadline
- **1 day before**: Alert 24 hours before deadline
- **At deadline**: Alert when task is due
- **After overdue**: Alert when task is past due

---

## 🔗 Navigation

### Where I Can Go From Here
- **Tasks** (`tasks.py`) - Manage tasks
- **Notification Settings** (`notification_settings.py`) - Global settings

---

## ⚡ Quick Tips

1. **Set Buffer Time**: Alert before deadline, not at deadline
2. **Prioritize**: Only set alerts for important tasks
3. **Check Settings**: Ensure notifications are enabled

---

**Related Files:** `task_alerts.py`, `components.py`, `helpers.py`