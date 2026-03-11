# 🧠 AI Assistant Memory Management System

**Purpose:** Enhanced memory and reasoning infrastructure for the AI assistant working on this project.

**Important:** These components are used BY the AI assistant during development sessions. They are NOT part of the runtime tracking application.

---

## Overview

This directory contains utilities that help the AI assistant manage context, memory, and complex task decomposition while working on the Veryfyn Tracking System.

Based on AI agent research (2024-2025), these components implement:
- Memory compression and forgetting strategies
- Reference-by-substitution for large code blocks
- Intent-driven retrieval
- Hierarchical task decomposition

---

## Architecture

```
brain/ai_assistant/
├── README.md                 # This file
├── memory_manager.py         # Memory compression & retrieval
├── reference_index.py        # Code block reference system
├── task_decomposer.py        # Hierarchical task breakdown
└── session_context.py        # Active session state management
```

---

## Components

### 1. Memory Manager (`memory_manager.py`)

**Purpose:** Compress and retrieve decision history efficiently.

**Features:**
- Summarizes `decisions.log` entries
- Implements relevance scoring
- Applies timestamp decay for older entries
- Intent-driven retrieval based on current task

**Usage by AI:**
```python
from brain.ai_assistant.memory_manager import MemoryManager

memory = MemoryManager()

# Get relevant decisions for current task
relevant = memory.get_relevant_decisions(
    intent="Adding new brain component",
    max_results=5
)

# Get compressed summary of recent activity
summary = memory.get_recent_summary(hours=24)
```

---

### 2. Reference Index (`reference_index.py`)

**Purpose:** Lightweight references to large code blocks (reference-by-substitution).

**Features:**
- Creates unique IDs for code files/blocks
- Stores metadata without loading full content
- Lazy loading when full content needed

**Usage by AI:**
```python
from brain.ai_assistant.reference_index import ReferenceIndex

index = ReferenceIndex()

# Create reference (stores ID, not full content)
ref_id = index.create_reference(
    file_path="brain/core/brain.py",
    description="Main brain entry point - 658 lines"
)

# Later: Load full content only when needed
content = index.load_reference(ref_id)
```

---

### 3. Task Decomposer (`task_decomposer.py`)

**Purpose:** Break complex requests into hierarchical subtasks.

**Features:**
- Creates task trees with dependencies
- Estimates complexity per subtask
- Tracks completion status

**Usage by AI:**
```python
from brain.ai_assistant.task_decomposer import TaskDecomposer

decomposer = TaskDecomposer()

# Decompose complex request
task_tree = decomposer.decompose(
    request="Add new correlation analysis feature",
    max_depth=3
)

# Get ordered subtasks
subtasks = task_tree.get_ordered_tasks()
```

---

### 4. Session Context (`session_context.py`)

**Purpose:** Manage active session state and working memory.

**Features:**
- Sliding window for recent interactions
- Context summarization
- Session persistence across conversations

**Usage by AI:**
```python
from brain.ai_assistant.session_context import SessionContext

context = SessionContext()

# Add interaction to sliding window
context.add_interaction(role="user", content="Add new feature")
context.add_interaction(role="assistant", content="Analyzing request...")

# Get compressed context for next turn
compressed = context.get_compressed_context()
```

---

## Integration with 5-File Memory

These components enhance the existing 5-file memory protocol:

| 5-File Memory | Enhancement |
|---------------|-------------|
| **ACTIVE PROMPT** | `session_context.py` manages sliding window |
| **SESSION STATE** | `session_context.py` persists across sessions |
| **DECISION LOG** | `memory_manager.py` compresses and retrieves |
| **PRIME DIRECTIVE** | `reference_index.py` stores lightweight references |
| **PATTERN LIBRARY** | `task_decomposer.py` applies patterns to subtasks |

---

## Memory Compression Strategy

### Sliding Window
- Keep last 10 interactions in active memory
- Summarize interactions 11-50
- Archive interactions 51+ with timestamp decay

### Relevance Scoring
When retrieving memories:
```
relevance_score = (
    keyword_match * 0.4 +
    intent_match * 0.3 +
    recency * 0.2 +
    decision_impact * 0.1
)
```

### Forgetting Policy
| Age | Action |
|-----|--------|
| < 1 hour | Keep in active memory |
| 1-24 hours | Summarize to key points |
| 1-7 days | Store with decay factor 0.5 |
| > 7 days | Archive, retrieve only on high relevance |

---

## Task Decomposition Patterns

### Pattern 1: Feature Addition
```
Add Feature X
├── 1. Analyze existing patterns
│   ├── 1a. Check FEATURE_MAP.md
│   └── 1b. Review similar features
├── 2. Create implementation plan
│   ├── 2a. Define models
│   ├── 2b. Define tools
│   └── 2c. Define UI components
├── 3. Implement
│   ├── 3a. Create models
│   ├── 3b. Create tools
│   └── 3c. Create UI
└── 4. Validate
    ├── 4a. Run tests
    └── 4b. Update documentation
```

### Pattern 2: Bug Fix
```
Fix Bug X
├── 1. Reproduce issue
├── 2. Diagnose root cause
│   ├── 2a. Scan related files
│   └── 2b. Check recent changes
├── 3. Plan fix
│   ├── 3a. Identify files to modify
│   └── 3b. Define validation criteria
├── 4. Implement fix
└── 5. Verify fix
    ├── 5a. Run tests
    └── 5b. Check for regressions
```

---

## AI Usage Protocol

### Before Responding to User

1. **Load Context**
   ```python
   context = SessionContext()
   context.load_session()
   ```

2. **Retrieve Relevant Memories**
   ```python
   memory = MemoryManager()
   relevant = memory.get_relevant_decisions(intent=user_request)
   ```

3. **Decompose Request** (if complex)
   ```python
   decomposer = TaskDecomposer()
   task_tree = decomposer.decompose(user_request)
   ```

4. **Check References** (for large files)
   ```python
   index = ReferenceIndex()
   refs = index.find_references(tags=["brain", "core"])
   ```

### During Task Execution

1. **Update Sliding Window**
   ```python
   context.add_interaction(role="assistant", content="Working on step 2a...")
   ```

2. **Log Decision**
   ```python
   memory.log_decision(
       choice="Using pattern X",
       reasoning="Matches existing architecture",
       implication="Consistent with DECISION_030"
   )
   ```

### After Completing Task

1. **Compress Context**
   ```python
   summary = context.compress_session()
   ```

2. **Reflexion**
   ```python
   reflection = {
       "what_worked": "...",
       "what_to_improve": "...",
       "pattern_learned": "..."
   }
   memory.store_reflection(reflection)
   ```

---

## Example: AI Session Flow

```
User: "Add a new correlation analysis between habits and sleep"

AI Thinking Process:
1. 🧠 SessionContext.load_session() → Load recent context
2. 🔍 MemoryManager.get_relevant_decisions("correlation analysis")
   → Found DECISION_029: Correlation Engine implementation
3. 📋 TaskDecomposer.decompose("Add correlation analysis")
   → Task tree with 8 subtasks
4. 📎 ReferenceIndex.find_references(tags=["correlation", "analysis"])
   → Found refs to brain/analysis/correlation.py
5. ✅ Execute subtask 1a: Check existing patterns
6. 📝 Log decision: "Extending existing correlation engine"
7. 🔁 Continue with remaining subtasks
8. 🪞 Store reflexion: "Pattern: Always check existing features first"
```

---

## Files Modified/Created

| File | Type | Purpose |
|------|------|---------|
| `brain/ai_assistant/README.md` | Created | This documentation |
| `brain/ai_assistant/memory_manager.py` | Created | Memory compression & retrieval |
| `brain/ai_assistant/reference_index.py` | Created | Code block references |
| `brain/ai_assistant/task_decomposer.py` | Created | Task hierarchy creation |
| `brain/ai_assistant/session_context.py` | Created | Session state management |

---

## Relationship to Brain System

**Important Distinction:**

| Brain System | AI Assistant Memory |
|--------------|---------------------|
| Runtime component | Development-time tool |
| Used by application | Used by AI during sessions |
| Persists in production | Not deployed to production |
| Handles user commands | Handles development tasks |

The AI assistant memory system **reads from** but **does not modify** the brain system during normal operation.

---

**Last Updated:** March 8, 2026
**Version:** 1.0.0
**Maintained By:** AI Assistant (Rigorous Architect Protocol)
