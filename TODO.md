# 📋 Veryfyn - TODO List

**Task tracking for the Veryfyn Personal Tracking System.**

---

## 🧭 Quick Navigation

| Want to... | Go to... |
|------------|----------|
| **AI entry point** | [AI_START_HERE.md](AI_START_HERE.md) |
| **Get started** | [GETTING_STARTED.md](GETTING_STARTED.md) |
| **Understand rules** | [PROJECT_RULES.md](PROJECT_RULES.md) |
| **Find features** | [FEATURE_MAP.md](FEATURE_MAP.md) |
| **See roadmap** | [ROADMAP.md](ROADMAP.md) |
| **See research** | [docs/research/](docs/research/) |

---

## ✅ Completed Phases

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

### Phase 4: Reminders & Notifications ✅ COMPLETE
- [x] Notification engine implementation
- [x] Habit reminders with smart timing
- [x] Task and goal deadline alerts
- [x] Notification settings UI
- [x] Quiet hours and preferences
- [x] Test suite (60+ tests passing)

### Phase 5: Data Management ✅ COMPLETE
- [x] Data export (CSV/JSON/SQLite)
- [x] Data import functionality
- [x] Backup/restore feature
- [x] Data reset options
- [x] Lifecycle management

### Phase 6: Intelligence Layer ✅ COMPLETE
- [x] Research analysis completed
- [x] Correlation engine implemented
- [x] Prediction models implemented
- [x] Time views analysis
- [x] Burnout detection

### Phase 7: Polish & Enhancement ✅ COMPLETE
- [x] Performance optimization
- [x] Memory management
- [x] Debounce utilities
- [x] Lazy loading
- [x] Pagination

### Phase 8: Advanced Performance ✅ COMPLETE
- [x] Profiling system
- [x] Event tracking
- [x] Heatmap analytics
- [x] Weekly review

### Phase 9: Advanced Reporting & Social ✅ COMPLETE
- [x] Reports page with date range picker
- [x] Multi-habit comparison charts
- [x] CSV/JSON export
- [x] Widget Settings page
- [x] Dashboard customization
- [x] Social Features (Friends, Challenges, Leaderboards) - EXIST
- [x] Template System - EXIST

---

## 🚀 Phase 10: Core Enhancements (Next)

Based on `docs/research/` analysis, these are the priority features to implement:

### Phase 6.1: Enhanced Habits (HIGH PRIORITY)
**Source:** Loop Habit Tracker, Habitica

- [ ] **Habit Score Algorithm** - Replace rigid streaks with weighted moving average
  - Weighted average of completion (recent days count more)
  - Score 0.0-1.0 instead of binary streak
  - Forgiving: gradual decay, not instant reset
  - Files: `tracking_app/models/habit.py`, `tracking_app/storage.py`

- [ ] **Streak Freeze System** - Preserve streak on missed days
  - Inventory system for freeze items
  - Earn freezes through achievements or purchase
  - Auto-apply option
  - Files: `tracking_app/models/inventory.py`, `tracking_app/pages/habits.py`

- [ ] **HP (Health Points) System** - Lose HP on missed habits
  - Start with 50 HP
  - Missed habits deal damage
  - HP=0 triggers level loss
  - Files: `tracking_app/models/user.py`, `tracking_app/pages/achievements.py`

### Phase 6.2: Correlation Engine (HIGH PRIORITY)
**Source:** `docs/research/CORRELATION_ENGINE_RESEARCH.md`

- [ ] **Pearson/Spearman Correlation** - Basic correlation discovery
  - Sleep ↔ Mood correlation
  - Exercise ↔ Energy correlation
  - Files: `brain/analysis/correlation.py`

- [ ] **Time-Lagged Correlation** - Discover delayed effects
  - Sleep affects tomorrow's productivity
  - Exercise affects mood 2 days later
  - Files: `brain/analysis/lagged_correlation.py`

- [ ] **Natural Language Insights** - Generate readable insights
  - "Your sleep is strongly correlated with mood (r=0.67)"
  - Templates for positive/negative relationships
  - Files: `brain/analysis/insights.py`

### Phase 6.3: Predictive Analytics (MEDIUM PRIORITY)
**Source:** `docs/research/AI_AND_PREDICTION.md`

- [ ] **Burnout Prediction** - Early warning system
  - Analyze: sleep, task completion, work hours, mood
  - Risk score 0-100
  - Intervention suggestions
  - Files: `brain/analysis/burnout.py`

- [ ] **Predictive Context Sensitivity (PCS)** - Habit predictability
  - Which context variables predict behavior
  - LASSO regression for feature selection
  - Score: How "habitual" is this behavior?
  - Files: `brain/analysis/pcs.py`

### Phase 6.4: Variable Rewards (MEDIUM PRIORITY)
**Source:** `docs/research/BEHAVIORAL_SCIENCE.md`

- [ ] **Random Loot Drops** - Variable rewards on completion
  - Common (60%), Rare (30%), Epic (8%), Legendary (2%)
  - Virtual items or bonus XP
  - Files: `brain/gamification/loot.py`

- [ ] **Mystery Achievements** - Hidden unlock conditions
  - Discoverable through gameplay
  - Surprise element
  - Files: `brain/gamification/achievements.py`

### Phase 6.5: N-of-1 Trials (FUTURE)
**Source:** `docs/research/OPEN_SOURCE_PROJECTS.md` (StudyU)

- [ ] **Experiment Module** - Self-experimentation
  - A-B-A withdrawal design
  - Randomized block design
  - Statistical analysis
  - Files: `tracking_app/pages/experiments.py`

### Phase 6.6: Local RAG (FUTURE)
**Source:** `docs/research/AI_AND_PREDICTION.md`

- [ ] **Ollama Integration** - Local LLM connection
- [ ] **ChromaDB Setup** - Vector database for personal data
- [ ] **Digital Coach** - AI assistant for insights
- [ ] **Chat with Your Data** - Natural language queries

---

## 📊 Implementation Priority Matrix

| Feature | Impact | Effort | Priority |
|---------|--------|--------|----------|
| Habit Score | High | Low | **Phase 6.1** |
| Streak Freeze | High | Low | **Phase 6.1** |
| HP System | Medium | Medium | **Phase 6.1** |
| Correlation Engine | High | Medium | **Phase 6.2** |
| Time-Lag Analysis | High | Medium | **Phase 6.2** |
| Burnout Prediction | Medium | Medium | **Phase 6.3** |
| Variable Rewards | Medium | Low | **Phase 6.4** |
| N-of-1 Trials | High | High | Future |
| Local RAG | Transformative | High | Future |

---

## 🐛 Known Issues

- [ ] Charts don't update in real-time when switching views
- [ ] Timer persistence across page refreshes (partially fixed)
- [ ] Streamlit pages need session state persistence

---

## 📝 Notes

### Version Goals
- **v1.0** - Core tracking features ✅
- **v1.1** - Gamification complete ✅
- **v1.2** - Brain system complete ✅
- **v1.3** - Notifications complete ✅
- **v1.4** - Data management complete ✅
- **v2.0** - Intelligence Layer (in progress)
- **v3.0** - Core Enhancements (planned, no AI)

### Research Sources
- [AI_AND_PREDICTION.md](docs/research/AI_AND_PREDICTION.md)
- [BEHAVIORAL_SCIENCE.md](docs/research/BEHAVIORAL_SCIENCE.md)
- [CORRELATION_ENGINE_RESEARCH.md](docs/research/CORRELATION_ENGINE_RESEARCH.md)
- [OPEN_SOURCE_PROJECTS.md](docs/research/OPEN_SOURCE_PROJECTS.md)
- [TECHNICAL_ARCHITECTURES.md](docs/research/TECHNICAL_ARCHITECTURES.md)

---

*Last updated: February 2026*
*Updated with research-based features*