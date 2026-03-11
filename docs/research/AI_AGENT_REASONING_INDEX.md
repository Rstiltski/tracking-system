# 🧠 AI Agent Reasoning Index

**Central reference for AI agent reasoning patterns and memory management in the Veryfyn Tracking System.**

**Created:** March 8, 2026 (DECISION_037)
**Last Updated:** March 8, 2026

---

## 🎯 Purpose

This index provides a complete map of all documentation and implementation files related to AI agent reasoning, memory management, and enhanced thinking protocols for AI assistants working on this project.

---

## 📚 Core Documentation

### Primary AI Rules & Protocols

| File | Purpose | Updated |
|------|---------|---------|
| [`brain/AI_RULES.md`](../brain/AI_RULES.md) | **MASTER PROTOCOL** - 4-phase workflow + ReAct pattern | ✅ March 8, 2026 |
| [`AI_START_HERE.md`](../AI_START_HERE.md) | AI entry point - mandatory context loading | ✅ March 8, 2026 |
| [`brain/ai_assistant/README.md`](../brain/ai_assistant/README.md) | AI Assistant Memory Management System | ✅ March 8, 2026 |
| [`docs/research/AI_AND_PREDICTION.md`](../docs/research/AI_AND_PREDICTION.md) | AI research and patterns | ✅ March 8, 2026 |

### Supporting Documentation

| File | Purpose | Status |
|------|---------|--------|
| [`CONTEXT.md`](../CONTEXT.md) | Master context reference | ✅ Current |
| [`brain/CORE_RULES.md`](../brain/CORE_RULES.md) | Immutable project laws (58+ rules) | ✅ Current |
| [`decisions.log`](../decisions.log) | Decision history (37+ entries) | ✅ Current |
| [`NEXT_STEP.md`](../NEXT_STEP.md) | Quick reference for AI assistant | ✅ March 8, 2026 |

---

## 🧠 AI Assistant Memory Management System

### Component Files

| Component | File | Lines | Purpose |
|-----------|------|-------|---------|
| **Module Init** | `brain/ai_assistant/__init__.py` | ~80 | Exports and version info |
| **Memory Manager** | `brain/ai_assistant/memory_manager.py` | ~300 | Compression, retrieval, relevance scoring |
| **Reference Index** | `brain/ai_assistant/reference_index.py` | ~350 | Reference-by-substitution pattern |
| **Task Decomposer** | `brain/ai_assistant/task_decomposer.py` | ~450 | Hierarchical decomposition with templates |
| **Session Context** | `brain/ai_assistant/session_context.py` | ~350 | Sliding window, persistence |

**Total:** ~1,530 lines of Python code

### Auto-Generated Files

| File | Purpose | Created By |
|------|---------|------------|
| `brain/ai_assistant/session_state.json` | Session persistence | SessionContext |
| `brain/ai_assistant/reference_index.json` | Reference cache | ReferenceIndex |

---

## 🔄 ReAct Thinking Pattern (REQUIRED)

**Every AI response MUST show:**

```markdown
🤔 THOUGHT: [What I'm analyzing and why]
📋 ACTION: [What I'm about to do]
👁️ OBSERVATION: [What I found/observed]
💭 REFLECTION: [What this means for next steps]
```

### Research Source
- Yao, S., et al. (2023). "ReAct: Synergizing Reasoning and Acting in Language Models"
- https://arxiv.org/abs/2210.03629

### Implementation
- Enforced in `brain/AI_RULES.md`
- Referenced in `AI_START_HERE.md`
- Documented in `brain/ai_assistant/README.md`

---

## 📊 Memory Protocols

### 1. Sliding Window

**Rule:** Keep last 10 interactions active, summarize older

**Implementation:**
```python
from brain.ai_assistant import SessionContext

context = SessionContext(sliding_window_size=10)
context.add_interaction(role="user", content="Request")
compressed = context.get_compressed_context()
```

**File:** `brain/ai_assistant/session_context.py`

### 2. Intent-Driven Retrieval

**Rule:** Load only memories relevant to current goal

**Implementation:**
```python
from brain.ai_assistant import MemoryManager

memory = MemoryManager()
relevant = memory.get_relevant_decisions(
    intent="Adding new brain component",
    max_results=5
)
```

**File:** `brain/ai_assistant/memory_manager.py`

### 3. Reference-by-Substitution

**Rule:** Use lightweight IDs for large files, load content on-demand

**Implementation:**
```python
from brain.ai_assistant import ReferenceIndex

index = ReferenceIndex()
ref_id = index.create_reference(
    file_path="brain/core/brain.py",
    description="Main brain entry point - 658 lines"
)
# Later, load only when needed
content = index.load_reference(ref_id)
```

**File:** `brain/ai_assistant/reference_index.py`

### 4. Timestamp Decay

**Rule:** Apply decay factor to older memories

**Formula:**
```python
decay_factor = 0.5 ** (age.total_seconds() / half_life.total_seconds())
# half_life = 24 hours
```

**Implementation:** `brain/ai_assistant/memory_manager.py` - `_calculate_relevance()`

---

## 📋 Task Decomposition

### Built-in Templates

| Template | Keywords | Subtasks | File |
|----------|----------|----------|------|
| Feature Addition | add, create, implement, new | 8 | `task_decomposer.py` |
| Bug Fix | fix, bug, error, issue | 6 | `task_decomposer.py` |
| Analysis | analyze, review, examine, audit | 5 | `task_decomposer.py` |
| Refactoring | refactor, restructure, reorganize | 6 | `task_decomposer.py` |
| Documentation | document, write docs, update readme | 5 | `task_decomposer.py` |

### Usage Example

```python
from brain.ai_assistant import TaskDecomposer

decomposer = TaskDecomposer()
task_tree = decomposer.decompose(
    request="Add new correlation analysis feature",
    max_depth=3
)

# Get ordered tasks (respecting dependencies)
for task_id in task_tree.get_ordered_tasks():
    node = task_tree.get_node(task_id)
    print(f"- {node.description} (priority: {node.priority.value})")
```

### Example Output

```
Task Tree: Add new correlation analysis feature
├── 1. Analyze existing patterns (priority: critical)
├── 2. Define data models (priority: high, dep: 1)
├── 3. Define tools/APIs (priority: high, dep: 2)
├── 4. Implement core logic (priority: high, dep: 3)
├── 5. Create UI components (priority: medium, dep: 2)
├── 6. Write tests (priority: high, dep: 4)
├── 7. Update documentation (priority: medium, dep: 4, 5)
└── 8. Validate and test (priority: critical, dep: 6, 7)
```

---

## 🧩 Integration with 5-File Memory

The AI Assistant Memory Management System enhances the existing 5-file memory protocol:

| 5-File Memory | Enhancement | Implementation |
|---------------|-------------|----------------|
| **ACTIVE PROMPT** | SessionContext manages sliding window | `session_context.py` |
| **SESSION STATE** | SessionContext persists to JSON | `session_context.py` + `session_state.json` |
| **DECISION LOG** | MemoryManager reads, compresses, retrieves | `memory_manager.py` + `decisions.log` |
| **PRIME DIRECTIVE** | ReferenceIndex stores lightweight references | `reference_index.py` + `.context.md` |
| **PATTERN LIBRARY** | TaskDecomposer applies templates | `task_decomposer.py` + `patterns/` |

---

## 📖 Decision Logging Protocol

**ALWAYS log decisions:**

```python
from brain.ai_assistant.memory_manager import log_decision

log_decision(
    choice="Using pattern X",
    reasoning="Matches existing architecture per DECISION_030",
    implication="Consistent with MOD_001 single-page rule",
    summary="Applied navigation pattern from DECISION_030"
)
```

**Format in decisions.log:**
```markdown
## DECISION_XXX: [Summary]

**Date:** [ISO timestamp]
**Status:** IMPLEMENTED

### Summary
[Brief description]

### Details
[Choice] -> [Reasoning] -> [Implication]
```

**Related:** DECISION_037 - AI Assistant Memory Management System Created

---

## 🔗 Cross-Reference Map

### AI Rules & Protocols
```
AI_START_HERE.md
    ↓
brain/AI_RULES.md (ReAct + 4-phase workflow)
    ↓
brain/ai_assistant/README.md (Memory management)
    ↓
docs/research/AI_AND_PREDICTION.md (Research context)
```

### Implementation Flow
```
User Request
    ↓
SessionContext.load_session()
    ↓
MemoryManager.get_relevant_decisions(intent)
    ↓
TaskDecomposer.decompose(request)
    ↓
ReAct Loop (Thought→Action→Observation→Reflection)
    ↓
MemoryManager.log_decision()
    ↓
SessionContext.save_session()
```

### File Dependencies
```
brain/ai_assistant/__init__.py
    ├── memory_manager.py
    ├── reference_index.py
    ├── task_decomposer.py
    └── session_context.py

Auto-generated:
    ├── session_state.json
    └── reference_index.json
```

---

## ✅ Checklist for AI Assistants

### Before Responding to User

- [ ] Load session context: `SessionContext()`
- [ ] Retrieve relevant decisions: `MemoryManager.get_relevant_decisions(intent)`
- [ ] Decompose complex requests: `TaskDecomposer.decompose(request)`
- [ ] Check references: `ReferenceIndex.find_references(tags)`
- [ ] Show ReAct thinking pattern

### During Task Execution

- [ ] Update sliding window: `context.add_interaction()`
- [ ] Log decisions: `memory.log_decision()`
- [ ] Track task progress: `tree.update_task_status()`

### After Completing Task

- [ ] Compress context: `context.compress_old_interactions()`
- [ ] Store reflexion: `memory.store_reflection()`
- [ ] Save session: `context._save_session()`

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Total Documentation Files | 4 (AI_RULES, AI_START_HERE, AI_AND_PREDICTION, AI_AGENT_REASONING_INDEX) |
| Total Implementation Files | 5 (__init__, memory_manager, reference_index, task_decomposer, session_context) |
| Total Lines of Code | ~1,530 |
| AI Agent Patterns | 6 (ReAct, Memory Compression, Reference-by-Substitution, Intent-Driven Retrieval, Hierarchical Decomposition, Stateful Memory) |
| Decision Log Entries | 37+ (DECISION_001 - DECISION_037) |
| Task Templates | 5 (Feature, Bug Fix, Analysis, Refactoring, Documentation) |

---

## 🎓 Training Resources

### For New AI Assistants

1. **Start Here:** `AI_START_HERE.md` - Load mandatory context
2. **Learn Protocol:** `brain/AI_RULES.md` - 4-phase workflow + ReAct
3. **Understand Memory:** `brain/ai_assistant/README.md` - Memory management system
4. **Review Research:** `docs/research/AI_AND_PREDICTION.md` - AI patterns and research
5. **Quick Reference:** `NEXT_STEP.md` - Practical usage guide

### For Human Developers

1. **Overview:** `brain/ai_assistant/README.md` - What the system does
2. **Implementation:** Individual `.py` files in `brain/ai_assistant/`
3. **Decision:** DECISION_037 in `decisions.log` - Why it was created
4. **Usage:** This file - How AI assistants use the system

---

## 🔮 Future Enhancements

### Potential Additions

| Enhancement | Priority | Complexity | Notes |
|-------------|----------|------------|-------|
| Multi-session memory sharing | Low | High | Cross-conversation learning |
| LLM-based summarization | Medium | Medium | Better context compression |
| Semantic search for decisions | Medium | Medium | Embedding-based retrieval |
| Custom decomposition templates | Low | Low | User-defined task patterns |
| Reflexion storage | Medium | Low | Store lessons learned |

### Research Integration

| Research Area | Status | Notes |
|---------------|--------|-------|
| ReAct Pattern | ✅ Implemented | Yao et al. (2023) |
| Memory Compression | ✅ Implemented | AI Agent Research |
| Task Decomposition | ✅ Implemented | Wang et al. (2023) |
| Reflexion | 🟡 Partial | Shinn et al. (2023) - needs enhancement |
| Multi-Agent Collaboration | ❌ Not implemented | Chen et al. (2023) |
| Tool Learning | ❌ Not implemented | Schick et al. (2023) |

---

**Last Updated:** March 8, 2026
**Maintained By:** AI Assistant (Rigorous Architect Protocol)
**Version:** 1.0.0

---

## 📁 Related Files

| File | Purpose |
|------|---------|
| [`brain/AI_RULES.md`](../brain/AI_RULES.md) | Master AI protocol |
| [`AI_START_HERE.md`](../AI_START_HERE.md) | AI entry point |
| [`brain/ai_assistant/README.md`](../brain/ai_assistant/README.md) | Memory management docs |
| [`docs/research/AI_AND_PREDICTION.md`](../docs/research/AI_AND_PREDICTION.md) | AI research |
| [`decisions.log`](../decisions.log) | Decision history |
| [`NEXT_STEP.md`](../NEXT_STEP.md) | Quick reference |
