# Phase 6 - Complete Testing Guide

**Purpose:** Step-by-step instructions to test all Phase 6 UI-Backend Integration features.

**Phases Covered:**
- 6.3: Habit Score UI
- 6.4: Streak Freeze UI
- 6.5: Intelligence Dashboard
- 6.6: Habit Stacking UI
- 6.7: Variable Rewards UI

**Last Updated:** February 26, 2026

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
- [x] Can create new habit
- [x] Score displays with percentage
- [x] Score category emoji appears
- [x] Score category label shows (Excellent/Strong/etc.)
- [x] Trend indicator shows (↑↓→)
- [ ] Trend label shows (improving/declining/stable)
- [ ] Streak count displays correctly
- [ ] 30-day completion rate shows

### Streak Freeze Tests
- [ ] Freeze inventory shows in sidebar
- [ ] Progress bar displays correctly
- [x] Can purchase freeze (if XP >= 100)
- [x] Error shows if not enough XP
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

## 🧠 Feature 3: Intelligence Dashboard Testing

### What It Does
- Displays burnout risk assessment
- Shows habit correlations
- Calculates PCS fragility scores
- Provides personalized recommendations

### Step-by-Step Test

#### Step 1: Open the Insights Page
```bash
streamlit run tracking_app/pages/insights.py
```

#### Step 2: Check Key Insights Summary
1. Look at the "💡 Key Insights" section
2. **Expected:** 
   - Burnout risk status (low/moderate/high/critical)
   - Completion trend insights
   - Sleep deficit warnings (if applicable)

#### Step 3: Test Burnout Risk Tab
1. Click on "Burnout Risk" tab
2. **Expected:**
   - Risk score (0-100%)
   - Risk level with emoji
   - Contributing factors list
   - Intervention recommendations

#### Step 4: Test Correlations Tab
1. Click on "Correlations" tab
2. **Prerequisites:** At least 2 habits with 7+ days of data
3. **Expected:**
   - List of habit correlations
   - Correlation coefficients (r values)
   - Strength and direction indicators

#### Step 5: Test Habit Fragility Tab
1. Click on "Habit Fragility" tab
2. **Prerequisites:** At least 14 days of habit data
3. **Expected:**
   - PCS scores for each habit
   - Fragility index (0-100)
   - AUC score (predictability)
   - Habit strength classification

---

## 📚 Feature 4: Habit Stacking Testing

### What It Does
- Create habit stacks with anchors
- Add habits to stacks in sequence
- Track stack completion
- View stack analytics

### Step-by-Step Test

#### Step 1: Open the Stacks Page
```bash
streamlit run tracking_app/pages/stacks.py
```

#### Step 2: Create a New Stack
1. Fill in the "Create New Stack" form:
   - **Name:** "Morning Routine"
   - **Category:** Select "Morning"
   - **Anchor:** Select "Wake up" or custom
2. Click "Create Stack"
3. **Expected:** Stack appears in "Your Stacks" section

#### Step 3: Add Habits to Stack
1. Find your newly created stack
2. Click "➕ Add Habit to Stack"
3. Select a habit from dropdown
4. Enable "Tiny version" checkbox
5. Click "Add to Stack"
6. **Expected:** Habit appears in stack chain

#### Step 4: Verify Stack Display
- Stack shows anchor description
- Habits display in numbered sequence
- Tiny habits show 🌱 indicator
- Tiny version descriptions appear

#### Step 5: Test Analytics
1. Click "📊 View Analytics" on a stack
2. **Expected:**
   - Stack depth count
   - Conversion rate percentage
   - Weak links warnings (if any)

---

## 🎁 Feature 5: Variable Rewards Testing

### What It Does
- Roll for random rewards
- Display rarity badges (Common/Uncommon/Rare/Legendary)
- Track reward inventory
- Show statistics

### Step-by-Step Test

#### Step 1: Open the Rewards Page
```bash
streamlit run tracking_app/pages/rewards.py
```

#### Step 2: Test Roll for Rewards
1. Click "🎲 Roll for Reward" button
2. **Expected:**
   - Spinner animation
   - Result displays (reward or "No reward")
   - XP added if reward won

#### Step 3: Check Roll Result
- **If reward won:**
  - Green success box with reward name
  - Reward description
  - XP earned display
- **If near miss:**
  - Warning "So close! Try again!"
- **If no reward:**
  - Info "No reward this time"

#### Step 4: Test Inventory Tab
1. Click "Inventory" tab
2. **Expected:**
   - Rewards grouped by rarity
   - Count of each rarity collected

#### Step 5: Test Catalog Tab
1. Click "Catalog" tab
2. Use rarity filter dropdown
3. **Expected:**
   - All available rewards displayed
   - Filter by rarity works
   - Shows icon, name, description, XP value

#### Step 6: Test Statistics Tab
1. Click "Statistics" tab
2. **Expected:**
   - Total rolls count
   - Rewards won count
   - Win rate percentage
   - XP from rewards total

---

## 📋 Complete Test Checklist

### Phase 6.3: Habit Score ✅
- [ ] Score displays with percentage
- [ ] Score category emoji appears
- [ ] Trend indicator shows (↑↓→)
- [ ] Streak count displays

### Phase 6.4: Streak Freeze ✅
- [ ] Freeze inventory shows in sidebar
- [ ] Can purchase freeze (if XP >= 100)
- [ ] Broken streak warning appears
- [ ] Using freeze preserves streak

### Phase 6.5: Intelligence Dashboard ✅
- [ ] Burnout risk displays correctly
- [ ] Correlations show when data available
- [ ] PCS fragility scores calculate
- [ ] Key insights update

### Phase 6.6: Habit Stacking ✅
- [ ] Can create stack with anchor
- [ ] Can add habits to stack
- [ ] Tiny habit indicators show
- [ ] Analytics display correctly

### Phase 6.7: Variable Rewards ✅
- [ ] Roll button works
- [ ] Rewards display with rarity
- [ ] XP added correctly
- [ ] Inventory tracks collected rewards
- [ ] Statistics display accurately

---

## 🚀 Run All Pages

```bash
# Main app
streamlit run tracking_app/app.py

# Individual pages
streamlit run tracking_app/pages/habits.py      # Score + Streak Freeze
streamlit run tracking_app/pages/insights.py    # Intelligence Dashboard
streamlit run tracking_app/pages/stacks.py      # Habit Stacking
streamlit run tracking_app/pages/rewards.py     # Variable Rewards
```

---

*Last updated: February 26, 2026*
