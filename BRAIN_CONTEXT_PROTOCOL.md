# 🧠 Brain Context Protocol

**The Constitution for AI Interaction in This Project**

---

## Overview

The Brain Context Protocol defines the **immutable rules** for how AI assistants interact with this project. These rules ensure consistent, intelligent behavior that leverages the full power of the brain system architecture.

---

## The Three Laws

### Law 1: README.md Files Are the Source of Truth

```
┌─────────────────────────────────────────────────────────────────┐
│                     LAW 1: CONTEXT FIRST                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  BEFORE processing ANY task, the AI MUST:                       │
│                                                                  │
│  1. Read README.md (main project documentation)                 │
│  2. Read brain/README.md (brain system architecture)            │
│  3. Read PROJECT_RULES.md (development guidelines)              │
│  4. Read domain-specific READMEs as needed                      │
│                                                                  │
│  These files contain:                                           │
│  - Project architecture and design                              │
│  - Feature documentation                                        │
│  - Coding standards and conventions                             │
│  - Brain system design and contracts                            │
│                                                                  │
│  NEVER assume context. ALWAYS load it from READMEs.             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Law 2: The Brain Folder Is the Thinking Process

```
┌─────────────────────────────────────────────────────────────────┐
│                     LAW 2: THINK BRAIN                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ALL operations MUST flow through the brain architecture:       │
│                                                                  │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │  Router  │──▶│ Policies │──▶│  State   │──▶│  Tools   │    │
│  │          │   │          │   │ Machine  │   │          │    │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘    │
│       │              │              │              │           │
│       ▼              ▼              ▼              ▼           │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Audit Log (append-only)                      │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Components:                                                    │
│  - Router: Validates and routes commands                        │
│  - Policies: Enforces security and business rules               │
│  - State Machines: Manages entity lifecycle                     │
│  - Tools: Executes operations                                   │
│  - Cerebellum: Coordinates all writes                           │
│  - Nervous System: Event-based communication                    │
│  - Audit Log: Records everything                                │
│                                                                  │
│  NEVER bypass the brain. ALWAYS use its architecture.          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Law 3: Simple Prompts Yield Deep Understanding

```
┌─────────────────────────────────────────────────────────────────┐
│                     LAW 3: DEEP UNDERSTANDING                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User's simple prompt → AI's deep understanding                 │
│                                                                  │
│  Example:                                                       │
│  User says: "add a habit"                                       │
│                                                                  │
│  AI understands:                                                │
│  ├── Create habit entity with proper schema                     │
│  ├── Initialize streak counter (gamification)                   │
│  ├── Set up XP rewards for completion                           │
│  ├── Configure notification reminders                           │
│  ├── Link to habit tracking UI                                  │
│  ├── Emit HABIT_CREATED event via Nervous System               │
│  └── Log to audit trail                                         │
│                                                                  │
│  The brain context module (brain/context/) enables this:        │
│  - ContextLoader: Loads all README.md files                     │
│  - ThinkingBrain: Processes prompts through brain               │
│                                                                  │
│  NEVER take prompts literally. ALWAYS understand deeply.        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation

### For AI Assistants

When you receive a task, follow this protocol:

```python
# Step 1: Load Context
from brain.context import ContextLoader
loader = ContextLoader()
loader.load_all()  # Reads all README.md files

# Step 2: Think Through Brain
from brain.context import ThinkingBrain
brain = ThinkingBrain()
result = brain.think("user's prompt")

# Step 3: Execute via Brain Architecture
from brain.core.brain import Brain
from brain.core.command_event import CommandEvent

core_brain = Brain()
event = CommandEvent(
    command_type=result.suggested_command,
    params=result.suggested_params,
    user_id="current_user"
)
outcome = core_brain.run(event)
```

### For Developers

The brain context module is available at `brain/context/`:

```
brain/context/
├── __init__.py           # Module exports
├── context_loader.py     # README.md loader
├── thinking_brain.py     # Prompt processor
└── README.md             # Documentation
```

---

## Context Priority Order

When loading context, prioritize in this order:

| Priority | File | Purpose |
|----------|------|---------|
| 1 | `README.md` | Main project documentation |
| 2 | `brain/README.md` | Brain system architecture |
| 3 | `PROJECT_RULES.md` | Development guidelines |
| 4 | `brain/core/README.md` | Core brain components |
| 5 | `brain/tools/README.md` | Tool documentation |
| 6 | `brain/design/README.md` | Design specifications |
| 7 | Domain-specific READMEs | Feature-specific docs |

---

## Brain Pathways

The ThinkingBrain maps prompts to brain pathways:

| Pathway | Description | Components |
|---------|-------------|------------|
| Habit Creation | Create habit with gamification | Router, OpsBrain, Cerebellum, NervousSystem |
| Task Creation | Create task with priority | Router, OpsBrain, Cerebellum, NervousSystem |
| Financial Recording | Record transactions | Router, FinanceBrain, Cerebellum, NervousSystem |
| Goal Setting | Set goals with milestones | Router, OpsBrain, Cerebellum, NervousSystem |
| Health Logging | Log health metrics | Router, OpsBrain, Cerebellum, NervousSystem |
| Time Tracking | Track productivity time | Router, OpsBrain, Cerebellum, NervousSystem |
| System Query | Query system data | Router, OpsBrain, FinanceBrain, RelationBrain |
| Brain Process | Generic brain processing | ContextLoader, Router, MetaBrain, Cerebellum |

---

## Intent Categories

The ThinkingBrain recognizes these intents:

| Intent | Keywords | Description |
|--------|----------|-------------|
| CREATE | add, create, new, make, start | Create new entities |
| READ | show, display, list, get, view | View/retrieve data |
| UPDATE | update, edit, modify, change | Modify existing data |
| DELETE | delete, remove, clear, erase | Remove entities |
| QUERY | how many, count, total, sum | Analyze data |
| NAVIGATE | go to, open, switch | Move between views |
| CONFIGURE | configure, settings, setup | Change preferences |
| ANALYZE | analyze, examine, inspect | Deep examination |
| HELP | help, how do i, explain | Documentation/help |

---

## Domain Categories

The ThinkingBrain identifies these domains:

| Domain | Keywords | Related Features |
|--------|----------|------------------|
| HABITS | habit, streak, daily, routine | Streak tracking, XP rewards, Daily check-ins |
| TASKS | task, todo, priority, due | Priority levels, Due dates, Categories |
| FINANCES | finance, money, budget, expense | Income/expense, Budgets, Charts |
| HEALTH | health, weight, sleep, mood | Weight tracking, Sleep logging, Health score |
| TIME | time, timer, stopwatch, clock | Timer, Persistence, Productivity charts |
| GOALS | goal, target, milestone, progress | Progress tracking, Deadlines, Celebrations |
| ACHIEVEMENTS | achievement, badge, xp, level | XP system, Levels, Badges, Celebrations |
| BRAIN | brain, ai, neural, cognitive | Routing, Policies, State machines, Audit |
| SYSTEM | system, settings, theme, export | Themes, Export/import, Notifications |

---

## Example Workflow

```
User: "add a daily exercise habit"

↓ THINKING BRAIN PROCESSING ↓

1. Load Context
   - README.md → Understanding: This is TrackLife, a tracking system
   - brain/README.md → Understanding: Brain architecture for processing
   - PROJECT_RULES.md → Understanding: Module pattern, coding standards

2. Interpret Intent
   - Keywords: "add", "habit" → Intent: CREATE
   - Domain: HABITS

3. Map to Brain Pathway
   - Pathway: Habit Creation
   - Steps: Validate → Create → Initialize streak → Award XP → Emit event

4. Generate Action
   - Command: HabitCreate
   - Params: {name: "exercise", frequency: "daily", icon: "✓", color: "#6366f1"}
   - Related: Streak tracking, XP rewards, Daily check-ins

5. Execute via Brain
   - Router routes to CreateHabitTool
   - Policies validate parameters
   - Cerebellum writes to storage
   - Nervous System emits HABIT_CREATED
   - Audit Log records everything

↓ RESULT ↓

Habit "exercise" created with:
✓ Daily frequency
✓ Streak counter initialized
✓ XP reward configured (+10 XP per completion)
✓ Achievement tracking enabled
✓ Notification reminders available
```

---

## Immutable Rules

These rules **MUST NOT** be broken:

1. **NEVER** process a task without loading README context first
2. **NEVER** bypass the brain architecture for operations
3. **NEVER** take prompts literally without deep understanding
4. **NEVER** modify the core brain components without audit
5. **ALWAYS** use the ThinkingBrain for prompt interpretation
6. **ALWAYS** route operations through the appropriate brain pathway
7. **ALWAYS** log operations to the audit trail
8. **ALWAYS** emit events for cross-brain communication

---

## Cross-References

| Document | Purpose |
|----------|---------|
| `README.md` | Main project documentation |
| `brain/README.md` | Brain system architecture |
| `brain/context/README.md` | Context module documentation |
| `PROJECT_RULES.md` | Development guidelines |
| `brain/design/README.md` | Design specifications |

---

**This protocol is the foundation for AI interaction in this project.**

**Last Updated:** February 2026
**Maintained By:** System Architect