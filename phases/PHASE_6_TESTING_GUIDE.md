# Phase 6.3 & 6.4 - Testing Guide

**Purpose:** Step-by-step instructions to test the new habit score and streak freeze features.

---

## 🚀 Quick Start

### 1. Start the Application

```bash
cd "/home/ramplestiltski/Documents/a_tracking>system/project tracking system/tracking-system"
streamlit run tracking_app/app.py
```

Or run the habits page directly:
```bash
streamlit run tracking_app/pages/habits.py
```

---

## 📊 Feature 1: Habit Score Testing

### What It Does
- Displays habit score (0-100%) using exponential smoothing algorithm
- Shows score category with emoji and color
- Indicates trend (improving ↑, declining ↓, or stable →)

### Step-by-Step Test

#### Step 1: Create a New Habit
1. Open the Habits page
2. Fill in the "Add New Habit" form:
   - **Name:** "Morning Exercise"
   - **Description:** "30 min workout"
   - **Icon:** 🏃 (or any you prefer)
   - **Color:** Green
   - **Frequency:** daily
3. Click "Add Habit"

#### Step 2: Check Initial Score
1. Look at the habit card you just created
2. **Expected:** Score shows "🆕 0%" with "Starting" label
3. **Trend:** Should show "→ stable"

#### Step 3: Complete the Habit Multiple Days
1. Click "✓" to mark the habit complete for today
2. **Expected:** See "+10 XP!" message
3. The score should remain low (0%) initially since it's only 1 day

#### Step 4: Simulate Multiple Days of Completion
To properly test the score algorithm, you need multiple days of data:

**Option A - Manual Testing Over Time:**
- Complete the habit daily for 7+ days
- Watch the score gradually increase
- After ~66 consecutive days, score should reach ~97%

**Option B - Quick Test with Existing Data:**
If you have habits with existing completion history:
1. Navigate to Habits page
2. Look at the score display on habit cards
3. Verify score category matches the percentage:
   - 🌟 Excellent: 85-100%
   - 💪 Strong: 70-84%
   - 🌱 Developing: 50-69%
   - 🔧 Building: 30-49%
   - 🆕 Starting: 0-29%

#### Step 5: Verify Score Components
On each habit card, verify you see:
- ✅ Score percentage (e.g., "75%")
- ✅ Category emoji (🌟💪🌱🔧🆕)
- ✅ Trend arrow (↑↓→) with color
- ✅ Category label (Excellent/Strong/etc.)
- ✅ Trend label (improving/declining/stable)
- ✅ Streak count
- ✅ 30-day completion rate

---

## ❄️ Feature 2: Streak Freeze Testing

### What It Does
- Shows streak freeze inventory in sidebar
- Allows purchasing freezes for 100 XP
- Detects broken streaks from yesterday
- Provides button to use freeze and preserve streak

### Step-by-Step Test

#### Step 1: Check Initial Streak Freeze Inventory
1. Look at the sidebar
2. Find "❄️ Streak Freezes" section
3. **Expected:** Shows "1/10 available" (you start with 1 free freeze)
4. Progress bar should be at 10%

#### Step 2: Test Purchasing a Streak Freeze
1. Check your current XP in the sidebar
2. If you have less than 100 XP, complete some habits first
3. Click "🛒 Buy Freeze (100 XP)" button
4. **Expected Results:**
   - Success: "❄️ Streak Freeze purchased!" message
   - Inventory increases to 2/10
   - XP decreases by 100
   - Page refreshes

5. **If XP < 100:**
   - Expected: Error message "Not enough XP! Need 100 XP."

#### Step 3: Test Maximum Freezes
1. Purchase freezes until you reach 10/10
2. **Expected:** Button changes to "✅ Max freezes reached!"
3. No more purchase button should appear

#### Step 4: Test Broken Streak Detection

**Prerequisites:** You need a habit with:
- At least 1 day completed before yesterday
- Yesterday NOT completed

**Manual Test:**
1. Create a habit today
2. Complete it today
3. Tomorrow (or simulate by changing date):
   - Don't complete the habit
4. On the third day:
   - Check if warning appears: "⚠️ Streak broken yesterday! Use a freeze to save it."

**Quick Test (if you have existing data):**
1. Find a habit where you missed yesterday but had a streak before
2. Look for the warning message under the habit name
3. Look for "❄️ Use Streak Freeze" button

#### Step 5: Test Using a Streak Freeze
1. Find a habit with a broken streak (warning shown)
2. Verify you have at least 1 freeze available
3. Click "❄️ Use Streak Freeze (X available)" button
4. **Expected Results:**
   - Success: "❄️ Streak frozen! Your streak is preserved."
   - Freeze count decreases by 1
   - Warning disappears
   - Streak count is preserved

---

## 🧪 Integration Tests

### Test 1: Score Updates After Completion
1. Create a new habit
2. Note the initial score (should be 0%)
3. Complete the habit for today
4. The score calculation uses 90-day lookback, so one day won't change much
5. Complete multiple days and watch score trend improve

### Test 2: XP and Freeze Purchase Flow
1. Note your current XP
2. Purchase a freeze (costs 100 XP)
3. Verify XP decreased by 100
4. Verify freeze count increased by 1

### Test 3: Freeze Usage Flow
1. Have a habit with broken streak
2. Click "Use Streak Freeze"
3. Verify:
   - Freeze count decreased
   - Streak preserved
   - Warning gone

---

## 📋 Test Checklist

### Habit Score Tests
- [ ] Can create new habit
- [ ] Score displays with percentage
- [ ] Score category emoji appears
- [ ] Score category label shows (Excellent/Strong/etc.)
- [ ] Trend indicator shows (↑↓→)
- [ ] Trend label shows (improving/declining/stable)
- [ ] Streak count displays correctly
- [ ] 30-day completion rate shows

### Streak Freeze Tests
- [ ] Freeze inventory shows in sidebar
- [ ] Progress bar displays correctly
- [ ] Can purchase freeze (if XP >= 100)
- [ ] Error shows if not enough XP
- [ ] Max freeze message when at 10/10
- [ ] Broken streak warning appears
- [ ] "Use Freeze" button appears for broken streaks
- [ ] Using freeze decreases inventory
- [ ] Using freeze preserves streak

---

## 🐛 Troubleshooting

### Issue: Score always shows 0%
**Cause:** No historical data for the habit
**Solution:** Complete the habit for multiple days to build score history

### Issue: "Buy Freeze" button doesn't work
**Cause:** Not enough XP
**Solution:** Complete habits to earn XP (10 XP per completion)

### Issue: "Use Freeze" button doesn't appear
**Cause:** No broken streak detected
**Solution:** You need:
- A habit completed at least 1 day before yesterday
- Yesterday NOT completed

### Issue: Import errors when running
**Cause:** Missing brain modules
**Solution:** Verify these files exist:
- `brain/models/habit.py`
- `brain/models/streak.py`
- `brain/models/frequency.py`
- `brain/models/entry.py`

---

## 📸 Expected Screenshots

### Sidebar - Streak Freeze Section
```
❄️ Streak Freezes
[████░░░░░░] 1/10 available
[🛒 Buy Freeze (100 XP)]
```

### Habit Card with Score
```
[🎯]  ⬜ Morning Exercise
       30 min workout

🌟 75% ↑
Strong · improving
🔥 12 day streak · 85% (30d)

[✓] [✏️] [🗑️]
```

### Habit Card with Broken Streak
```
[🎯]  ⬜ Morning Exercise
       30 min workout
⚠️ Streak broken yesterday! Use a freeze to save it.

🌱 45% ↓
Developing · declining
🔥 0 day streak · 60% (30d)

[✓] [✏️] [🗑️]

[❄️ Use Streak Freeze (2 available)]
```

---

*Last updated: February 26, 2026*