# Habit Score Specification

**Feature:** Scientific habit strength measurement  
**Phase:** 1.1  
**Priority:** High  
**Effort:** Low

---

## Overview

Replace rigid streak counting with a weighted moving average algorithm that provides a more accurate and forgiving measure of habit strength.

---

## Problem Statement

### Current Behavior

- Streaks are binary: count increments on completion, resets to 0 on miss
- User with 100-day streak misses one day → streak = 0
- This causes the "what-the-hell" effect: users quit after breaking streaks
- Streak count doesn't reflect actual habit strength

### Desired Behavior

- Score from 0.0 to 1.0 (displayed as 0-100%)
- Recent days have higher weight than older days
- Gradual decay on misses, not reset to zero
- More forgiving and scientifically accurate

---

## Algorithm

### Formula

```
Habit Score = Σ(completion[i] × weight[i]) / Σ(weight[i])

Where:
- completion[i] = 1 if completed on day i, 0 if not
- weight[i] = exp(-λ × i)
- λ = decay rate (default: 0.05)
- i = days ago (0 = today, 1 = yesterday, etc.)
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `decayRate` (λ) | 0.05 | Controls how quickly old days lose weight |
| `lookbackDays` | 60 | Maximum days to consider in calculation |

### Decay Rate Effects

| Decay Rate | Effect |
|------------|--------|
| 0.02 | Slow decay, older days matter more |
| 0.05 | Balanced (recommended) |
| 0.10 | Fast decay, only recent days matter |

### Example Calculations

#### Example 1: Perfect 7-day streak
```
Day 0 (today):     completion=1, weight=1.000
Day 1:             completion=1, weight=0.951
Day 2:             completion=1, weight=0.904
Day 3:             completion=1, weight=0.860
Day 4:             completion=1, weight=0.818
Day 5:             completion=1, weight=0.778
Day 6:             completion=1, weight=0.740

Score = 6.051 / 6.051 = 1.00 (100%)
```

#### Example 2: 6 of 7 days completed
```
Same weights as above, but Day 3 missed:
Score = 5.191 / 6.051 = 0.86 (86%)
```

#### Example 3: One miss after 30-day streak
```
With decay rate 0.05:
- Recent days have highest weight
- One miss reduces score by ~3-5%
- Score would be ~95% instead of 0
```

---

## Implementation

### Module: `js/habit-score.js`

```javascript
/**
 * Habit Score Module
 * Implements weighted moving average for habit strength calculation
 */
const HabitScore = {
    config: {
        decayRate: 0.05,
        lookbackDays: 60
    },
    
    /**
     * Configure the algorithm
     * @param {Object} options - Configuration options
     */
    configure(options) {
        Object.assign(this.config, options);
    },
    
    /**
     * Calculate habit score from completion history
     * @param {Array<boolean>} completions - Array of completion status (newest first)
     * @returns {number} Score from 0.0 to 1.0
     */
    calculate(completions) {
        if (!completions || completions.length === 0) return 0;
        
        let weightedSum = 0;
        let totalWeight = 0;
        
        const daysToConsider = Math.min(completions.length, this.config.lookbackDays);
        
        for (let i = 0; i < daysToConsider; i++) {
            const weight = Math.exp(-this.config.decayRate * i);
            totalWeight += weight;
            
            if (completions[i]) {
                weightedSum += weight;
            }
        }
        
        return totalWeight > 0 ? weightedSum / totalWeight : 0;
    },
    
    /**
     * Get score as percentage (0-100)
     * @param {Array<boolean>} completions - Completion history
     * @returns {number} Percentage score
     */
    getPercentage(completions) {
        return Math.round(this.calculate(completions) * 100);
    },
    
    /**
     * Get score category for display
     * @param {number} score - Score from 0.0 to 1.0
     * @returns {Object} Category with label, color, and emoji
     */
    getCategory(score) {
        if (score >= 0.85) return { label: 'Excellent', color: '#4CAF50', emoji: '🌟' };
        if (score >= 0.70) return { label: 'Strong', color: '#8BC34A', emoji: '💪' };
        if (score >= 0.50) return { label: 'Developing', color: '#FFC107', emoji: '🌱' };
        if (score >= 0.30) return { label: 'Building', color: '#FF9800', emoji: '🔧' };
        return { label: 'Starting', color: '#F44336', emoji: '🆕' };
    },
    
    /**
     * Get completion history for a habit
     * @param {string} habitId - Habit ID
     * @param {number} days - Number of days to retrieve
     * @returns {Array<boolean>} Completion array (newest first)
     */
    getCompletionHistory(habitId, days = 60) {
        const habit = Storage.getHabit(habitId);
        if (!habit) return [];
        
        const completions = [];
        const today = new Date();
        
        for (let i = 0; i < days; i++) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0];
            
            completions.push(habit.completions?.[dateStr] || false);
        }
        
        return completions;
    },
    
    /**
     * Calculate and display score for a habit
     * @param {string} habitId - Habit ID
     * @returns {Object} Score data
     */
    getHabitScoreData(habitId) {
        const completions = this.getCompletionHistory(habitId);
        const score = this.calculate(completions);
        const category = this.getCategory(score);
        
        return {
            score,
            percentage: Math.round(score * 100),
            category,
            completions: completions.filter(c => c).length,
            totalDays: completions.length
        };
    }
};

// Make globally available
window.HabitScore = HabitScore;
```

---

## UI Components

### Score Ring Component

```html
<div class="habit-score-ring" data-score="75">
    <svg viewBox="0 0 100 100">
        <circle class="bg" cx="50" cy="50" r="45"/>
        <circle class="progress" cx="50" cy="50" r="45" 
                stroke-dasharray="283"
                stroke-dashoffset="70.75"/>
    </svg>
    <div class="score-content">
        <span class="score-value">75%</span>
        <span class="score-emoji">💪</span>
    </div>
</div>
```

### CSS Styles

```css
.habit-score-ring {
    position: relative;
    width: 80px;
    height: 80px;
}

.habit-score-ring svg {
    transform: rotate(-90deg);
}

.habit-score-ring .bg {
    fill: none;
    stroke: #e0e0e0;
    stroke-width: 8;
}

.habit-score-ring .progress {
    fill: none;
    stroke: var(--score-color, #4CAF50);
    stroke-width: 8;
    stroke-linecap: round;
    transition: stroke-dashoffset 0.5s ease;
}

.score-content {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
}

.score-value {
    font-size: 1.2rem;
    font-weight: bold;
}

.score-emoji {
    display: block;
    font-size: 1rem;
}
```

---

## Integration

### Update `js/habits.js`

```javascript
// In renderHabits function
function renderHabits() {
    habits.forEach(habit => {
        const scoreData = HabitScore.getHabitScoreData(habit.id);
        
        // Replace streak display with score
        const scoreHtml = `
            <div class="habit-score-ring" style="--score-color: ${scoreData.category.color}">
                <span class="score-value">${scoreData.percentage}%</span>
                <span class="score-emoji">${scoreData.category.emoji}</span>
            </div>
            <div class="score-label">${scoreData.category.label}</div>
        `;
        
        // ... render habit card
    });
}
```

---

## Testing

### Unit Tests

```javascript
// js/tests/habit-score.test.js
describe('HabitScore', () => {
    test('returns 0 for empty completions', () => {
        expect(HabitScore.calculate([])).toBe(0);
    });
    
    test('returns 1 for perfect streak', () => {
        const completions = [true, true, true, true, true, true, true];
        expect(HabitScore.calculate(completions)).toBeCloseTo(1.0, 2);
    });
    
    test('returns correct score for mixed completions', () => {
        const completions = [true, true, false, true, true, true, false];
        const score = HabitScore.calculate(completions);
        expect(score).toBeGreaterThan(0.5);
        expect(score).toBeLessThan(1.0);
    });
    
    test('recent days have higher weight', () => {
        const recentMiss = [false, true, true, true, true, true, true];
        const oldMiss = [true, true, true, true, true, true, false];
        
        const recentMissScore = HabitScore.calculate(recentMiss);
        const oldMissScore = HabitScore.calculate(oldMiss);
        
        expect(oldMissScore).toBeGreaterThan(recentMissScore);
    });
    
    test('getCategory returns correct category', () => {
        expect(HabitScore.getCategory(0.90).label).toBe('Excellent');
        expect(HabitScore.getCategory(0.75).label).toBe('Strong');
        expect(HabitScore.getCategory(0.55).label).toBe('Developing');
        expect(HabitScore.getCategory(0.35).label).toBe('Building');
        expect(HabitScore.getCategory(0.15).label).toBe('Starting');
    });
});
```

---

## Migration

### From Streak to Score

```javascript
// Migration script
function migrateStreakToScore() {
    const habits = Storage.getHabits();
    
    habits.forEach(habit => {
        // Keep streak for display during transition
        habit.legacyStreak = habit.streak;
        
        // Calculate initial score from existing data
        const completions = HabitScore.getCompletionHistory(habit.id);
        habit.score = HabitScore.calculate(completions);
    });
    
    Storage.saveHabits(habits);
}
```

---

## References

- **Source:** Loop Habit Tracker (iSoron/uhabits)
- **Research:** [docs/research/OPEN_SOURCE_PROJECTS.md](../research/OPEN_SOURCE_PROJECTS.md)
- **Phase:** [phases/PHASE_1_FOUNDATION.md](../../phases/PHASE_1_FOUNDATION.md)

---

*Last updated: February 2026*