# Open-Source Projects Research

**Detailed analysis of key open-source personal tracking projects.**

---

## Overview

This document provides detailed analysis of open-source projects that serve as reference implementations for TrackLife enhancements.

---

## Loop Habit Tracker

**Repository:** https://github.com/iSoron/uhabits  
**Platform:** Android  
**Language:** Kotlin/Java  
**Database:** SQLite

### Key Feature: Habit Score Algorithm

Loop replaces rigid streaks with a scientific "Habit Score" using a weighted moving average.

#### Algorithm Details

```
Habit Score = Σ(completion[i] × weight[i]) / Σ(weight[i])

Where:
- completion[i] = 1 if completed on day i, 0 if not
- weight[i] = exp(-i/τ)  (exponential decay)
- τ = time constant (controls decay rate)
- Recent days have higher weight
```

#### Implementation Pattern

```java
// Simplified Loop algorithm
public double computeScore(List<Boolean> completions) {
    double score = 0;
    double totalWeight = 0;
    double lambda = 0.05; // Decay rate
    
    for (int i = 0; i < completions.size(); i++) {
        double weight = Math.exp(-lambda * i);
        totalWeight += weight;
        if (completions.get(i)) {
            score += weight;
        }
    }
    
    return score / totalWeight; // 0.0 to 1.0
}
```

#### Benefits Over Rigid Streaks

| Rigid Streak | Habit Score |
|--------------|-------------|
| Binary: 5 or 0 | Gradient: 0.0 to 1.0 |
| One miss = reset to 0 | Gradual decay |
| Demotivating after break | Forgiving |
| Doesn't show strength | Shows habit strength |

### Architecture

```
uhabits/
├── app/                    # Android app
│   ├── activities/         # UI activities
│   ├── models/             # Data models
│   └── persistence/        # SQLite database
├── core/                   # Core logic
│   ├── models/
│   └── commands/
└── backend/                # Optional sync server
```

### TrackLife Takeaways

1. Implement Habit Score instead of rigid streaks
2. Use exponential decay weighting
3. Display score as percentage (0-100%)

---

## Habitica

**Repository:** https://github.com/HabitRPG/habitica  
**Platform:** Web, iOS, Android  
**Language:** JavaScript (Vue.js/Node.js)  
**Database:** MongoDB

### Key Feature: RPG Gamification

Habitica transforms life into an RPG game with classes, quests, and social accountability.

### Core Mechanics

#### Currency System

| Currency | Earned By | Spent On |
|----------|-----------|----------|
| **Gold** | Completing tasks | Equipment, custom rewards |
| **Gems** | Achievements, purchases | Special items |
| **XP** | All completions | Level progression |
| **HP** | N/A (starts at 50) | Lost on misses |

#### Health System

```javascript
// Damage calculation
function calculateDamage(user, missedDailies) {
    const baseDamage = missedDailies.length * 2.5;
    const constitutionBonus = user.stats.con * 0.5;
    const armorReduction = user.items.armor.defense;
    
    return Math.max(0, baseDamage - constitutionBonus - armorReduction);
}

// On HP reaching 0
function onDeath(user) {
    user.stats.hp = 0;
    user.stats.lvl = Math.max(1, user.stats.lvl - 1);
    user.items.armor = null; // Lose equipment
    user.stats.gp = Math.floor(user.stats.gp * 0.5); // Lose half gold
}
```

#### Streak Freeze Item

```javascript
// Streak freeze mechanics
const STREAK_FREEZE_ITEM_ID = 'snowball';

function protectStreak(habit, userId) {
    const user = getUser(userId);
    const freezeItem = user.items.find(i => i.key === STREAK_FREEZE_ITEM_ID);
    
    if (freezeItem && freezeItem.quantity > 0) {
        freezeItem.quantity -= 1;
        habit.streakPreserved = true;
        return true; // Streak protected
    }
    return false; // No freeze available
}
```

#### Party System

```javascript
// Quest damage distribution
function processQuestDamage(party, missedDailiesByUser) {
    const totalMissed = Object.values(missedDailiesByUser)
        .reduce((sum, count) => sum + count, 0);
    
    const bossDamage = totalMissed * party.quest.boss.strength;
    
    // All party members take damage
    party.members.forEach(member => {
        member.stats.hp -= bossDamage;
    });
}
```

### Architecture

```
habitica/
├── website/                # Vue.js frontend
│   ├── client/             # Client-side code
│   └── common/             # Shared code
├── api/                    # Node.js backend
│   ├── controllers/
│   ├── models/
│   └── middleware/
└── migrations/             # MongoDB migrations
```

### TrackLife Takeaways

1. Implement HP system with loss on missed habits
2. Add Streak Freeze as purchasable item
3. Consider Party system for social accountability
4. Use variable rewards (random loot)

---

## ActivityWatch

**Repository:** https://github.com/ActivityWatch/activitywatch  
**Platform:** Desktop (Windows/Mac/Linux)  
**Language:** Python  
**Database:** SQLite

### Key Feature: Event Sourcing with Buckets

ActivityWatch stores all data as immutable events in "buckets."

### Bucket Model

```python
# Bucket structure
{
    "id": "aw-watcher-window_hostname",
    "type": "current-window",
    "client": "aw-watcher-window",
    "hostname": "user-machine",
    "created": "2026-02-14T10:00:00Z"
}

# Event structure
{
    "timestamp": "2026-02-14T10:00:00Z",
    "duration": 300.0,  # seconds
    "data": {
        "app": "Chrome",
        "title": "GitHub - ActivityWatch",
        "url": "https://github.com/..."
    }
}
```

### Heartbeat Mechanism

Instead of recording start/end times, ActivityWatch uses "heartbeats":

```python
def heartbeat(event, pulsetime=30):
    """
    If same event within pulsetime, extend duration.
    Otherwise, create new event.
    """
    last_event = get_last_event()
    
    if last_event and last_event.data == event.data:
        time_diff = event.timestamp - last_event.timestamp
        if time_diff < pulsetime:
            # Extend last event
            last_event.duration += time_diff
            return last_event
    
    # Create new event
    return create_event(event)
```

### Query Language

```python
# ActivityWatch query example
def query_productivity(bucket_id, time_range):
    events = query_bucket(bucket_id, time_range)
    
    # Filter out AFK time
    afk_events = query_bucket("aw-watcher-afk_" + hostname, time_range)
    events = filter_period_intersect(events, afk_events)
    
    # Group by application
    return merge_events_by_keys(events, ["app"])
```

### Architecture

```
activitywatch/
├── aw-server/              # Core server
│   ├── aw_server/
│   │   ├── api.py          # REST API
│   │   └── datastore.py    # SQLite storage
│   └── tests/
├── aw-watcher-*/           # Data collectors
│   ├── aw-watcher-window/
│   └── aw-watcher-afk/
└── aw-qt/                  # Qt GUI
```

### TrackLife Takeaways

1. Implement event sourcing for all data
2. Use heartbeat pattern for continuous tracking
3. Store immutable events, derive state
4. Create query language for insights

---

## Gullak

**Repository:** https://github.com/mr-karan/gullak  
**Platform:** CLI/Web  
**Language:** Go  
**Database:** SQLite

### Key Feature: AI-Native Logging

Gullak uses LLMs to parse natural language into structured data.

### Natural Language Processing

```go
// User input: "Had coffee for $5 at Starbucks"
// LLM output:
{
    "category": "Food & Drinks",
    "subcategory": "Coffee",
    "amount": 5.00,
    "currency": "USD",
    "merchant": "Starbucks",
    "date": "2026-02-14"
}
```

### KERNEL Prompt Framework

```markdown
K - Keep it simple: "Extract expense data"
E - Easy to verify: "Output valid JSON"
R - Reproducible: "Use ISO 8601 for dates"
N - Narrow scope: "Only extract financial data"
E - Explicit constraints: "Return null for unknown values"
L - Logical structure: Input → Thinking → JSON Output
```

### System Prompt Example

```markdown
You are a financial data extractor. Parse the user's input into structured JSON.

Input: {user_input}

Output format:
{
    "category": string,
    "amount": number,
    "merchant": string,
    "date": "YYYY-MM-DD",
    "notes": string
}

Rules:
- If amount not specified, return null
- Infer category from context
- Today's date is 2026-02-14
```

### Architecture

```
gullak/
├── cmd/                    # CLI commands
├── internal/
│   ├── llm/               # LLM integration
│   │   ├── openai.go
│   │   └── local.go       # Local LLM support
│   ├── storage/           # SQLite
│   └── parser/            # NLP parsing
└── web/                    # Web interface
```

### TrackLife Takeaways

1. Add natural language input for habits
2. Support local LLM (Ollama) for privacy
3. Use structured prompts for reliable parsing
4. Allow manual correction of parsed data

---

## Nomie

**Repository:** https://github.com/open-nomie/nomie6-oss  
**Platform:** Web (PWA)  
**Language:** JavaScript (Svelte)  
**Database:** IndexedDB / CouchDB

### Key Feature: Flexible Tracking

Nomie allows tracking anything with custom trackers.

### Tracker Model

```javascript
const tracker = {
    id: "mood",
    type: "range",  // checkbox, range, number, timer
    name: "Mood",
    emoji: "😊",
    min: 1,
    max: 5,
    color: "#4CAF50",
    tags: ["wellness", "daily"]
};
```

### Storage Engine Abstraction

```javascript
// Nomie's storage abstraction
class StorageEngine {
    async save(key, value) { throw new Error("Not implemented"); }
    async get(key) { throw new Error("Not implemented"); }
    async delete(key) { throw new Error("Not implemented"); }
    async query(filter) { throw new Error("Not implemented"); }
}

// IndexedDB implementation
class IndexedDBStorage extends StorageEngine {
    async save(key, value) {
        return db.trackers.put({ _id: key, ...value });
    }
}

// CouchDB implementation (for sync)
class CouchDBStorage extends StorageEngine {
    async save(key, value) {
        return fetch(`${this.url}/${key}`, {
            method: 'PUT',
            body: JSON.stringify(value)
        });
    }
}
```

### Plugin System

```javascript
// Nomie plugin example
const plugin = {
    id: "habit-chains",
    name: "Habit Chains",
    version: "1.0.0",
    
    onRecord(record) {
        // Process record
    },
    
    render(container) {
        // Render plugin UI
    },
    
    settings: [
        { key: "chainLength", type: "number", default: 7 }
    ]
};
```

### Architecture

```
nomie6-oss/
├── src/
│   ├── lib/               # Core library
│   │   ├── storage/       # Storage engines
│   │   ├── trackers/      # Tracker types
│   │   └── plugins/       # Plugin system
│   ├── routes/            # Svelte routes
│   └── stores/            # Svelte stores
└── static/                # PWA assets
```

### TrackLife Takeaways

1. Use storage abstraction for flexibility
2. Support custom tracker types
3. Implement plugin system for extensibility
4. Build as PWA for offline support

---

## StudyU / StudyMe

**Repository:** https://github.com/hpi-studyu/studyu  
**Platform:** Web / Mobile (Flutter)  
**Language:** Dart (Flutter), Python (Backend)

### Key Feature: N-of-1 Trials

StudyU enables rigorous self-experimentation with proper scientific methodology.

### Experiment Protocol

```json
{
    "id": "magnesium-sleep-trial",
    "name": "Magnesium for Sleep Quality",
    "hypothesis": "Magnesium before bed improves sleep quality",
    "design": "WITHDRAWAL",  // A-B-A
    "phases": [
        { "type": "baseline", "duration": 7, "label": "A" },
        { "type": "intervention", "duration": 14, "label": "B" },
        { "type": "baseline", "duration": 7, "label": "A" }
    ],
    "intervention": {
        "name": "Magnesium 400mg",
        "instructions": "Take 400mg magnesium 1 hour before bed"
    },
    "outcome": {
        "name": "Sleep Quality",
        "type": "scale",
        "min": 1,
        "max": 10
    },
    "randomization": "BLOCKED"  // For alternating designs
}
```

### Phase Randomization

```dart
// Randomized block design
List<String> generatePhases(int blocks, String a, String b) {
    final phases = <String>[];
    for (var i = 0; i < blocks; i++) {
        final block = Random().nextBool() 
            ? [a, b] 
            : [b, a];
        phases.addAll(block);
    }
    return phases;
}
```

### Statistical Analysis

```python
# Bayesian analysis of N-of-1 trial
def analyze_nof1(baseline_scores, intervention_scores):
    from scipy import stats
    
    # Effect size
    effect = np.mean(intervention_scores) - np.mean(baseline_scores)
    
    # Probability of benefit
    t_stat, p_value = stats.ttest_rel(intervention_scores, baseline_scores)
    
    # Bayesian probability
    prob_benefit = 1 - stats.t.cdf(0, df=len(baseline_scores)-1)
    
    return {
        "effect_size": effect,
        "p_value": p_value,
        "probability_of_benefit": prob_benefit
    }
```

### Architecture

```
studyu/
├── studyu_platform/        # Web platform
│   ├── backend/            # Python/FastAPI
│   └── frontend/           # Vue.js
├── studyme/                # Mobile app
│   └── lib/                # Flutter
└── analysis/               # R/Python analysis
```

### TrackLife Takeaways

1. Implement N-of-1 trial module
2. Support A-B-A and alternating designs
3. Add phase randomization
4. Include statistical analysis

---

## Reference Summary

| Project | Key Feature | TrackLife Application |
|---------|-------------|----------------------|
| **Loop** | Habit Score algorithm | Replace rigid streaks |
| **Habitica** | RPG gamification | HP system, Streak Freeze |
| **ActivityWatch** | Event sourcing | Immutable event storage |
| **Gullak** | AI-native logging | Natural language input |
| **Nomie** | Flexible tracking | Custom trackers, plugins |
| **StudyU** | N-of-1 trials | Self-experimentation |

---

## Cross-References

| Related Document | Content |
|------------------|---------|
| [RESEARCH_SUMMARY.md](RESEARCH_SUMMARY.md) | Overview of all research |
| [BEHAVIORAL_SCIENCE.md](BEHAVIORAL_SCIENCE.md) | Habitica gamification details |
| [CORRELATION_ENGINE_RESEARCH.md](CORRELATION_ENGINE_RESEARCH.md) | Phase 2.1 Correlation Engine research |
| [docs/specs/HABIT_SCORE_SPEC.md](../specs/HABIT_SCORE_SPEC.md) | Loop algorithm spec |
| [docs/specs/N_OF_1_TRIALS_SPEC.md](../specs/N_OF_1_TRIALS_SPEC.md) | StudyU implementation |

---

## Cloned Repositories

The following repositories have been cloned for detailed analysis:

| Repository | Location | Purpose |
|------------|----------|---------|
| roqua/autovar | `repos/autovar/` | VAR models, Granger causality (Phase 2.1) |
| p0lloc/perfice | `repos/perfice/` | Automatic insights, NLG (Phase 2.1) |
| markrai/fitbaus | `repos/fitbaus/` | Correlation matrix dashboard (Phase 2.1) |
| farhanaugustine/Temporal_Behavior_Analysis | `repos/Temporal_Behavior_Analysis/` | Time-lagged cross-correlation (Phase 2.1) |
| gianlucatruda/quantified-sleep | `repos/quantified-sleep/` | ML for lag detection (Phase 2.1) |
| karlicoss/HPI | `repos/HPI/` | Data unification infrastructure (Phase 2.1) |

---

*Last updated: February 2026*
