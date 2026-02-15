# 🧩 Chunked Todo System - Implementation Guidelines

**Purpose:** Provide comprehensive guidelines for using the chunked todo system across all project files (.md and .py)

---

## 🎯 Overview

The chunked todo system addresses the problem of AI working on "big chunks of data and processing doing a lot of things at once" by breaking work into manageable 1-3 task chunks with detailed explanations.

### Core Benefits
1. **Reduced cognitive load** - Focus on 1-3 tasks at a time
2. **Better explanations** - Each task includes What, Why, How
3. **Clear progress tracking** - Visual chunk completion
4. **Context preservation** - Boundaries between work sessions
5. **Higher quality output** - Detailed planning before implementation

---

## 📋 System Components

### 1. Templates Directory (`templates/`)
| File | Purpose | Usage Example |
|------|---------|---------------|
| `todo_chunk_template.md` | Detailed chunk planning | New feature implementation |
| `phase_chunk_template.md` | Phase-level organization | Phase 1.1 Habit Score |
| `python_todo_template.py` | Python module todos | Brain module development |
| `brain_todo_guidelines.md` | Brain-specific patterns | AI-native feature development |

### 2. Updated TODO.md
- Added "Chunked Todo System" section
- Restructured Phase 1.1 with chunked approach
- Links to templates and guidelines

### 3. Integration Points
- `.md` files: Use markdown templates
- `.py` files: Use Python template patterns
- Brain modules: Follow brain-specific guidelines

---

## 🛠️ How to Use

### For New Features
1. **Analyze** requirements and break into 1-3 task chunks
2. **Choose** appropriate template based on file type
3. **Fill** template with detailed explanations
4. **Execute** one chunk at a time
5. **Update** status after each chunk

### Example Workflow: Habit Score Implementation
```
1. SELECT Chunk 1: Research & Design (2 tasks)
2. SWITCH to architect mode
3. EXECUTE Task 1: Research algorithm
4. EXECUTE Task 2: Design formula
5. UPDATE status to completed
6. MOVE to Chunk 2: Core Implementation
```

### For Existing Todos
1. **Review** current todo list
2. **Group** related tasks into chunks (1-3 per chunk)
3. **Add** detailed explanations using templates
4. **Prioritize** chunks based on dependencies
5. **Execute** following chunked workflow

---

## 📝 Template Usage Guidelines

### Markdown Files (.md)
**When to use:** TODO.md, phase documentation, feature specs

**Key elements to include:**
1. **Chunk metadata** (ID, status, priority, effort)
2. **Task descriptions** with What, Why, How
3. **File references** (which files will be modified)
4. **Dependencies** (prerequisite chunks/tasks)
5. **Validation criteria** (how to verify completion)

**Example structure:**
```markdown
### Chunk 1: [Chunk Name]
**Status:** `[ ] Planning` / `[-] In Progress` / `[x] Complete`

**Task 1: [Specific task]**
- **What:** [Exactly what needs to be done]
- **Why:** [Purpose and impact]
- **How:** [Step-by-step approach]
- **Files:** [files_to_modify]
- **Validation:** [How to verify]
```

### Python Files (.py)
**When to use:** Brain modules, utility functions, core logic

**Key patterns:**
1. **Module-level todos** at top of file
2. **Function-level todos** within functions
3. **Class-level todos** within class definitions
4. **Status indicators** (TODO, IN_PROGRESS, DONE)

**Example pattern:**
```python
# 🧩 TODO: [Module Name] - Chunked Implementation
# 
# **Chunk 1: Core Structure**
# Tasks:
# 1. [ ] Create module with proper imports
# 2. [ ] Define core classes/functions
# 3. [ ] Add audit logging integration
# 
# **Files:** brain/[module]/[file].py
# **Status:** TODO
```

### Brain Modules
**Additional requirements:**
1. **NO direct database access** - Use Tools only
2. **ALWAYS log to audit** - Every command recorded
3. **ALWAYS validate transitions** - State machines enforced
4. **NO placeholders** - Complete implementations only

**Brain-specific template:** `templates/brain_todo_guidelines.md`

---

## 🔄 Execution Workflow

### Step 1: Planning (Architect Mode)
1. Analyze the task or feature
2. Break into 1-3 task chunks
3. Create detailed plan for first chunk
4. Identify dependencies and required files
5. Document in appropriate template

### Step 2: Implementation (Code Mode)
1. Switch to Code mode
2. Implement first task with detailed explanations
3. Test implementation
4. Update todo status
5. Repeat for remaining tasks in chunk

### Step 3: Validation (Debug Mode if needed)
1. Test edge cases
2. Verify integration points
3. Check for regressions
4. Update documentation

### Step 4: Completion & Transition
1. Mark chunk as complete
2. Review completion checklist
3. Identify next chunk
4. Update progress tracking

---

## 📊 Progress Tracking

### Status Indicators
- `[ ]` - Not started
- `[-]` - In progress
- `[x]` - Completed

### Progress Metrics
- **Chunks completed:** X/Y
- **Tasks completed:** X/Y
- **Time spent:** X hours
- **Next focus:** [Chunk name]

### Example Tracking Section
```markdown
## 📈 Progress Tracking
**Module:** habit_score
**Phase:** 1.1
**Chunks:** 1/3 completed
**Tasks:** 2/7 completed
**Next Focus:** Chunk 2 - Core Implementation
**Last Updated:** 2026-02-15
```

---

## 🧪 Quality Assurance

### Before Starting a Chunk
1. **Scope validation** - Is this truly 1-3 tasks?
2. **Dependency check** - Are prerequisites met?
3. **Resource assessment** - Are all required files accessible?
4. **Time estimation** - Can this be completed in 1-2 hours?

### During Implementation
1. **Explanation quality** - Are What, Why, How clearly documented?
2. **Code quality** - Follows existing patterns and style
3. **Testing** - Includes appropriate tests
4. **Documentation** - Updated as code changes

### After Completion
1. **Verification** - All success criteria met
2. **Integration testing** - Works with existing code
3. **Status update** - Todo marked complete
4. **Knowledge transfer** - Insights documented

---

## 🔍 Example: Habit Score Chunk 1

### Before (Traditional)
```
- [ ] Research Loop's weighted moving average algorithm
- [ ] Design TrackLife's Habit Score formula
```

### After (Chunked)
```
#### Chunk 1: Research & Design (2 tasks)
**Status:** `[-] In Progress`
**Mode:** `architect`

**Task 1: Research Loop's algorithm**
- **What:** Understand exponential decay weighting formula
- **Why:** Foundation for scientific habit scoring
- **How:** Analyze Loop Habit Tracker's algorithm, document insights
- **Files:** `docs/specs/HABIT_SCORE_SPEC.md`
- **Output:** Algorithm summary with formula explanation

**Task 2: Design TrackLife's formula**
- **What:** Adapt algorithm with custom parameters
- **Why:** Create forgiving, accurate habit strength measure
- **How:** Define decayRate (λ=0.05), lookbackDays (60), categories
- **Files:** `docs/specs/HABIT_SCORE_SPEC.md`
- **Output:** Final formula specification
```

---

## 🚀 Getting Started

### For New Contributors
1. Read `PROJECT_RULES.md` for project guidelines
2. Review `TODO.md` for current priorities
3. Examine `templates/` for chunked templates
4. Start with a small chunk (1-2 tasks)
5. Follow the execution workflow

### For AI Assistants
1. Always use chunked approach for todo items
2. Provide detailed explanations for each task
3. Update status after each chunk
4. Reference templates for consistency
5. Document insights and learning points

---

## 📚 Related Documents

| Document | Purpose |
|----------|---------|
| [PROJECT_RULES.md](PROJECT_RULES.md) | Project guidelines and conventions |
| [GETTING_STARTED.md](GETTING_STARTED.md) | Setup and workflow instructions |
| [TODO.md](TODO.md) | Current tasks with chunked examples |
| [templates/](templates/) | All chunked todo templates |

---

## 🔮 Future Enhancements

### Planned Improvements
1. **Automated chunk tracking** - Script to track chunk progress
2. **Time estimation refinement** - Better effort estimation guidelines
3. **Integration with Brain system** - Automated todo updates
4. **Visual progress dashboard** - Chart showing chunk completion

### Feedback Collection
- Monitor implementation quality
- Gather user/AI feedback
- Iterate on templates based on usage
- Update guidelines quarterly

---

*Guidelines version: 1.0 | Created: 2026-02-15 | Last updated: 2026-02-15*
*For use across all TrackLife project files*