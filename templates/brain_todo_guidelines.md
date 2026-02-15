# 🧠 Brain Module Todo Guidelines - Chunked Approach

**Purpose:** Provide AI-native todo patterns for Brain system modules with detailed explanations and chunked execution

---

## 🎯 Core Principles

### Chunked Execution
1. **Work in 1-3 task chunks** per execution session
2. **Each chunk should be completable** in 1-2 hours
3. **Clear boundaries** between chunks
4. **Detailed explanations** for each task

### Brain-Specific Requirements
- **NO direct database access** - Use Tools only
- **ALWAYS log to audit** - Every command recorded
- **ALWAYS validate transitions** - State machines enforced
- **NO placeholders** - Complete implementations only
- **Follow existing patterns** - Consistency across modules

---

## 📋 Template Usage

### For New Brain Modules
```python
# 🧩 TODO: [Module Name] - Chunked Implementation
# 
# **Phase:** [Phase Name]
# **Chunk:** 1/3
# **Priority:** High
# 
# **Task 1: Core Module Structure**
# Status: TODO
# Files: brain/[module]/__init__.py, brain/[module]/[file].py
# Dependencies: None
# 
# **Detailed Plan:**
# 1. Create module directory with __init__.py
# 2. Define core classes with proper docstrings
# 3. Add audit logging integration
# 4. Register module in brain/__init__.py
# 
# **Code Pattern:**
# ```python
# from brain.core.command_event import CommandEvent
# from brain.core.result import BrainResult
# import logging
# 
# logger = logging.getLogger(__name__)
# 
# class NewModule:
#     """Module purpose"""
#     pass
# ```
# 
# **Task 2: Tool Integration**
# Status: TODO
# Files: brain/tools/[tool_file].py, brain/core/contracts.py
# Dependencies: Task 1 completion
# 
# **Detailed Plan:**
# 1. Create tool functions with proper signatures
# 2. Register tools in ToolRegistry
# 3. Implement tool contracts
# 4. Add error handling
# 
# **Validation:**
# - [ ] Tools appear in registry
# - [ ] Commands execute without errors
# - [ ] Audit logs contain tool usage
```

### For Module Enhancements
```python
# 🧩 TODO: Enhance [Existing Module] - Chunked Approach
# 
# **Chunk 1: Add New Feature**
# Tasks:
# 1. [ ] Design feature architecture
# 2. [ ] Implement core logic
# 3. [ ] Add tests
# 
# **Chunk 2: Integration**
# Tasks:
# 1. [ ] Update existing functions
# 2. [ ] Modify state transitions
# 3. [ ] Update documentation
# 
# **Chunk 3: Validation**
# Tasks:
# 1. [ ] Run existing tests
# 2. [ ] Test edge cases
# 3. [ ] Verify audit logs
```

---

## 🛠️ Implementation Workflow

### Step 1: Planning (Architect Mode)
1. Analyze requirements
2. Break into 1-3 task chunks
3. Create detailed plan for first chunk
4. Identify dependencies and files

### Step 2: Execution (Code Mode)
1. Switch to Code mode
2. Implement first task with detailed explanations
3. Test implementation
4. Update todo status

### Step 3: Validation (Debug Mode)
1. Switch to Debug mode if needed
2. Test edge cases
3. Verify integration points
4. Update documentation

### Step 4: Completion
1. Mark chunk as complete
2. Move to next chunk
3. Update progress tracking

---

## 📊 Progress Tracking

### Chunk Status Indicators
- `[ ]` Not started
- `[-]` In progress
- `[x]` Completed

### Example Progress Tracking
```
**Module: habit_score**
**Phase: 1.1**
**Chunks:** 2/4 completed
**Tasks:** 5/8 completed
**Next Focus:** Chunk 3 - Visualization
```

---

## 🧪 Testing Strategy

### Unit Tests (Per Chunk)
- Test core logic
- Mock dependencies
- Verify edge cases

### Integration Tests (After Chunk Completion)
- Test with real tools
- Verify state transitions
- Check audit logs

### Brain-Specific Tests
- Tool registration
- Command execution
- Policy enforcement
- State machine validation

---

## 📝 Documentation Requirements

### Per Chunk Documentation
1. **What changed** - Brief description
2. **Why changed** - Purpose and impact
3. **How to use** - Usage examples
4. **Integration points** - Other modules affected

### File Updates Required
- Module docstrings
- README.md updates
- API documentation
- Example usage

---

## 🔄 Example: Habit Score Implementation

### Chunk 1: Research & Design (2 tasks)
```
**Task 1: Research Loop's algorithm**
What: Understand weighted moving average formula
Why: Foundation for habit score implementation
How: Read documentation, analyze formula
Files: docs/specs/HABIT_SCORE_SPEC.md
Output: Summary of algorithm

**Task 2: Design TrackLife's formula**
What: Adapt algorithm to TrackLife's needs
Why: Customize for our use case
How: Modify parameters, define defaults
Files: docs/specs/HABIT_SCORE_SPEC.md
Output: Final formula specification
```

### Chunk 2: Core Implementation (3 tasks)
```
**Task 1: Create habit-score.js module**
What: Implement calculate() function
Why: Core calculation logic
How: JavaScript implementation of formula
Files: js/habit-score.js
Output: Working calculate() function

**Task 2: Add getCategory() function**
What: Map scores to categories (Excellent, Strong, etc.)
Why: User-friendly display
How: Switch statement with thresholds
Files: js/habit-score.js
Output: Category mapping function

**Task 3: Write tests**
What: Unit tests for calculation
Why: Ensure correctness
How: Jest tests with various scenarios
Files: js/tests/habit-score.test.js
Output: Passing test suite
```

### Chunk 3: Integration (2 tasks)
```
**Task 1: Update habits.js**
What: Replace streak display with habit score
Why: User-facing feature
How: Modify createHabitCard() function
Files: js/habits.js
Output: Updated UI showing scores

**Task 2: Add visualization**
What: Visual score indicator
Why: Better user experience
How: CSS ring visualization
Files: css/styles.css, js/habits.js
Output: Visual score display
```

---

## 🚀 Getting Started

1. **Choose a module** to implement or enhance
2. **Break it down** into 1-3 task chunks
3. **Use templates** for consistent structure
4. **Follow workflow** for each chunk
5. **Track progress** and update status

---

*Guidelines version: 1.0 | For use with Brain system modules*