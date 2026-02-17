# Phase 3: Behavioral Science Implementation

**Duration:** 3-4 weeks
**Status:** 📋 Not Started
**Dependencies:** Phase 2 Complete
**Created:** February 16, 2026

---

## Overview

Phase 3 focuses on implementing evidence-based behavioral science techniques to help users build lasting habits. This phase transforms research insights into practical features that guide users toward sustainable behavior change.

---

## Goals

| Goal | Success Metric |
|------|----------------|
| Implement habit stacking | Users can link habits to existing routines |
| Implement implementation intentions | Users can define when/where habits occur |
| Implement reward scheduling | Variable rewards increase engagement |
| Implement social accountability | Users can share progress with accountability partners |

---

## Phase 3.1: Habit Stacking

**Priority:** High  
**Effort:** Medium  
**Duration:** 1 week  
**Status:** 🔄 In Progress

### Problem

Users struggle to establish new habits because they lack clear triggers. Without an existing routine to attach to, new habits require conscious effort and willpower.

### Solution

Implement habit stacking based on BJ Fogg's Tiny Habits methodology:
- Link new habits to existing behaviors
- Create automatic triggers
- Reduce cognitive load

### Methodology: The "Anchor" Protocol

The core of Habit Stacking relies on the formula: **"After I [Current Habit], I will [New Habit]"**

**Key Principles:**

1. **The "Tiny" Constraint:** New habits must be scaled down to < 30 seconds (e.g., "floss one tooth" instead of "floss teeth") to bypass reliance on motivation.

2. **Anchor Precision:** Vague anchors like "in the morning" fail. Effective anchors are precise physical events:
   - "After I put my coffee mug down"
   - "After I flush the toilet"
   - "After I close my laptop"

3. **Stack Depth:** Introduce only **one** new habit into a stack at a time. Once the behavior achieves a high automaticity score (SRBAI), a second link can be added.

### Data Model

```sql
-- The core unit of behavior
CREATE TABLE habits (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    title TEXT NOT NULL,
    difficulty_level INTEGER DEFAULT 1 -- 1=Tiny, 5=Hard
);

-- Defines the "Stack" (The Chain)
CREATE TABLE habit_stacks (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    name TEXT, -- e.g., "Morning Routine"
    trigger_description TEXT -- e.g., "After I pour my coffee"
);

-- Links Habits to Stacks in a specific order
CREATE TABLE stack_items (
    stack_id UUID REFERENCES habit_stacks(id),
    habit_id UUID REFERENCES habits(id),
    position_index INTEGER NOT NULL, -- 0, 1, 2...
    delay_seconds INTEGER DEFAULT 0, -- Buffer time between habits
    PRIMARY KEY (stack_id, habit_id)
);
```

### UI Implementation

**A. The Anchor Wizard**
Instead of a time picker, implement an "Anchor Selector" with categorized presets:

| Category | Anchor Examples |
|----------|-----------------|
| Morning | Waking up, Turning off alarm, Brushing teeth, Brewing coffee |
| Transit | Starting car, Arriving at desk, Walking through front door |
| Evening | Washing dishes, Putting on pajamas, Turning off lights |

**B. Daisy Chain UI**
- Display stacked habits as vertical timeline with connector lines
- Unified Completion State: When first habit is checked, "unlock" the next
- Visual "domino effect" through the chain

### Analytics & Tracking

| Metric | Description | Target |
|--------|-------------|--------|
| **Stack Conversion Rate** | % times Habit B completed given Habit A | > 60% |
| **Automaticity Score (SRBAI)** | 4-question survey after 14 days | High automaticity |
| **Stack Decay** | Drop-off point in chain | Identify weak links |

### Tasks

- [x] Research habit stacking methodology (BJ Fogg's Tiny Habits)
- [ ] Design habit stacking data model
- [ ] Implement `brain/behavioral/habit_stacking.py`
- [ ] Create habit stacking UI
- [ ] Add habit chain visualization
- [ ] Track stacking effectiveness

### Implementation

*See `brain/behavioral/habit_stacking.py`*

---

## Phase 3.2: Implementation Intentions

**Priority:** High  
**Effort:** Medium  
**Duration:** 1 week  
**Status:** 🔄 In Progress

### Problem

Users set vague goals like "exercise more" without specifying when or where. Research shows that specific implementation intentions dramatically increase follow-through.

### Solution

Implement "If-Then" planning based on Peter Gollwitzer's research:
- Help users define specific triggers
- Create context-dependent action plans
- Increase habit automation

### Methodology: The "If-Then" Protocol

Implementation Intentions (II) use the structure: *"If situation X is encountered, then I will perform the goal-directed response Y!"*

**Key Principles:**

1. **Strategic Automaticity:** Delegates behavior control to environmental cues, bypassing willpower
2. **Specificity is King:** Vague cues ("When I feel tired") fail. Concrete cues ("When the clock strikes 14:00") succeed.
3. **Two-Part Mechanism:**
   - **Perceptual Readiness:** The "If" cue is identified 2x faster than non-cued stimuli
   - **Response Automation:** The "Then" action executes with less cognitive load

### Research Evidence

| Metric | Finding |
|--------|---------|
| **Effect Size** | Medium-to-large (d=0.6-0.8) on goal attainment |
| **Success Rate** | Closes intention-behavior gap (53% → significantly higher) |
| **Cue Detection** | 2x faster identification of cued stimuli |
| **Cognitive Load** | Reduced reaction time for automated responses |

### Formal Model

```
Standard Goal Intention: I intend to achieve Z
Implementation Intention: If X, then I will Y

Efficacy E = P(B|C) where cognitive_cost → 0
```

### Data Model

```python
@dataclass
class ImplementationIntention:
    id: str
    goal_id: str
    if_condition: IfCondition  # Trigger
    then_action: ThenAction    # Response
    is_active: bool = True
    
@dataclass
class IfCondition:
    trigger_type: str  # 'time', 'event', 'location', 'app_state'
    source: str        # 'clock', 'calendar', 'system'
    predicate: str     # 'time == "08:00"'
    
@dataclass
class ThenAction:
    action_type: str   # 'notification', 'ui_change', 'script'
    payload: str       # Action details
```

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   EventBus      │────▶│  Rule Matcher    │────▶│  Dispatcher     │
│  (Time, App,    │     │  (If-Then Logic) │     │  (Notification, │
│   Location)     │     │                  │     │   UI, Script)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Trigger Types

| Type | Example | Source |
|------|---------|--------|
| **Time** | "When it's 08:00" | Clock |
| **Event** | "After I complete habit X" | EventBus |
| **Location** | "When I arrive at gym" | GPS/Check-in |
| **App State** | "When VS Code opens" | ActivityWatch |

### Tasks

- [x] Research implementation intentions methodology (Gollwitzer's If-Then planning)
- [ ] Design implementation intention schema
- [ ] Implement `ImplementationIntention` dataclass
- [ ] Implement `IfCondition` and `ThenAction` dataclasses
- [ ] Implement `RuleMatcher` with forward-chaining logic
- [ ] Implement `IntentionEngine` class
- [ ] Create If-Then planning interface
- [ ] Add context-aware reminders
- [ ] Track intention effectiveness

### Implementation

*See `brain/behavioral/implementation_intentions.py`*

### References

- Gollwitzer, P. M. (1999). "Implementation intentions: Strong effects of simple plans"
- WOOP Methodology: https://woopmylife.org/
- Experta (Python Rule Engine): https://github.com/nilp0inter/experta

---

## Phase 3.3: Reward Scheduling

**Priority:** Medium  
**Effort:** Medium  
**Duration:** 1 week  
**Status:** 🔄 In Progress

### Problem

Fixed rewards lose effectiveness over time. Users become habituated to predictable rewards, reducing motivation.

### Solution

Implement variable reward scheduling based on B.F. Skinner's operant conditioning:
- Variable Ratio (VR) reinforcement schedule
- Surprise rewards with weighted probability
- Achievement anticipation mechanics

### Methodology: Variable Ratio Schedule

Variable Ratio (VR) schedules provide reinforcement after an unpredictable number of responses, generating the highest response rate and extinction resistance.

**Key Principles:**

1. **Intermittent Reinforcement**: Rewards are delivered unpredictably, not every time
2. **Dopamine Prediction Error**: Unpredictability keeps dopamine response high
3. **Extinction Resistance**: Behaviors persist longer when rewards cease
4. **Near-Miss Effect**: "Almost won" triggers similar dopamine response

### Research Evidence

| Metric | Finding |
|--------|---------|
| **Response Rate** | Highest of any reinforcement schedule |
| **Extinction Resistance** | Significantly longer than continuous reinforcement |
| **Optimal Probability** | ~30% base drop chance with weighted rarities |

### Formal Model: Dopamine Prediction Error

```
δt = Rt + γV(St+1) - V(St)

Where:
- Rt = Actual reward at time t (0 or 1)
- V(St) = Expected reward
- δt > 0 = Positive Prediction Error (Surprise) → Learning

Fixed rewards: δ → 0 (Habituation)
Variable rewards: δ remains consistently high
```

### The Hook Model (Nir Eyal)

| Reward Type | Description | Examples |
|-------------|-------------|----------|
| **Tribe** | Social validation | Likes, leaderboards, recognition |
| **Hunt** | Material resources | Badges, unlockables, points, XP |
| **Self** | Mastery & competence | Leveling up, streak completion |

### Data Model

```python
class RewardType(Enum):
    TRIBE = "tribe"      # Social validation
    HUNT = "hunt"        # Material resources
    SELF = "self"        # Mastery/competence

class Rarity(Enum):
    COMMON = "common"       # 60% weight
    UNCOMMON = "uncommon"   # 25% weight
    RARE = "rare"           # 12% weight
    LEGENDARY = "legendary" # 3% weight

@dataclass
class Reward:
    id: str
    name: str
    reward_type: RewardType
    rarity: Rarity
    weight: float
    value: int
    icon: str
    description: str

@dataclass
class RewardTable:
    rewards: List[Reward]
    base_drop_chance: float = 0.3
    
    def roll(self, context: Dict) -> Optional[Reward]:
        """Roll for a reward using weighted random selection"""
```

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  User Action    │────▶│  Reward Engine   │────▶│  UI Feedback    │
│  (Completion)   │     │  (Roll & Select) │     │  (Animation)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Reward Table    │
                        │  (Weighted Items)│
                        └──────────────────┘
```

### Satiation Prevention

Reward value decays with frequency: `V ∝ 1/f`

- Track reward history per user
- Adjust weights based on recent rewards
- Implement "cooldown" for rare rewards

### Tasks

- [x] Research variable reward mechanisms (Skinner's operant conditioning)
- [ ] Design reward scheduling algorithm
- [ ] Implement `Reward` and `RewardTable` dataclasses
- [ ] Implement `RewardEngine` class
- [ ] Implement weighted random selection
- [ ] Add reward history tracking
- [ ] Create reward UI feedback
- [ ] Track reward effectiveness

### Implementation

*See `brain/behavioral/rewards.py`*

### References

- Skinner, B.F. (1953). "Science and Human Behavior"
- Eyal, N. (2014). "Hooked: How to Build Habit-Forming Products"
- Habitica (Open Source): https://github.com/Habitica/habitica

---

## Phase 3.4: Social Accountability

**Priority:** Medium  
**Effort:** Medium  
**Duration:** 1 week

### Problem

Users lack external accountability. Without social pressure, it's easy to skip habits when motivation wanes.

### Solution

Implement accountability features:
- Accountability partner system
- Progress sharing
- Streak competitions
- Commitment contracts

### Tasks

- [ ] Research social accountability mechanisms (awaiting user input)
- [ ] Design accountability partner system
- [ ] Implement progress sharing
- [ ] Add commitment contract features
- [ ] Track accountability effectiveness

### Implementation

*Awaiting user research and guidance*

---

## Success Criteria

| Criteria | How to Verify | Status |
|----------|---------------|--------|
| Habit stacking works | Users can create habit chains | [ ] |
| Implementation intentions work | Users can define If-Then plans | [ ] |
| Variable rewards work | Surprise rewards increase engagement | [ ] |
| Social accountability works | Users can add accountability partners | [ ] |

---

## Dependencies

| Dependency | Purpose | Status |
|------------|---------|--------|
| Phase 1 Complete | Foundation features | ✅ |
| Phase 2 Complete | Intelligence features | ✅ |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Feature complexity overwhelms users | Progressive disclosure, simple defaults |
| Privacy concerns with social features | Opt-in only, clear permissions |
| Variable rewards feel manipulative | Transparent system, user control |

---

## Next Phase

After completing Phase 3, proceed to:
- Phase 4: Reminders & Notifications

---

## Research Needed

This phase requires user-provided research on:

1. **Habit Stacking**
   - BJ Fogg's Tiny Habits methodology
   - Optimal habit chain length
   - Best practices for linking behaviors

2. **Implementation Intentions**
   - Gollwitzer's research on If-Then planning
   - Effective trigger design
   - Context-dependent behavior activation

3. **Variable Rewards**
   - Skinner's operant conditioning research
   - Optimal reward schedules
   - Gamification best practices

4. **Social Accountability**
   - Social facilitation research
   - Commitment contract effectiveness
   - Peer pressure dynamics

---

*Last updated: February 16, 2026*
*Status: Awaiting user research and guidance*