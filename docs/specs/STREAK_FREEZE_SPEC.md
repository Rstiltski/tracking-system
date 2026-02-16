# Streak Freeze Specification

**Version:** 1.0  
**Date:** February 16, 2026  
**Status:** Active

---

## Overview

The Streak Freeze mechanic is designed to prevent user churn from broken streaks by allowing users to preserve their streak on a missed day. This addresses the "what-the-hell" effect where users abandon habits entirely after breaking a streak.

### Problem Statement

Current streak system is binary and demotivating:
- User with 100-day streak misses one day → streak resets to 0
- This causes users to quit entirely ("what-the-hell" effect)
- Doesn't show actual habit strength

### Solution

Streak Freeze is an item that:
- Preserves streak on a missed day
- Is consumed automatically when needed
- Can be earned through consistent tracking or purchased with XP

---

## Data Model

### StreakFreeze Object

```javascript
// Add to user data
const userData = {
    // ... existing fields
    inventory: {
        streakFreezes: 3,  // Current count
        maxFreezes: 10     // Maximum allowed
    },
    freezeHistory: [
        { habitId: 'abc123', date: '2026-02-10', used: true }
    ]
};
```

### Configuration Constants

| Property | Value | Description |
|----------|-------|-------------|
| `maxFreezes` | 10 | Maximum number of streak freezes allowed |
| `xpCost` | 100 | XP cost to purchase a streak freeze |
| `earnThreshold` | 7 | Days of consistency to earn one freeze |

---

## Implementation Details

### Core Functions

#### `hasFreeze()`
Check if streak freeze is available

#### `useFreeze(habitId, date)`
Use a streak freeze for a habit

#### `purchaseFreeze()`
Purchase a streak freeze with XP

#### `awardFreeze()`
Award a freeze for consistency

### UI Components

#### Streak Freeze Widget
```html
<div class="streak-freeze-widget">
    <span class="freeze-icon">❄️</span>
    <span class="freeze-count">3</span>
    <button class="purchase-freeze" onclick="StreakFreeze.purchaseFreeze()">
        Buy (100 XP)
    </button>
</div>
```

---

## Behavioral Science Principles

### Loss Aversion
Users are more motivated to avoid losing something they have than gaining something new. Streak freezes allow users to avoid the "loss" of their streak.

### Variable Rewards
Streak freezes are awarded at unpredictable intervals (after 7 days of consistency, 30 days, etc.), which increases engagement through variable ratio reinforcement.

### Gamification Elements
- XP system: Streak freezes can be purchased with earned XP
- Achievement system: Consistent behavior earns free streak freezes
- Inventory management: Limited capacity creates strategic decisions

---

## Integration Points

### With Habit Scoring
- When a freeze is used, the day is marked as "skipped" rather than missed
- This preserves the streak without artificially inflating the habit score
- The freeze usage is logged for analytics

### With XP System
- Purchasing freezes costs XP
- Earning freezes awards XP indirectly (preserving streaks leads to more XP earning opportunities)

### With Analytics
- Track freeze usage patterns
- Monitor correlation between freeze availability and habit retention
- Analyze which habits most commonly use freezes

---

## Risk Mitigation

### Overuse Prevention
- Maximum freeze capacity limits strategic use
- XP cost creates friction preventing frivolous use
- Freeze history allows analysis of problematic habits

### Game Economy Balance
- XP costs balanced against typical XP earning rates
- Earn thresholds calibrated to promote positive behaviors
- Limited inventory prevents hoarding

---

## Future Enhancements

### Advanced Features
- Different types of freezes (partial, temporary)
- Shared freezes between family members
- Freeze expiration to encourage use
- Premium freezes with special properties

### Analytics
- Predict which users would benefit from freezes
- Optimize freeze earning thresholds
- Personalize freeze recommendations

---

## References

- Fogg, B. J. (2009). *Persuasive Technology: Using Computers to Change What We Think and Do*
- Milkman, K. L., et al. (2021). "Habit Formation and Change." *Annual Review of Psychology*
- Research document: "Behavioral Science in Habit Formation Systems.docx"