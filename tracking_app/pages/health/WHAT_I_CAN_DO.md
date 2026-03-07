# 🎯 What I Can Do - Health Page

## Purpose
Track your physical well-being by logging weight, sleep hours, mood, and notes. View trends over time to understand your health patterns.

---

## ✅ User Interactions

### Actions I Can Perform

| Action | How | Result |
|--------|-----|--------|
| **Log health data** | Fill form, click "💾 Save Entry" | Today's health entry saved |
| **Update entry** | Modify form values, save again | Entry updated for today |
| **Clear entry** | Click "🗑️ Clear" | Reset today's entry |
| **View trends** | Scroll to charts | See 30-day trends |
| **View history** | Scroll to history | See past entries |

### Forms I Can Fill

**Health Log Form:**
- **Weight (kg)**: Your current weight (optional)
- **Sleep (hours)**: Hours of sleep last night (optional)
- **Mood**: How you're feeling today
- **Notes**: Optional notes about how you're feeling

### Buttons I Can Click

| Button | What It Does |
|--------|--------------|
| 💾 Save Entry | Save today's health data |
| 🗑️ Clear | Reset the form |

---

## 📊 Data Displayed

### Weekly Summary

| Metric | Description |
|--------|-------------|
| **Avg Weight** | Average weight over past 7 days |
| **Avg Sleep** | Average sleep hours over past 7 days |
| **Most Common Mood** | Mood you had most often this week |

### Trend Charts (30-day view)

| Tab | What It Shows |
|-----|---------------|
| **Weight** | Line chart of weight over time |
| **Sleep** | Line chart of sleep hours over time |
| **Mood** | Bar chart of mood ratings over time |

### Mood Scale

| Mood | Icon | Value |
|------|------|-------|
| Great | 😊 | 4 |
| Good | 🙂 | 3 |
| Okay | 😐 | 2 |
| Bad | 😔 | 1 |

### History
- **Date**: Entry date
- **Weight**: Weight in kg
- **Sleep**: Sleep hours
- **Mood**: Mood with icon
- **Notes**: Entry notes (truncated)

---

## 🔗 Navigation

### Where I Can Go From Here
- **Dashboard** - Overview including health summary
- **Emotional Health** (`emotional_health.py`) - Detailed emotional tracking
- **Calendar** (`calendar.py`) - View health entries on calendar
- **Insights** (`insights.py`) - Correlations with other metrics

---

## ⚡ Quick Tips

1. **Log Daily**: Consistent logging reveals patterns
2. **Use Notes**: Capture context for your mood/health
3. **Track Sleep**: Sleep affects everything - track it!
4. **Review Trends**: Check charts weekly to spot patterns
5. **Be Honest**: Accurate data leads to better insights

---

## 📈 Health Trends

The trend indicators show:
- ⬆️ **Improving**: Metric is trending upward
- ⬇️ **Declining**: Metric is trending downward
- ➡️ **Stable**: No significant change

---

## 📋 Entry Limits

- **History Display**: Shows last 10 entries
- **Chart Range**: Last 30 days
- **Summary Range**: Last 7 days

---

## 🎯 Mood Options

| Option | When to Use |
|--------|-------------|
| **😊 Great** | Excellent day, feeling wonderful |
| **🙂 Good** | Positive day, things going well |
| **😐 Okay** | Average day, nothing special |
| **😔 Bad** | Difficult day, feeling down |

---

**Related Files:** `health.py`, `components.py`, `helpers.py`, `constants.py`, `session_state.py`