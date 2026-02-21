# Phase 6: Local AI Integration

**Duration:** 4 weeks
**Status:** 📋 Not Started
**Dependencies:** Phase 5 Complete ✅
**Created:** February 20, 2026

---

## Overview

Phase 6 implements AI integration with a **hybrid architecture** supporting both local (Ollama) and cloud providers (OpenAI, Anthropic, Google, Groq). This enables users to interact with their tracking data through natural language, receive proactive coaching, and generate automated insights.

**Implementation Language:** Python 3.10+
**Key Libraries:** ChromaDB, sentence-transformers, Ollama/OpenAI/Anthropic SDKs

---

## Goals

| Goal | Success Metric |
|------|----------------|
| Hybrid AI Support | Users can choose local OR cloud providers |
| RAG System | Users can chat with their data privately |
| Weekly Summaries | Automated insight generation every week |
| Digital Coach | Proactive suggestions based on patterns |
| API Key Management | Secure storage and easy configuration |

---

## Phase 6.1: RAG Foundation

**Priority:** High
**Effort:** High
**Duration:** 5-6 days
**Status:** 📋 Not Started

### Problem

Users cannot query their tracking data using natural language. The system lacks semantic search capabilities to find relevant context for AI responses.

### Solution

Implement a Retrieval-Augmented Generation (RAG) system:
- Vector database (ChromaDB) for semantic search
- Embedding pipeline using sentence-transformers
- Context retrieval from user's historical data
- Multi-provider LLM support (local + cloud)

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER QUERY                                   │
│              "Why have I been tired lately?"                     │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  EMBEDDING MODEL                                 │
│              (sentence-transformers)                             │
│         Converts query to vector representation                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VECTOR DATABASE                               │
│                     (ChromaDB)                                   │
│     Semantic search for relevant personal data                  │
│                                                                  │
│  Results:                                                       │
│  - Sleep data: avg 5.2 hrs last week                            │
│  - Mood logs: "feeling exhausted" (3 entries)                   │
│  - Exercise: skipped 4 workouts                                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LLM PROVIDER                                │
│              (Ollama / OpenAI / Anthropic)                       │
│     Generates response based on retrieved context                │
│                                                                  │
│  Response:                                                      │
│  "Based on your data, you've been averaging only 5.2 hours      │
│   of sleep this week, which is below your usual 7 hours.        │
│   You've also skipped 4 workouts and logged feeling             │
│   exhausted multiple times. Try prioritizing sleep..."          │
└─────────────────────────────────────────────────────────────────┘
```

### Data Model

```python
"""
Phase 6.1: RAG Foundation - Data Models

Python dataclasses for AI provider configuration and RAG components.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class AIProvider(Enum):
    """Supported AI providers."""
    OLLAMA = "ollama"           # Local, no API key required
    OPENAI = "openai"           # Requires OPENAI_API_KEY
    ANTHROPIC = "anthropic"     # Requires ANTHROPIC_API_KEY
    GEMINI = "gemini"           # Requires GOOGLE_API_KEY
    GROQ = "groq"               # Requires GROQ_API_KEY
    OPENROUTER = "openrouter"   # Requires OPENROUTER_API_KEY


@dataclass
class ProviderConfig:
    """Configuration for an AI provider."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    provider: AIProvider = AIProvider.OLLAMA
    model: str = "llama3"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 2048
    temperature: float = 0.7
    
    # Ollama-specific
    ollama_host: str = "http://localhost:11434"
    
    # Cloud provider options
    organization: Optional[str] = None
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def validate(self) -> bool:
        """Validate configuration has required fields."""
        if self.provider == AIProvider.OLLAMA:
            return True  # No API key needed for local
        return self.api_key is not None and len(self.api_key) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'provider': self.provider.value,
            'model': self.model,
            'api_key': '***' if self.api_key else None,  # Don't expose key
            'base_url': self.base_url,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'ollama_host': self.ollama_host,
            'organization': self.organization,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    model_name: str = "all-MiniLM-L6-v2"
    chunk_size: int = 500  # Characters per chunk
    chunk_overlap: int = 50  # Overlap between chunks
    batch_size: int = 32  # Embeddings per batch
    
    # Cache settings
    enable_cache: bool = True
    cache_ttl_hours: int = 24


@dataclass
class VectorDocument:
    """A document stored in the vector database."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Source tracking
    source_type: str = ""  # 'habit', 'task', 'health', 'journal'
    source_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for ChromaDB."""
        return {
            'id': self.id,
            'content': self.content,
            'embedding': self.embedding,
            'metadata': {
                **self.metadata,
                'source_type': self.source_type,
                'source_id': self.source_id,
                'created_at': self.created_at.isoformat(),
            }
        }


@dataclass
class RAGContext:
    """Context retrieved for a query."""
    query: str = ""
    query_embedding: Optional[List[float]] = None
    retrieved_docs: List[VectorDocument] = field(default_factory=list)
    relevance_scores: List[float] = field(default_factory=list)
    total_tokens: int = 0
    retrieval_time_ms: float = 0.0
    
    def get_context_text(self, max_docs: int = 5) -> str:
        """Get concatenated context text for LLM prompt."""
        docs = self.retrieved_docs[:max_docs]
        return "\n\n".join(doc.content for doc in docs)
```

### Default Model Configurations

| Provider | Default Model | Context Window | Cost per 1K tokens |
|----------|---------------|----------------|-------------------|
| **Ollama** | llama3 | 8K | Free (local) |
| **OpenAI** | gpt-4o-mini | 128K | $0.15/$0.60 |
| **Anthropic** | claude-3-haiku | 200K | $0.25/$1.25 |
| **Gemini** | gemini-1.5-flash | 1M | $0.075/$0.30 |
| **Groq** | llama-3.1-8b | 128K | Free tier available |

### Tasks

- [ ] Create `brain/ai/` module structure
- [ ] Implement `ProviderConfig` and `AIProvider` enums
- [ ] Create `brain/ai/providers/base.py` with `AIProviderBase` ABC
- [ ] Implement `brain/ai/providers/ollama_provider.py`
- [ ] Implement `brain/ai/providers/openai_provider.py`
- [ ] Implement `brain/ai/providers/anthropic_provider.py`
- [ ] Implement `brain/ai/providers/gemini_provider.py`
- [ ] Implement `brain/ai/providers/groq_provider.py`
- [ ] Create `brain/ai/providers/factory.py` for provider instantiation
- [ ] Implement `brain/ai/api_keys.py` for secure key management
- [ ] Create `brain/ai/embeddings.py` with sentence-transformers
- [ ] Implement `brain/ai/vector_store.py` with ChromaDB integration
- [ ] Create embedding pipeline for all tracking modules
- [ ] Write unit tests for provider implementations

### Implementation Location

```
brain/ai/
├── __init__.py
├── models.py                # Data models (ProviderConfig, etc.)
├── providers/
│   ├── __init__.py
│   ├── base.py              # AIProviderBase ABC
│   ├── factory.py           # ProviderFactory
│   ├── ollama_provider.py   # Local LLM
│   ├── openai_provider.py   # OpenAI GPT
│   ├── anthropic_provider.py # Claude
│   ├── gemini_provider.py   # Google Gemini
│   └── groq_provider.py     # Groq (fast)
├── api_keys.py              # API key management
├── embeddings.py            # Embedding generation
└── vector_store.py          # ChromaDB integration
```

---

## Phase 6.2: AI Assistant

**Priority:** High
**Effort:** Medium
**Duration:** 4-5 days
**Status:** 📋 Not Started

### Problem

Users cannot interact with their tracking data through natural language. They must manually navigate through different views and analyze data themselves.

### Solution

Create an AI Assistant that:
- Accepts natural language queries about user data
- Retrieves relevant context using RAG
- Generates human-readable insights and recommendations
- Supports streaming responses for real-time interaction

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT CHAT UI                             │
│                                                                  │
│  User: "Why have I been tired lately?"                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Assistant:                                                │  │
│  │ Based on your tracking data, I can see a few factors:    │  │
│  │                                                           │  │
│  │ 1. **Sleep**: You've averaged 5.2 hours/night this       │  │
│  │    week, down from your usual 7 hours.                   │  │
│  │                                                           │  │
│  │ 2. **Exercise**: You've skipped 4 of your planned        │  │
│  │    workouts this week.                                    │  │
│  │                                                           │  │
│  │ 3. **Mood**: You've logged "exhausted" 3 times.          │  │
│  │                                                           │  │
│  │ **Recommendation**: Try going to bed 30 minutes earlier  │  │
│  │ and resuming your workout routine for better energy.     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [Type a message...]                           [Send]           │
└─────────────────────────────────────────────────────────────────┘
```

### Data Model

```python
"""
Phase 6.2: AI Assistant - Data Models
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class MessageRole(Enum):
    """Chat message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ChatMessage:
    """A single chat message."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole = MessageRole.USER
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Context used for this response (assistant only)
    context_used: Optional[RAGContext] = None
    tokens_used: int = 0
    
    # Metadata
    model: str = ""
    provider: str = ""
    latency_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'role': self.role.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'tokens_used': self.tokens_used,
            'model': self.model,
            'provider': self.provider,
            'latency_ms': self.latency_ms,
        }


@dataclass
class ChatSession:
    """A chat session with message history."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    title: str = "New Chat"
    messages: List[ChatMessage] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Configuration
    provider_config_id: str = ""
    
    def add_message(self, role: MessageRole, content: str, **kwargs) -> ChatMessage:
        """Add a message to the session."""
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            **kwargs
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def get_context_window(self, max_messages: int = 10) -> List[ChatMessage]:
        """Get recent messages for context window."""
        return self.messages[-max_messages:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'messages': [m.to_dict() for m in self.messages],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'provider_config_id': self.provider_config_id,
        }


@dataclass
class AssistantResponse:
    """Structured response from the AI assistant."""
    content: str = ""
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    related_habits: List[str] = field(default_factory=list)
    related_metrics: List[str] = field(default_factory=list)
    
    # Source attribution
    sources: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    confidence: float = 0.0
    tokens_used: int = 0
    latency_ms: float = 0.0
```

### Assistant Capabilities

| Capability | Description | Example Query |
|------------|-------------|---------------|
| **Data Query** | Answer questions about tracked data | "How many habits did I complete this week?" |
| **Pattern Analysis** | Identify trends and patterns | "When am I most productive?" |
| **Correlation Discovery** | Find relationships between metrics | "Does sleep affect my mood?" |
| **Recommendations** | Suggest improvements | "What should I focus on this week?" |
| **Progress Summary** | Summarize progress over time | "How did I do this month vs last month?" |
| **Goal Guidance** | Help with goal achievement | "How can I reach my weight goal?" |

### Tasks

- [ ] Create `brain/ai/assistant.py` with main `AIAssistant` class
- [ ] Implement `brain/ai/context_retriever.py` for RAG retrieval
- [ ] Create `brain/ai/insight_generator.py` for structured insights
- [ ] Implement streaming response support
- [ ] Create chat session persistence
- [ ] Build `tracking_app/pages/ai_assistant.py` Streamlit UI
- [ ] Implement chat history sidebar
- [ ] Add response source attribution
- [ ] Write unit tests for assistant functionality

### Implementation Location

```
brain/ai/
├── assistant.py             # Main AIAssistant class
├── context_retriever.py     # RAG context retrieval
├── insight_generator.py     # Insight generation
├── chat_session.py          # Session management
└── prompts/
    ├── __init__.py
    ├── system_prompts.py    # System prompts for different modes
    └── templates.py         # Prompt templates

tracking_app/pages/
└── ai_assistant.py          # Streamlit chat UI
```

---

## Phase 6.3: Digital Coach

**Priority:** Medium
**Effort:** High
**Duration:** 5-6 days
**Status:** 📋 Not Started

### Problem

The AI Assistant is reactive - users must ask questions. The system lacks proactive guidance and intervention capabilities.

### Solution

Create a Digital Coach that:
- Monitors user data continuously
- Detects patterns requiring intervention
- Proactively suggests actions
- Adapts to user's current state (push vs recovery mode)

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DIGITAL COACH ENGINE                          │
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │  Pattern Monitor  │───▶│  Intervention    │                   │
│  │                   │    │  Decision Engine │                   │
│  └──────────────────┘    └────────┬─────────┘                   │
│          ▲                        │                              │
│          │                        ▼                              │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │  User State      │◀───│  Suggestion      │                   │
│  │  Assessment      │    │  Generator       │                   │
│  └──────────────────┘    └──────────────────┘                   │
│          │                                                       │
│          ▼                                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              INTERVENTION TYPES                           │   │
│  │                                                           │   │
│  │  🎯 Encouragement   ⚠️ Warning     💡 Suggestion          │   │
│  │  🔄 Recovery Mode   📊 Summary     🏆 Celebration          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Model

```python
"""
Phase 6.3: Digital Coach - Data Models
"""

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
import uuid


class UserState(Enum):
    """Assessed state of the user."""
    THRIVING = "thriving"      # Doing well, can handle more
    STABLE = "stable"          # Normal operation
    STRESSED = "stressed"      # Showing signs of strain
    STRUGGLING = "struggling"  # Needs support
    RECOVERING = "recovering"  # In recovery mode
    BURNOUT_RISK = "burnout_risk"  # High risk of burnout


class InterventionType(Enum):
    """Types of coach interventions."""
    ENCOURAGEMENT = "encouragement"
    WARNING = "warning"
    SUGGESTION = "suggestion"
    RECOVERY_MODE = "recovery_mode"
    SUMMARY = "summary"
    CELEBRATION = "celebration"
    REMINDER = "reminder"
    PIVOT = "pivot"


class InterventionPriority(Enum):
    """Priority level for interventions."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class CoachIntervention:
    """A coach intervention to be presented to the user."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: InterventionType = InterventionType.SUGGESTION
    priority: InterventionPriority = InterventionPriority.MEDIUM
    
    # Content
    title: str = ""
    message: str = ""
    details: str = ""
    
    # Actions the user can take
    actions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Triggering conditions
    trigger_reason: str = ""
    trigger_data: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    display_after: Optional[datetime] = None
    
    # User interaction
    shown: bool = False
    shown_at: Optional[datetime] = None
    dismissed: bool = False
    action_taken: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type.value,
            'priority': self.priority.value,
            'title': self.title,
            'message': self.message,
            'details': self.details,
            'actions': self.actions,
            'trigger_reason': self.trigger_reason,
            'created_at': self.created_at.isoformat(),
            'shown': self.shown,
            'dismissed': self.dismissed,
            'action_taken': self.action_taken,
        }


@dataclass
class CoachPersonality:
    """Configurable coach personality."""
    name: str = "Coach"
    tone: str = "supportive"  # supportive, challenging, gentle, direct
    style: str = "balanced"   # balanced, analytical, empathetic, action-oriented
    
    # Communication preferences
    use_emojis: bool = True
    use_encouragement: bool = True
    use_humor: bool = False
    
    # Intervention thresholds
    intervention_frequency: str = "moderate"  # minimal, moderate, frequent
    risk_sensitivity: str = "balanced"  # conservative, balanced, sensitive
    
    def get_system_prompt_additions(self) -> str:
        """Get personality additions for system prompt."""
        prompts = {
            "supportive": "Be warm and encouraging in your responses.",
            "challenging": "Be direct and push the user to improve.",
            "gentle": "Be soft and understanding in your approach.",
            "direct": "Be concise and get straight to the point.",
        }
        return prompts.get(self.tone, "")


@dataclass
class UserAssessment:
    """Assessment of user's current state."""
    user_id: str = ""
    assessed_at: datetime = field(default_factory=datetime.now)
    
    # Overall state
    state: UserState = UserState.STABLE
    confidence: float = 0.0
    
    # Component scores
    habit_health_score: float = 0.0
    consistency_score: float = 0.0
    energy_level: float = 0.0
    stress_indicators: float = 0.0
    
    # Derived insights
    strengths: List[str] = field(default_factory=list)
    areas_of_concern: List[str] = field(default_factory=list)
    recommended_focus: List[str] = field(default_factory=list)
    
    # Mode recommendation
    recommended_mode: str = "normal"  # normal, push, recovery
    mode_reason: str = ""
```

### Intervention Rules

| Trigger | Condition | Intervention Type | Example |
|---------|-----------|-------------------|---------|
| **Burnout Risk** | Burnout score > 70% | RECOVERY_MODE | "Your burnout risk is high. I'm switching you to recovery mode." |
| **Streak Break** | Streak broken after 7+ days | ENCOURAGEMENT | "Your streak ended, but you built a great habit! Let's restart." |
| **Low Completion** | < 50% completion for 3 days | WARNING | "You've missed several habits. Is everything okay?" |
| **Milestone** | Goal achieved | CELEBRATION | "🎉 Congratulations! You reached your goal!" |
| **Inconsistency** | High variance in completion times | SUGGESTION | "Your routine timing varies a lot. Try setting specific times." |
| **Improvement** | 20% improvement in metric | ENCOURAGEMENT | "Great progress! Your sleep quality improved this week." |

### Tasks

- [ ] Create `brain/ai/coach/` module structure
- [ ] Implement `brain/ai/coach/intervention_engine.py`
- [ ] Implement `brain/ai/coach/user_assessment.py`
- [ ] Implement `brain/ai/coach/suggestion_engine.py`
- [ ] Implement `brain/ai/coach/recovery_mode.py`
- [ ] Create intervention rule definitions
- [ ] Implement coach personality configuration
- [ ] Build `tracking_app/pages/digital_coach.py` settings UI
- [ ] Add intervention scheduling with APScheduler
- [ ] Write unit tests for coach functionality

### Implementation Location

```
brain/ai/coach/
├── __init__.py
├── intervention_engine.py   # Main intervention logic
├── user_assessment.py       # User state assessment
├── suggestion_engine.py     # Proactive suggestions
├── recovery_mode.py         # Recovery mode management
├── rules.py                 # Intervention rule definitions
└── personality.py           # Coach personality config

tracking_app/pages/
└── digital_coach.py         # Coach settings UI
```

---

## Phase 6.4: Integration & Polish

**Priority:** Medium
**Effort:** Medium
**Duration:** 4-5 days
**Status:** 📋 Not Started

### Problem

The AI components are built in isolation. They need to be integrated with the existing Brain system and tested thoroughly.

### Solution

Complete the integration phase:
- Connect AI to existing Brain tools
- Add weekly summary automation
- Create user onboarding flow
- Write comprehensive tests
- Optimize performance

### Key Deliverables

| Deliverable | Description |
|-------------|-------------|
| **Brain Integration** | AI can use Brain tools for data access |
| **Weekly Summaries** | Automated summary generation every week |
| **Onboarding Flow** | First-time user setup for AI features |
| **Performance Tuning** | Optimize response times and memory usage |
| **Documentation** | User guide and API documentation |

### Weekly Summary Automation

```python
"""
Weekly Summary Generator

Automatically generates summaries of user's tracking data every week.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any


@dataclass
class WeeklySummary:
    """Generated weekly summary."""
    id: str
    user_id: str
    week_start: datetime
    week_end: datetime
    
    # Habit summary
    habits_completed: int
    habits_total: int
    completion_rate: float
    top_habits: List[str]
    struggling_habits: List[str]
    
    # Task summary
    tasks_completed: int
    tasks_total: int
    overdue_tasks: int
    
    # Health summary
    avg_sleep_hours: float
    avg_mood: float
    weight_change: float
    
    # Goals progress
    goals_progress: List[Dict[str, Any]]
    
    # AI-generated insights
    key_insights: List[str]
    recommendations: List[str]
    
    # Narrative summary (generated by LLM)
    narrative: str
    
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_email_format(self) -> str:
        """Format as email HTML."""
        pass
    
    def to_notification_format(self) -> str:
        """Format for push notification."""
        pass
```

### Tasks

- [ ] Create `brain/ai/integration.py` for Brain tool access
- [ ] Implement `brain/ai/weekly_summary.py` automation
- [ ] Add APScheduler job for weekly summary generation
- [ ] Create `tracking_app/pages/ai_onboarding.py`
- [ ] Implement first-time setup wizard
- [ ] Add AI settings to main settings page
- [ ] Optimize embedding generation (batching, caching)
- [ ] Implement lazy loading for models
- [ ] Write comprehensive test suite
- [ ] Create user documentation
- [ ] Add API documentation

### Implementation Location

```
brain/ai/
├── integration.py           # Brain tool integration
├── weekly_summary.py        # Automated summaries
└── onboarding.py            # User setup flow

tracking_app/pages/
├── ai_onboarding.py         # First-time setup
└── ai_settings.py           # AI configuration

tests/
├── test_ai_providers.py
├── test_ai_assistant.py
├── test_ai_coach.py
├── test_ai_integration.py
└── test_weekly_summary.py

docs/
└── guides/
    └── AI_USER_GUIDE.md     # User documentation
```

---

## API Key Management

### Secure Storage Strategy

| Storage Method | Security Level | Use Case |
|---------------|----------------|----------|
| **Environment Variables** | High | Server/production deployments |
| **Encrypted Local File** | Medium | Desktop development |
| **Streamlit Secrets** | High | Streamlit Cloud deployment |
| **User Input (Session)** | Low | Temporary testing |

### Implementation

```python
# brain/ai/api_keys.py

import os
import json
from pathlib import Path
from typing import Optional
import base64
import hashlib

class APIKeyManager:
    """
    Secure API key management for AI providers.
    
    Priority order for key retrieval:
    1. Environment variables (highest priority)
    2. Streamlit secrets (if available)
    3. Encrypted local storage
    4. User input via UI (lowest priority, session-only)
    """
    
    ENV_KEY_MAPPING = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }
    
    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or Path.home() / ".veryfyn" / "ai_keys.enc"
    
    def get_key(self, provider: str) -> Optional[str]:
        """Get API key for provider."""
        # Try environment variable first
        env_key = self.ENV_KEY_MAPPING.get(provider.lower())
        if env_key:
            key = os.environ.get(env_key)
            if key:
                return key
        
        # Try Streamlit secrets
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and provider in st.secrets:
                return st.secrets[provider]
        except ImportError:
            pass
        
        # Try encrypted local storage
        if self.storage_path.exists():
            return self._load_from_storage(provider)
        
        return None
    
    def set_key(self, provider: str, api_key: str, store_locally: bool = True):
        """Store API key for provider."""
        # Set in environment for current session
        env_key = self.ENV_KEY_MAPPING.get(provider.lower())
        if env_key:
            os.environ[env_key] = api_key
        
        # Optionally store in encrypted local file
        if store_locally:
            self._save_to_storage(provider, api_key)
    
    def _save_to_storage(self, provider: str, api_key: str):
        """Save to encrypted local storage."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing keys
        keys = {}
        if self.storage_path.exists():
            keys = self._decrypt_storage()
        
        keys[provider] = api_key
        
        # Encrypt and save
        self._encrypt_storage(keys)
    
    def _encrypt_storage(self, keys: dict) -> None:
        """Encrypt and save keys to storage."""
        import json
        data = json.dumps(keys).encode()
        # Simple encryption (in production, use proper encryption)
        encoded = base64.b64encode(data)
        with open(self.storage_path, 'wb') as f:
            f.write(encoded)
    
    def _decrypt_storage(self) -> dict:
        """Decrypt and load keys from storage."""
        try:
            with open(self.storage_path, 'rb') as f:
                encoded = f.read()
            data = base64.b64decode(encoded)
            return json.loads(data.decode())
        except Exception:
            return {}
```

---

## Dependencies

### Required Python Packages

```txt
# Phase 6 Dependencies

# Vector Database
chromadb>=0.4.0

# Embeddings
sentence-transformers>=2.2.0

# Local LLM
ollama>=0.1.0

# Cloud Providers (optional)
openai>=1.0.0
anthropic>=0.18.0
google-generativeai>=0.3.0
groq>=0.4.0

# Scheduling (already installed from Phase 4)
apscheduler>=3.10.0

# ML Runtime (optional, for local embeddings)
torch>=2.0.0
```

### External Dependencies

| Dependency | Required | Description |
|------------|----------|-------------|
| **Ollama** | Optional | Local LLM server - https://ollama.ai |
| **CUDA** | Optional | GPU acceleration for embeddings |

---

## Security Considerations

| Concern | Mitigation |
|---------|------------|
| **API Key Exposure** | Never log or display full keys, use encrypted storage |
| **Data Privacy** | Local-first: use Ollama by default, cloud requires consent |
| **Prompt Injection** | Sanitize user inputs, validate generated content |
| **Model Hallucination** | Ground responses in actual data, cite sources |
| **Rate Limiting** | Implement request throttling for cloud APIs |

---

## Performance Considerations

| Challenge | Solution |
|-----------|----------|
| **Slow Embedding Generation** | Batch processing, background jobs, caching |
| **Large Vector Database** | Periodic cleanup, efficient indexing |
| **High Memory Usage** | Lazy model loading, limit context window |
| **API Rate Limits** | Request queuing, exponential backoff |

---

## Success Criteria

| Criteria | How to Verify |
|----------|---------------|
| Multi-provider support | Can switch between Ollama, OpenAI, Anthropic |
| Chat interface works | Can ask questions and get contextual answers |
| RAG retrieval accurate | Retrieved context is relevant to query |
| Digital coach active | Proactive interventions are triggered |
| Weekly summaries generated | Automated summary delivered weekly |
| API keys secure | Keys stored encrypted, never exposed |

---

## Testing Strategy

### Unit Tests

```python
# tests/test_ai_providers.py

def test_ollama_provider_initialization():
    """Test Ollama provider can be initialized without API key."""
    config = ProviderConfig(provider=AIProvider.OLLAMA, model="llama3")
    assert config.validate() == True

def test_openai_provider_requires_key():
    """Test OpenAI provider requires API key."""
    config = ProviderConfig(provider=AIProvider.OPENAI, model="gpt-4")
    assert config.validate() == False
    config.api_key = "sk-test"
    assert config.validate() == True

def test_embedding_generation():
    """Test embedding generation from text."""
    from brain.ai.embeddings import EmbeddingEngine
    engine = EmbeddingEngine()
    embedding = engine.embed("Test text")
    assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension

def test_vector_store_crud():
    """Test ChromaDB operations."""
    from brain.ai.vector_store import VectorStore
    store = VectorStore()
    store.add("doc1", "Test content", {"source": "test"})
    results = store.search("Test", n_results=1)
    assert len(results) == 1
```

### Integration Tests

```python
# tests/test_ai_integration.py

def test_full_rag_pipeline():
    """Test complete RAG pipeline."""
    # 1. Embed user data
    # 2. Store in vector DB
    # 3. Query with context retrieval
    # 4. Generate response
    pass

def test_weekly_summary_generation():
    """Test automated weekly summary."""
    pass
```

---

## Future Enhancements (Post-Phase 6)

| Enhancement | Description |
|-------------|-------------|
| **Voice Interface** | Speech-to-text for queries |
| **Multi-modal** | Image analysis (food logging, etc.) |
| **Fine-tuning** | Custom model for habit coaching |
| **Agent Mode** | Autonomous AI actions |
| **Social Features** | AI-moderated group challenges |

---

## Cross-References

| Document | Content |
|----------|---------|
| [TODO.md](TODO.md) | Task tracking |
| [ROADMAP.md](ROADMAP.md) | Overall roadmap |
| [docs/research/AI_AND_PREDICTION.md](../docs/research/AI_AND_PREDICTION.md) | AI research |
| [brain/README.md](../brain/README.md) | Brain system docs |

---

*Last updated: February 20, 2026*
*Status: 📋 Phase 6 Not Started - Ready for Implementation*