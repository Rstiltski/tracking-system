# 🧠 Brain Context Module - The Thinking Layer

**The bridge between simple prompts and deep understanding.**

---

## TABLE OF CONTENTS

| # | Section | Key Info |
|---|---------|----------|
| 1 | Overview | What is the Context Module? |
| 2 | Architecture | How it works |
| 3 | Components | Module breakdown |
| 4 | Usage | How to use it |
| 5 | Brain Context Protocol | The rules |
| 6 | Examples | Practical examples |

---

## §1 Overview

The Brain Context Module is the **thinking layer** that connects AI assistants to the brain system's architecture. It ensures that:

- **README.md files are always referenced** for context
- **The brain folder is used as the thinking process**
- **Simple prompts yield deep understanding** through brain architecture

### Core Principle

```
Simple Prompt → Context Loading → Brain Processing → Deep Understanding
     "add habit"    README.md files    ThinkingBrain    Full gamification context
```

---

## §2 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    THINKING BRAIN                                │
│                  (Context Processor)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. LOAD CONTEXT                                                 │
│     └── ContextLoader → All README.md files                      │
│                                                                  │
│  2. INTERPRET INTENT                                             │
│     └── Parse prompt → Identify domain & action                  │
│                                                                  │
│  3. MAP TO BRAIN                                                 │
│     └── Find brain pathway for execution                         │
│                                                                  │
│  4. GENERATE RESPONSE                                            │
│     └── Return action with reasoning                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## §3 Components

### ContextLoader (`context_loader.py`)

Loads and manages README.md context files.

**Features:**
- Finds all README.md files in the project
- Loads content as structured context
- Provides search across all documentation
- Prioritizes important files (main README, brain README, PROJECT_RULES)

**Usage:**
```python
from brain.context import ContextLoader

loader = ContextLoader()

# Load all README files
contexts = loader.load_all()

# Get specific context
brain_readme = loader.get("brain/README.md")

# Search across all READMEs
results = loader.search("habit")

# Get full context string for AI
full_context = loader.get_full_context()
```

### ThinkingBrain (`thinking_brain.py`)

Processes simple prompts through the brain architecture.

**Features:**
- Interprets user intent (create, read, update, delete, etc.)
- Identifies domain (habits, tasks, finances, etc.)
- Maps to brain pathways
- Generates detailed reasoning

**Usage:**
```python
from brain.context import ThinkingBrain

brain = ThinkingBrain()

# Process a simple prompt
result = brain.think("add a habit")

print(f"Intent: {result.interpreted_intent}")
print(f"Domain: {result.identified_domain}")
print(f"Action: {result.action}")
print(f"Reasoning: {result.reasoning}")
```

---

## §4 Usage

### Basic Usage

```python
from brain.context import ThinkingBrain, ContextLoader

# Quick thinking
from brain.context import think
result = think("add a habit")

# Get thinking trace
from brain.context import get_thinking_trace
trace = get_thinking_trace("show my finances")
print(trace)
```

### Integration with Brain System

```python
from brain.context import ThinkingBrain
from brain.core.brain import Brain
from brain.core.command_event import CommandEvent

# Initialize
thinking_brain = ThinkingBrain()
brain = Brain()

# Process user prompt
result = thinking_brain.think("create a new habit called Exercise")

if result.suggested_command:
    # Create command event
    event = CommandEvent(
        command_type=result.suggested_command,
        params=result.suggested_params,
        user_id="user123"
    )
    
    # Execute through brain
    brain_result = brain.run(event)
```

---

## §5 Brain Context Protocol

The Brain Context Protocol defines the rules for AI interaction:

### Rule 1: README.md Files Are Source of Truth

```
ALWAYS read README.md files before processing any task.
The READMEs contain:
- Project architecture
- Feature documentation
- Coding standards
- Brain system design
```

### Rule 2: Brain Folder Is the Thinking Process

```
ALWAYS use the brain folder architecture for processing:
- Router: Routes commands
- Policies: Validates operations
- State Machines: Manages entity lifecycle
- Tools: Executes operations
- Cerebellum: Coordinates writes
- Nervous System: Event communication
```

### Rule 3: Simple Prompts → Deep Understanding

```
User gives: "add a habit"
AI understands:
- Create habit entity
- Initialize streak counter
- Set up gamification (XP, achievements)
- Configure notification reminders
- Link to habit tracking UI
```

### Priority Order for Context Loading

1. `README.md` - Main project documentation
2. `brain/README.md` - Brain system architecture
3. `PROJECT_RULES.md` - Development guidelines
4. `brain/core/README.md` - Core brain components
5. `brain/tools/README.md` - Tool documentation
6. `brain/design/README.md` - Design specifications

---

## §6 Examples

### Example 1: Creating a Habit

```python
>>> from brain.context import think
>>> result = think("add a daily exercise habit")

>>> print(result.interpreted_intent)
IntentCategory.CREATE

>>> print(result.identified_domain)
Domain.HABITS

>>> print(result.suggested_command)
HabitCreate

>>> print(result.related_features)
['Streak tracking', 'XP rewards for completion', 'Daily check-ins', ...]
```

### Example 2: Querying Finances

```python
>>> result = think("show my expenses this month")

>>> print(result.interpreted_intent)
IntentCategory.READ

>>> print(result.identified_domain)
Domain.FINANCES

>>> print(result.brain_pathway)
System Query
```

### Example 3: Getting Full Thinking Trace

```python
>>> from brain.context import get_thinking_trace
>>> print(get_thinking_trace("track my sleep"))

============================================================
THINKING BRAIN - PROCESSING TRACE
============================================================

Input: 'track my sleep'

## Context Loading
Loaded 3 README files for context:
  - README.md
  - brain/README.md
  - PROJECT_RULES.md

## Intent Analysis
Detected intent: **create**
This indicates the user wants to create something new.

## Domain Identification
Identified domain: **health**
This relates to the health module of the tracking system.

## Brain Pathway
Selected pathway: **Health Logging**
Log health metrics

Processing steps:
  1. Validate health data
  2. Calculate health score
  3. Update trends
  4. Store entry
  5. Emit HEALTH_LOGGED event

Brain components involved:
  - Router
  - OpsBrain
  - Cerebellum
  - NervousSystem

## Conclusion
The prompt 'track my sleep' has been interpreted as a **create**
operation in the **health** domain.

============================================================
RESULT
============================================================

Intent: create
Domain: health
Confidence: 90%

Action:
Intent: create
Domain: health
Action: Log health metrics

Suggested Command: HealthLog
Parameters: {
  "weight": null,
  "sleepHours": null,
  "mood": "good"
}

Related Features:
  - Weight tracking
  - Sleep logging
  - Mood tracking
  - Health score calculation
  - Trend visualization
```

---

## Cross-References

| If you need... | Read this file |
|----------------|---------------|
| AI entry point | `AI_START_HERE.md` |
| Main project docs | `README.md` |
| Brain system docs | `brain/README.md` |
| Project rules | `PROJECT_RULES.md` |
| Core brain docs | `brain/core/README.md` |
| Security protocols | `brain/SECURITY_PLAYBOOK.md` |
| Tool contracts | `brain/design/04_tool_contracts.md` |

---

**Last Updated:** February 2026
**Maintained By:** System Architect