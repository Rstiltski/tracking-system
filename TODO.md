# 📋 TrackLife - TODO List

**Task tracking for the TrackLife Enhancement Roadmap.**

---

## 🧭 Quick Navigation

| Want to... | Go to... |
|------------|----------|
| **Get started** | [GETTING_STARTED.md](GETTING_STARTED.md) |
| **Understand rules** | [PROJECT_RULES.md](PROJECT_RULES.md) |
| **Find features** | [FEATURE_MAP.md](FEATURE_MAP.md) |
| **See research** | [docs/research/](docs/research/) |
| **Use chunked templates** | [templates/](templates/) |

---

## 🧩 New: Chunked Todo System

**Purpose:** Work in small, manageable chunks (1-3 tasks) with detailed explanations

### Key Principles
1. **Chunked Execution** - Focus on 1-3 tasks at a time
2. **Detailed Explanations** - Each task includes What, Why, How
3. **Progressive Disclosure** - Start high-level, drill to specifics
4. **Context Preservation** - Clear boundaries between chunks

### Templates Available
| Template | Purpose |
|----------|---------|
| [todo_chunk_template.md](templates/todo_chunk_template.md) | Detailed chunk planning |
| [phase_chunk_template.md](templates/phase_chunk_template.md) | Phase-level chunk organization |
| [python_todo_template.py](templates/python_todo_template.py) | Python module todos |
| [brain_todo_guidelines.md](templates/brain_todo_guidelines.md) | Brain-specific guidelines |

### Workflow
1. **Select** 1 chunk (1-3 tasks) to work on
2. **Switch** to appropriate mode (architect/code/debug)
3. **Execute** with detailed explanations
4. **Update** status and move to next chunk

---

## 📚 Roadmap Documents

| Document | Description |
|----------|-------------|
| [ENHANCEMENT_ROADMAP.md](ENHANCEMENT_ROADMAP.md) | Master enhancement plan |
| [ROADMAP.md](ROADMAP.md) | Historical roadmap (archived) |
| [BRAIN_DEVELOPMENT_ROADMAP.md](BRAIN_DEVELOPMENT_ROADMAP.md) | Brain system development |

---

## ✅ Documentation Updates Complete

**Status:** ✅ Complete  
**Completed:** February 2026

### Documentation Structure
- [x] Create `docs/research/` directory with 5 research documents
- [x] Create `phases/` directory with Phase 1 documentation
- [x] Create `docs/specs/` with HABIT_SCORE_SPEC.md
- [x] Create `docs/schemas/` with EVENT_SCHEMA.md
- [x] Create `docs/guides/` with INDEXEDDB_MIGRATION.md

### LLM Operational Guide Integration
- [x] Update `PROJECT_RULES.md` with complete LLM Operational Guide
- [x] Create `GETTING_STARTED.md` with workflow instructions
- [x] Update `README.md` with navigation and LLM guide
- [x] Update `FEATURE_MAP.md` with documentation structure
- [x] Update `brain/README.md` with LLM guide for Brain module
- [x] Update `brain/__init__.py` with LLM docstring
- [x] Update `brain/core/__init__.py` with LLM docstring

---

## 🎯 Current Phase: Phase 1 - Foundation Strengthening

**Status:** 🔵 Not Started (Status corrected - see IMPLEMENTATION_GAP_ANALYSIS.md)
**Duration:** 2 weeks
**Details:** [phases/PHASE_1_FOUNDATION.md](phases/PHASE_1_FOUNDATION.md)

**⚠️ Note:** Previous status markers were incorrect. Documentation/specs exist but code is not implemented.

### Phase 1.1: Habit Score Algorithm
**Priority:** High | **Effort:** Low | **Duration:** 2-3 days

**Implementation Strategy:** Chunked approach (3 chunks, 1-3 tasks each)

#### Chunk 1: Research & Design (2 tasks)
**Status:** ✅ Complete
**Mode:** `architect`
**Tasks:**
1. [x] **Research Loop's weighted moving average algorithm**
   - **What:** Understand the exponential decay weighting formula
   - **Why:** Foundation for scientific habit scoring
   - **How:** Analyze Loop Habit Tracker's algorithm, document key insights
   - **Files:** `docs/specs/HABIT_SCORE_SPEC.md`, research notes
   - **Output:** Algorithm summary with formula explanation

2. [x] **Design TrackLife's Habit Score formula**
   - **What:** Adapt algorithm to TrackLife's needs with custom parameters
   - **Why:** Create a forgiving, accurate habit strength measure
   - **How:** Define decayRate (λ=0.05), lookbackDays (60), score categories
   - **Files:** `docs/specs/HABIT_SCORE_SPEC.md`
   - **Output:** Final formula specification with default values

#### Chunk 2: Core Implementation (3 tasks)
**Status:** 🔵 Not Started
**Mode:** `code`
**Tasks:**
1. [ ] **Create `js/habit-score.js` module**
   - **What:** Implement calculate(), getPercentage(), getCategory() functions
   - **Why:** Core calculation logic for habit scores
   - **How:** JavaScript implementation of weighted moving average
   - **Files:** `js/habit-score.js`, `js/tests/habit-score.test.js`
   - **Output:** Working module with basic functionality

2. [ ] **Add Habit Score visualization to UI**
   - **What:** Visual score indicator (colored ring, percentage display)
   - **Why:** User-friendly representation of habit strength
   - **How:** CSS ring visualization, update habit card template
   - **Files:** `css/styles.css`, `js/habits.js`
   - **Output:** Visual score display in habit cards

3. [ ] **Write tests for Habit Score calculation**
   - **What:** Unit tests for edge cases and correctness
   - **Why:** Ensure algorithm works correctly
   - **How:** Jest tests with various completion patterns
   - **Files:** `js/tests/habit-score.test.js`
   - **Output:** Passing test suite with 90%+ coverage

#### Chunk 3: Integration & Polish (2 tasks)
**Status:** 🔵 Not Started
**Mode:** `code`
**Tasks:**
1. [ ] **Update `js/habits.js` to use Habit Score**
   - **What:** Replace streak display with habit score in UI
   - **Why:** User-facing feature improvement
   - **How:** Modify createHabitCard() function, update storage
   - **Files:** `js/habits.js`, `js/storage.js`
   - **Output:** Updated UI showing scores instead of binary streaks

2. [ ] **Add advanced features (optional)**
   - **What:** Score history tracking, trend analysis
   - **Why:** Deeper insights into habit development
   - **How:** Extended data storage, chart integration
   - **Files:** `js/charts.js`, `js/habit-score.js`
   - **Output:** Enhanced habit analytics

**Reference:** [docs/specs/HABIT_SCORE_SPEC.md](docs/specs/HABIT_SCORE_SPEC.md)
**Template:** [templates/phase_chunk_template.md](templates/phase_chunk_template.md)

### Phase 1.2: Streak Freeze Mechanic
**Priority:** High | **Effort:** Low | **Duration:** 2-3 days

**Status:** 🔵 Not Started
- [ ] Design streak freeze inventory system
- [ ] Add freeze data to user schema
- [ ] Implement freeze consumption logic
- [ ] Add freeze earning mechanisms (XP purchase, achievements)
- [ ] Update streak calculation to respect freezes
- [ ] Add freeze management UI

**Reference:** [docs/specs/STREAK_FREEZE_SPEC.md](docs/specs/STREAK_FREEZE_SPEC.md)

### Phase 1.3: Event Sourcing Foundation
**Priority:** Medium | **Effort:** Medium | **Duration:** 3-4 days

**Status:** 🔵 Not Started
- [ ] Design event schema (immutable events)
- [ ] Create `js/event-store.js` module
- [ ] Update data operations to emit events
- [ ] Add event replay capability
- [ ] Migrate existing data to events

**Reference:** [docs/schemas/EVENT_SCHEMA.md](docs/schemas/EVENT_SCHEMA.md)

### Phase 1.4: IndexedDB Migration
**Priority:** Medium | **Effort:** Medium | **Duration:** 3-4 days

**Status:** 🔵 Not Started
- [ ] Add Dexie.js library
- [ ] Define database schema
- [ ] Create migration script from LocalStorage
- [ ] Update all modules to use IndexedDB
- [ ] Test data persistence and performance

**Reference:** [docs/guides/INDEXEDDB_MIGRATION.md](docs/guides/INDEXEDDB_MIGRATION.md)

---

## 📊 Phase 2: Intelligence Layer

**Status:** 🔵 Not Started  
**Duration:** 3 weeks  
**Details:** [phases/PHASE_2_INTELLIGENCE.md](phases/PHASE_2_INTELLIGENCE.md)

### Phase 2.1: Correlation Engine
- [ ] Create `js/insights.js` module
- [ ] Implement Pearson correlation
- [ ] Implement Spearman correlation
- [ ] Implement time-lag analysis
- [ ] Create insight discovery algorithm
- [ ] Add insights dashboard UI

### Phase 2.2: Predictive Context Sensitivity (PCS)
- [ ] Research LASSO regression for habit prediction
- [ ] Create `js/prediction.js` module
- [ ] Implement context variable tracking
- [ ] Calculate PCS score for habits
- [ ] Display habit strength (not just streak)

### Phase 2.3: Burnout Prediction
- [ ] Design burnout risk model
- [ ] Collect input features (sleep, tasks, HRV)
- [ ] Implement burnout score calculation
- [ ] Add intervention suggestions
- [ ] Create burnout alert system

---

## 🧠 Phase 3: Behavioral Science Implementation

**Status:** 🔵 Not Started  
**Duration:** 2 weeks  
**Details:** [phases/PHASE_3_BEHAVIORAL.md](phases/PHASE_3_BEHAVIORAL.md)

### Phase 3.1: Atomic Habits Framework
- [ ] Implement "Make It Obvious" (widgets, visibility)
- [ ] Implement "Make It Attractive" (gamification, anticipation)
- [ ] Implement "Make It Easy" (friction reduction, NLP input)
- [ ] Implement "Make It Satisfying" (feedback, rewards)

### Phase 3.2: Loss Aversion Mechanics
- [ ] Add Health Points (HP) system
- [ ] HP decreases on missed habits
- [ ] "Red Chains" for negative streaks
- [ ] Visual penalty indicators

### Phase 3.3: Variable Rewards
- [ ] Design random loot drop system
- [ ] Create mystery achievements
- [ ] Add surprise bonus events
- [ ] Balance reward frequency

---

## ⚙️ Phase 4: Automation & Integration

**Status:** 🔵 Not Started  
**Duration:** 2 weeks  
**Details:** [phases/PHASE_4_AUTOMATION.md](phases/PHASE_4_AUTOMATION.md)

### Phase 4.1: Rule Engine
- [ ] Create `js/rules.js` module
- [ ] Define rule schema (trigger, condition, action)
- [ ] Implement rule evaluation engine
- [ ] Create rule management UI
- [ ] Add pre-built rule templates

### Phase 4.2: Webhook System
- [ ] Create Python webhook endpoint
- [ ] Define webhook payload schema
- [ ] Add authentication for webhooks
- [ ] Create webhook management UI
- [ ] Document API for external integrations

### Phase 4.3: Natural Language Input
- [ ] Design NLP parsing system
- [ ] Integrate with local LLM (Ollama)
- [ ] Create `js/ai-logging.js` module
- [ ] Add natural language input UI
- [ ] Test parsing accuracy

---

## 🧪 Phase 5: Scientific Self-Experimentation

**Status:** 🔵 Not Started  
**Duration:** 2 weeks  
**Details:** [phases/PHASE_5_EXPERIMENTATION.md](phases/PHASE_5_EXPERIMENTATION.md)

### Phase 5.1: N-of-1 Trial Module
- [ ] Create `js/experiments.js` module
- [ ] Design experiment schema
- [ ] Implement phase randomization
- [ ] Add washout period logic
- [ ] Create experiment creation wizard

### Phase 5.2: Experiment Analytics
- [ ] Implement statistical analysis
- [ ] Create experiment results visualization
- [ ] Add effect size calculation
- [ ] Generate experiment reports

---

## 🤖 Phase 6: Local AI Integration

**Status:** 🔵 Not Started  
**Duration:** 4 weeks  
**Details:** [phases/PHASE_6_AI_INTEGRATION.md](phases/PHASE_6_AI_INTEGRATION.md)

### Phase 6.1: RAG Foundation
- [ ] Set up Ollama integration
- [ ] Add embedding model
- [ ] Integrate ChromaDB
- [ ] Create data embedding pipeline

### Phase 6.2: AI Assistant
- [ ] Create chat interface
- [ ] Implement context retrieval
- [ ] Add insight generation
- [ ] Create weekly summary automation

### Phase 6.3: Digital Coach
- [ ] Design coach intervention logic
- [ ] Implement proactive suggestions
- [ ] Add recovery mode switching
- [ ] Create coach personality/settings

---

## ✅ Completed Phases (Historical)

### Phase 1: Core Tracking Features ✅ COMPLETE
- [x] Project structure setup
- [x] Storage module with LocalStorage
- [x] Habits tracking module
- [x] Tasks/Todos module
- [x] Finances tracking module
- [x] Health metrics module
- [x] Time tracking module
- [x] Goals module
- [x] Dashboard view
- [x] Navigation system
- [x] Dark/Light theme toggle
- [x] Responsive design

### Phase 2: Gamification System ✅ COMPLETE
- [x] XP and level system
- [x] Achievement badges framework
- [x] Streak tracking
- [x] Celebration effects (confetti)
- [x] Motivational quotes

### Phase 3: Brain System Integration ✅ COMPLETE
- [x] Brain core architecture
- [x] Router and command system
- [x] Policy engine
- [x] State machines
- [x] Tool registry (100+ tools)
- [x] Audit logging
- [x] Security components
- [x] Immune system

---

## 🐛 Known Issues

- [ ] Charts don't update in real-time when switching views
- [ ] Timer persistence across page refreshes (partially fixed)
- [ ] Mobile sidebar doesn't close automatically after navigation (fixed)

---

## 📝 Notes

### Priority Order
1. Complete documentation structure (Phase 0)
2. Implement Habit Score Algorithm (Phase 1.1)
3. Implement Streak Freeze (Phase 1.2)
4. Continue with remaining Phase 1 tasks

### Version Goals
- **v1.0** - Core tracking features ✅
- **v1.1** - Gamification complete ✅
- **v1.2** - Brain system complete ✅
- **v2.0** - Foundation strengthening (Habit Score, Streak Freeze)
- **v2.1** - Intelligence layer (Correlations, PCS)
- **v3.0** - Full AI integration

---

*Last updated: February 2026*