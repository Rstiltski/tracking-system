# Phase 6: Local AI Integration - TODO List

**Duration:** 4 weeks
**Status:** 🟡 In Progress
**Dependencies:** Phase 5 Complete ✅
**Created:** February 20, 2026
**Updated:** February 21, 2026 (Phase 6.4 testing complete, core functionality implemented)

---

## Research Sources

Based on cloned repositories in `docs/research/repos/`:

| Repository | Key Patterns | Phase 6 Application |
|------------|--------------|---------------------|
| **habitica/** | RPG gamification, HP system, Streak Freeze, Party system | Digital Coach interventions |
| **apscheduler/** | BackgroundScheduler, CronTrigger, job management | Intervention scheduling |
| **autovar/** | Granger causality, VAR models, sign detection | Correlation engine |
| **perfice/** | NLG insight templates, FDR correction | Insight generation |
| **quantified-sleep/** | LASSO lag detection, Markov unfolding | Pattern detection |
| **Temporal_Behavior_Analysis/** | Time-lagged cross-correlation | Correlation analysis |

---

## Code Quality Updates

### Pylance Error Fixes (February 20, 2026)

Fixed `reportMissingImports` and `reportOptionalMemberAccess` errors in AI module files:

| File | Errors Fixed | Solution |
|------|--------------|----------|
| `brain/ai/embeddings.py` | 4 imports, 6 member access | `# type: ignore[import-unresolved]`, `# type: ignore[union-attr]` |
| `brain/ai/api_keys.py` | 1 import | `# type: ignore[import-unresolved]` |
| `brain/ai/providers/factory.py` | 8 imports | `# type: ignore[import-unresolved]` |

**Note:** The `import-unresolved` directive is correct for optional dependencies that may not be installed, as opposed to `import-untyped` which is for packages that exist but lack type stubs.

---

## Quick Reference

| Sub-Phase | Priority | Duration | Status |
|-----------|----------|----------|--------|
| 6.1 RAG Foundation | High | 5-6 days | ✅ Complete |
| 6.2 AI Assistant | High | 4-5 days | ✅ Complete |
| 6.3 Digital Coach | Medium | 5-6 days | ✅ Complete |
| 6.4 Integration & Polish | Medium | 4-5 days | 🟡 In Progress |

---

## Phase 6.1: RAG Foundation

**Priority:** High | **Effort:** High | **Duration:** 5-6 days
**Status:** ✅ **COMPLETE** - Core infrastructure implemented

### Module Structure

- [x] Create `brain/ai/__init__.py` with module docstring
- [x] Create `brain/ai/models.py` with data models
- [x] Create `brain/ai/providers/__init__.py`

### Provider Implementations

- [x] Create `brain/ai/providers/base.py` - AIProviderBase ABC
- [x] Create `brain/ai/providers/ollama_provider.py` - Local LLM (no API key required)
- [x] Create `brain/ai/providers/openai_provider.py` - OpenAI GPT with embeddings
- [x] Create `brain/ai/providers/anthropic_provider.py` - Claude provider
- [x] Create `brain/ai/providers/gemini_provider.py` - Google Gemini provider
- [x] Create `brain/ai/providers/groq_provider.py` - Groq provider
- [x] Create `brain/ai/providers/factory.py` - ProviderFactory with lazy loading

### API Key Management

- [x] Create `brain/ai/api_keys.py` with APIKeyManager class
- [x] Implement environment variable retrieval
- [x] Implement encrypted local storage
- [x] Implement Streamlit secrets support

### Embedding & Vector Store

- [x] Create `brain/ai/embeddings.py` with EmbeddingEngine (multi-backend)
- [x] Create `brain/ai/vector_store.py` with ChromaDB integration
- [ ] Implement data embedding pipeline for all modules (Phase 6.2)
- [ ] Create document chunking logic (Phase 6.2)

### Research Documentation

- [x] Create `docs/research/RAG_FOUNDATION_RESEARCH.md`

### Testing

- [x] Create `tests/test_ai_providers.py` (Phase 6.4)
- [x] Test Ollama provider initialization
- [x] Test cloud provider API key validation
- [x] Test embedding generation
- [x] Test vector store CRUD operations

---

## Phase 6.2: AI Assistant

**Priority:** High | **Effort:** Medium | **Duration:** 4-5 days
**Status:** ✅ **COMPLETE** - All core components implemented

### Core Components

- [x] Create `brain/ai/assistant.py` with AIAssistant class
- [x] Create `brain/ai/context_retriever.py` for RAG retrieval
- [x] Create `brain/ai/insight_generator.py` for structured insights
- [x] Create `brain/ai/chat_session.py` for session management

### Prompt Engineering

- [x] Create `brain/ai/prompts/__init__.py`
- [x] Create `brain/ai/prompts/system_prompts.py`
- [x] Create `brain/ai/prompts/templates.py`
- [x] Design habit coaching prompts
- [x] Design insight generation prompts

### Streamlit UI

- [x] Create `tracking_app/pages/ai_assistant.py`
- [x] Implement chat message display
- [x] Implement user input field
- [x] Implement streaming response display
- [x] Add chat history sidebar
- [x] Add source attribution display

### Session Persistence

- [x] Design chat session schema
- [x] Implement SQLite persistence for sessions
- [x] Add session load/restore functionality

### Testing

- [x] Create `tests/test_ai_assistant.py`
- [x] Test RAG context retrieval
- [x] Test insight generation
- [x] Test chat session management

---

## Phase 6.3: Digital Coach

**Priority:** Medium | **Effort:** High | **Duration:** 5-6 days
**Status:** ✅ **COMPLETE** - Core components and UI implemented

### Core Components

- [x] Create `brain/ai/coach/__init__.py`
- [x] Create `brain/ai/coach/intervention_engine.py`
- [x] Create `brain/ai/coach/user_assessment.py`
- [x] Create `brain/ai/coach/suggestion_engine.py`
- [x] Create `brain/ai/coach/recovery_mode.py`

### Rules & Personality

- [x] Create `brain/ai/coach/rules.py` with intervention rules
- [x] Create `brain/ai/coach/personality.py` with coach personality config
- [x] Define burnout risk interventions
- [x] Define streak break interventions
- [x] Define milestone celebrations
- [x] Define improvement encouragements

### Streamlit UI

- [x] Create `tracking_app/pages/digital_coach.py`
- [x] Implement coach personality settings
- [x] Implement intervention history display 
- [x] Implement coach on/off toggle

### Scheduling

- [ ] Integrate with APScheduler for intervention checks
- [ ] Add daily assessment job
- [ ] Add intervention trigger checks

### Testing

- [x] Create `tests/test_ai_coach.py`
- [x] Test user state assessment
- [x] Test intervention triggers
- [x] Test suggestion generation

---

## Phase 6.4: Integration & Polish

**Priority:** Medium | **Effort:** Medium | **Duration:** 4-5 days
**Status:** 🟡 **In Progress** - Core integration complete

### Brain Integration

- [x] Create `brain/ai/integration.py`
- [x] Connect AI to Brain tools for data access
- [x] Implement tool execution for AI actions

### Weekly Summaries

- [x] Create `brain/ai/weekly_summary.py`
- [x] Design weekly summary data model
- [x] Implement summary generation logic
- [ ] Add APScheduler job for weekly summaries
- [ ] Create summary delivery (in-app + optional email)

### Onboarding

- [x] Create `tracking_app/pages/ai_onboarding.py`
- [x] Design first-time setup wizard
- [x] Add provider selection screen
- [x] Add API key input form
- [x] Add model selection

### Settings

- [x] Create `tracking_app/pages/ai_settings.py`
- [x] Implement provider switching
- [x] Implement API key management UI
- [x] Implement model selection
- [x] Implement feature toggles

### Performance Optimization

- [ ] Implement lazy loading for embedding models
- [ ] Add embedding caching
- [ ] Optimize context window size
- [ ] Add request queuing for rate limits

### Documentation

- [x] Create `docs/guides/AI_USER_GUIDE.md`
- [x] Document provider setup
- [x] Document API key management
- [x] Document chat interface usage
- [x] Document coach features

### Testing

- [x] Create `tests/test_ai_integration.py`
- [x] Test full RAG pipeline
- [x] Test weekly summary generation
- [x] Test Brain tool integration

---

## Dependencies to Add

Add to `requirements.txt`:

```txt
# Phase 6: AI Integration
chromadb>=0.4.0
sentence-transformers>=2.2.0
ollama>=0.1.0

# Cloud providers (optional)
openai>=1.0.0
anthropic>=0.18.0
google-generativeai>=0.3.0
groq>=0.4.0

# ML runtime (optional)
torch>=2.0.0
```

---

## Success Criteria

| Criteria | Verification Method |
|----------|---------------------|
| Multi-provider support | Switch between Ollama, OpenAI, Anthropic |
| Chat interface works | Ask questions, get contextual answers |
| RAG retrieval accurate | Retrieved context relevant to query |
| Digital coach active | Proactive interventions triggered |
| Weekly summaries | Automated summary delivered |
| API keys secure | Keys encrypted, never exposed in logs |

---

## External Dependencies

| Dependency | Required | Installation |
|------------|----------|--------------|
| **Ollama** | Optional | https://ollama.ai |
| **CUDA** | Optional | For GPU acceleration |

---

## File Structure Preview

```
brain/ai/
├── __init__.py
├── models.py
├── providers/
│   ├── __init__.py
│   ├── base.py
│   ├── factory.py
│   ├── ollama_provider.py
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── gemini_provider.py
│   └── groq_provider.py
├── api_keys.py
├── embeddings.py
├── vector_store.py
├── assistant.py
├── context_retriever.py
├── insight_generator.py
├── chat_session.py
├── prompts/
│   ├── __init__.py
│   ├── system_prompts.py
│   └── templates.py
├── coach/
│   ├── __init__.py
│   ├── intervention_engine.py
│   ├── user_assessment.py
│   ├── suggestion_engine.py
│   ├── recovery_mode.py
│   ├── rules.py
│   └── personality.py
├── integration.py
├── weekly_summary.py
└── onboarding.py

tracking_app/pages/
├── ai_assistant.py
├── digital_coach.py
├── ai_onboarding.py
└── ai_settings.py

tests/
├── test_ai_providers.py
├── test_ai_assistant.py
├── test_ai_coach.py
├── test_ai_integration.py
└── test_weekly_summary.py
```

---

*Last updated: February 21, 2026*
