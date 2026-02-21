# Phase 6.2: AI Assistant Research Report

**Created:** February 20, 2026
**Status:** Complete
**Repositories Analyzed:** LangChain, LlamaIndex, PrivateGPT, MemGPT

---

## Executive Summary

This research identifies key patterns and reusable components for implementing the Veryfyn AI Assistant. The analysis focuses on four critical areas:

1. **Chat Session Management** - Conversation persistence and history
2. **Context Retrieval Strategies** - RAG patterns for personal data
3. **Prompt Template Systems** - Structured prompt engineering
4. **Memory Management** - Long-term and short-term memory patterns

---

## 1. Chat Session Management Patterns

### Pattern 1.1: Message-Based Architecture (LangChain)

LangChain uses a message-based architecture with typed message classes:

```python
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

class ChatSession:
    """Session management with typed messages."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: List[BaseMessage] = []
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_user_message(self, content: str) -> None:
        self.messages.append(HumanMessage(content=content))
        self.updated_at = datetime.now()
    
    def add_ai_message(self, content: str) -> None:
        self.messages.append(AIMessage(content=content))
        self.updated_at = datetime.now()
    
    def get_context_window(self, max_tokens: int) -> List[BaseMessage]:
        """Get messages that fit within token limit."""
        # Implement token counting and windowing
        pass
```

### Pattern 1.2: Session Persistence (PrivateGPT)

PrivateGPT implements session persistence with SQLite:

```python
# Database schema for chat sessions
CREATE TABLE chat_sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    metadata JSON
);

CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    role TEXT,  -- 'user', 'assistant', 'system'
    content TEXT,
    created_at TIMESTAMP,
    tokens_used INTEGER,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
);
```

### Recommendation for Veryfyn

```python
# brain/ai/chat_session.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class ChatMessage:
    """Single message in a chat session."""
    role: MessageRole
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    tokens: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChatSession:
    """Chat session with persistence support."""
    session_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: MessageRole, content: str, **metadata) -> None:
        """Add a message to the session."""
        message = ChatMessage(
            role=role,
            content=content,
            metadata=metadata
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_messages_for_llm(self, max_tokens: int = 4096) -> List[Dict[str, str]]:
        """Get messages formatted for LLM API."""
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in self.messages
        ]
    
    def get_context_window(self, max_messages: int = 20) -> List[ChatMessage]:
        """Get recent messages within context window."""
        return self.messages[-max_messages:]
```

---

## 2. Context Retrieval Strategies

### Pattern 2.1: Hybrid Retrieval (LlamaIndex)

LlamaIndex combines multiple retrieval strategies:

```python
from llama_index.core import VectorStoreIndex, SummaryIndex
from llama_index.core.retrievers import VectorIndexRetriever, SummaryIndexRetriever
from llama_index.core.retrievers import RouterRetriever

# Vector retrieval for semantic similarity
vector_retriever = VectorIndexRetriever(
    index=vector_index,
    similarity_top_k=5
)

# Summary retrieval for broad queries
summary_retriever = SummaryIndexRetriever(
    index=summary_index
)

# Router combines multiple retrievers
hybrid_retriever = RouterRetriever(
    retrievers=[vector_retriever, summary_retriever],
    selector=LLMSingleSelector()
)
```

### Pattern 2.2: Metadata Filtering (LangChain)

Filter by source type, date, user context:

```python
from langchain.vectorstores import Chroma
from langchain.schema import Document

# Query with metadata filters
results = vectorstore.similarity_search(
    query="What habits did I miss?",
    k=5,
    filter={
        "source_type": "habit",
        "date": {"$gte": "2026-01-01"}
    }
)
```

### Recommendation for Veryfyn

```python
# brain/ai/context_retriever.py

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from brain.ai.vector_store import VectorStore, SearchResult
from brain.ai.models import VectorDocument

class ContextRetriever:
    """
    Context retriever for Veryfyn personal data.
    
    Supports:
    - Semantic similarity search
    - Source type filtering (habit, task, health, etc.)
    - Date range filtering
    - Multi-query expansion
    """
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
    
    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        source_types: Optional[List[str]] = None,
        date_range: Optional[tuple] = None,
        min_relevance: float = 0.5
    ) -> List[SearchResult]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User query
            n_results: Maximum results
            source_types: Filter by source types
            date_range: (start_date, end_date) tuple
            min_relevance: Minimum relevance score
        
        Returns:
            List of relevant documents
        """
        # Build where clause
        where_clause = {}
        if source_types:
            where_clause['source_type'] = {'$in': source_types}
        
        # Search
        results = self.vector_store.search(
            query=query,
            n_results=n_results * 2,  # Get extra for filtering
            where=where_clause if where_clause else None
        )
        
        # Filter by relevance and date
        filtered = []
        for result in results:
            if result.score < min_relevance:
                continue
            if date_range:
                doc_date = result.document.metadata.get('date')
                if doc_date and not (date_range[0] <= doc_date <= date_range[1]):
                    continue
            filtered.append(result)
        
        return filtered[:n_results]
    
    def retrieve_for_habits(self, query: str) -> List[SearchResult]:
        """Retrieve habit-related context."""
        return self.retrieve(
            query=query,
            source_types=['habit', 'habit_completion'],
            n_results=5
        )
    
    def retrieve_for_health(self, query: str) -> List[SearchResult]:
        """Retrieve health-related context."""
        return self.retrieve(
            query=query,
            source_types=['health', 'sleep', 'mood', 'exercise'],
            n_results=5
        )
    
    def retrieve_recent(self, days: int = 7, n_results: int = 10) -> List[SearchResult]:
        """Retrieve recent activity across all types."""
        start_date = datetime.now() - timedelta(days=days)
        return self.retrieve(
            query="recent activity",  # Generic query
            n_results=n_results,
            date_range=(start_date, datetime.now())
        )
```

---

## 3. Prompt Template Systems

### Pattern 3.1: Template Inheritance (LangChain)

LangChain uses PromptTemplate with variable substitution:

```python
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate

# System prompt template
system_template = """You are a helpful AI assistant for {app_name}.

Your role is to help users with {specialty}.

Guidelines:
{guidelines}

Available context:
{context}
"""

system_prompt = SystemMessagePromptTemplate.from_template(system_template)

# Human prompt template
human_template = "{query}"
human_prompt = HumanMessagePromptTemplate.from_template(human_template)

# Combined chat prompt
chat_prompt = ChatPromptTemplate.from_messages([
    system_prompt,
    human_prompt
])
```

### Pattern 3.2: Few-Shot Prompting

```python
from langchain.prompts import FewShotPromptTemplate

examples = [
    {"query": "Why am I tired?", "answer": "Based on your sleep data, you've averaged 5.5 hours this week, which is below your target of 7 hours."},
    {"query": "How are my habits?", "answer": "You've completed 85% of your habits this week, with meditation being your most consistent habit at 100%."}
]

example_prompt = PromptTemplate(
    input_variables=["query", "answer"],
    template="Query: {query}\nAnswer: {answer}"
)

few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="You are a personal tracking assistant. Answer queries based on user data.",
    suffix="Query: {query}\nAnswer:",
    input_variables=["query"]
)
```

### Recommendation for Veryfyn

```python
# brain/ai/prompts/system_prompts.py

from string import Template
from typing import Dict, Any, List

class SystemPromptBuilder:
    """Build system prompts for Veryfyn AI Assistant."""
    
    BASE_PROMPT = Template("""You are a helpful AI assistant integrated with Veryfyn, a personal tracking system.

Your role is to help users understand their habits, health, productivity, and goals.

## Capabilities
- Analyze habit patterns and provide insights
- Track goal progress and suggest improvements
- Identify correlations between behaviors
- Provide personalized recommendations

## Guidelines
- Be concise but thorough
- Ground your responses in the provided context
- If you don't have enough information, say so
- Provide actionable recommendations when appropriate
- Be supportive and encouraging
- Avoid making medical or financial advice
- Respond in a friendly, conversational tone

## Available Context
$context

## Current Date
$current_date

## User Profile
$user_profile""")

    COACH_PROMPT = Template("""You are a supportive digital coach for Veryfyn.

## Personality
$personality

## Coaching Style
- Celebrate successes enthusiastically
- Frame setbacks as learning opportunities
- Provide specific, actionable suggestions
- Check in on progress regularly

## Current Situation
$situation

## Recommended Action
Suggest an appropriate intervention or encouragement.""")

    @classmethod
    def build(cls, context: str = "", user_profile: Dict[str, Any] = None) -> str:
        """Build a system prompt with context."""
        return cls.BASE_PROMPT.substitute(
            context=context or "No relevant context available.",
            current_date=datetime.now().strftime("%Y-%m-%d"),
            user_profile=str(user_profile or {})
        )
    
    @classmethod
    def build_coach_prompt(
        cls,
        personality: str,
        situation: str
    ) -> str:
        """Build a coaching intervention prompt."""
        return cls.COACH_PROMPT.substitute(
            personality=personality,
            situation=situation
        )


# brain/ai/prompts/templates.py

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class PromptTemplate:
    """Reusable prompt template."""
    name: str
    template: str
    input_variables: List[str]
    description: str = ""

# Pre-defined templates for Veryfyn
INSIGHT_TEMPLATE = PromptTemplate(
    name="habit_insight",
    template="""Analyze the following habit data and provide insights:

Habit: {habit_name}
Completions (last 30 days): {completion_rate}%
Current streak: {streak} days
Best streak: {best_streak} days
Average time: {avg_time}
Notes: {notes}

Provide:
1. Pattern observation
2. Success factors
3. Improvement suggestions""",
    input_variables=[
        "habit_name", "completion_rate", "streak", 
        "best_streak", "avg_time", "notes"
    ]
)

GOAL_PROGRESS_TEMPLATE = PromptTemplate(
    name="goal_progress",
    template="""Analyze goal progress and provide recommendations:

Goal: {goal_name}
Target: {target}
Current: {current}
Deadline: {deadline}
Progress: {progress_pct}%
Recent activities: {recent_activities}

Provide:
1. Progress assessment
2. Potential blockers
3. Action items to get back on track""",
    input_variables=[
        "goal_name", "target", "current", "deadline",
        "progress_pct", "recent_activities"
    ]
)
```

---

## 4. Memory Management Patterns

### Pattern 4.1: Memory Hierarchy (MemGPT)

MemGPT implements a tiered memory system:

```python
# Core memory (always in context)
core_memory = {
    "persona": "I am a helpful assistant...",
    "user_preferences": {...},
    "key_facts": [...]
}

# Working memory (recent interactions)
working_memory = {
    "recent_messages": [...],
    "current_context": {...}
}

# Archival memory (long-term storage)
archival_memory = VectorStore()  # Semantic search
```

### Pattern 4.2: Conversation Summary (LangChain)

```python
from langchain.memory import ConversationSummaryMemory

# Automatically summarizes old conversations
memory = ConversationSummaryMemory(
    llm=llm,
    max_token_limit=500
)

# Old messages are compressed into summary
# Recent messages kept verbatim
```

### Recommendation for Veryfyn

```python
# brain/ai/memory.py

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from brain.ai.vector_store import VectorStore

@dataclass
class CoreMemory:
    """Core memory - always included in context."""
    user_name: str = ""
    preferences: Dict[str, Any] = field(default_factory=dict)
    goals: List[Dict[str, Any]] = field(default_factory=list)
    key_insights: List[str] = field(default_factory=list)
    
    def to_context(self) -> str:
        """Format as context string."""
        parts = []
        if self.user_name:
            parts.append(f"User: {self.user_name}")
        if self.preferences:
            parts.append(f"Preferences: {self.preferences}")
        if self.goals:
            parts.append(f"Active Goals: {[g['name'] for g in self.goals]}")
        if self.key_insights:
            parts.append(f"Key Insights: {self.key_insights[-5:]}")  # Last 5
        return "\n".join(parts)

@dataclass 
class WorkingMemory:
    """Working memory - recent interactions."""
    recent_messages: List[Dict[str, str]] = field(default_factory=list)
    current_context: List[str] = field(default_factory=list)
    last_query: str = ""
    last_response: str = ""
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to working memory."""
        self.recent_messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # Keep last 20 messages
        if len(self.recent_messages) > 20:
            self.recent_messages = self.recent_messages[-20:]
    
    def get_messages(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get recent messages for LLM context."""
        return [
            {"role": m["role"], "content": m["content"]}
            for m in self.recent_messages[-max_messages:]
        ]

class AssistantMemory:
    """
    Combined memory system for Veryfyn AI Assistant.
    
    Layers:
    1. Core Memory - Always in context (user preferences, goals)
    2. Working Memory - Recent messages and current context
    3. Long-term Memory - Vector search over historical data
    """
    
    def __init__(self, vector_store: VectorStore):
        self.core = CoreMemory()
        self.working = WorkingMemory()
        self.long_term = vector_store  # Archival memory
    
    def build_context(
        self,
        query: str,
        max_tokens: int = 2000
    ) -> str:
        """
        Build context for LLM prompt.
        
        Combines core memory + retrieved context + recent messages.
        """
        parts = []
        
        # 1. Core memory (always included)
        core_context = self.core.to_context()
        if core_context:
            parts.append(f"## User Profile\n{core_context}")
        
        # 2. Retrieve relevant long-term memory
        retrieved = self.long_term.search(query, n_results=3)
        if retrieved:
            context_items = [
                f"- {r.document.content[:200]}"
                for r in retrieved
            ]
            parts.append(f"## Relevant History\n" + "\n".join(context_items))
        
        # 3. Recent messages summary
        if self.working.recent_messages:
            recent = self.working.get_messages(max_messages=5)
            messages_str = "\n".join([
                f"{m['role']}: {m['content'][:100]}"
                for m in recent
            ])
            parts.append(f"## Recent Conversation\n{messages_str}")
        
        return "\n\n".join(parts)
    
    def update_core(self, key: str, value: Any) -> None:
        """Update core memory."""
        if key == "user_name":
            self.core.user_name = value
        elif key == "preferences":
            self.core.preferences.update(value)
        elif key == "goal":
            self.core.goals.append(value)
        elif key == "insight":
            self.core.key_insights.append(value)
```

---

## 5. Implementation Architecture

### Recommended Module Structure

```
brain/ai/
├── assistant.py          # Main AIAssistant class
├── chat_session.py       # Session management
├── context_retriever.py  # RAG context retrieval
├── memory.py             # Memory management
├── insight_generator.py  # Structured insights
├── prompts/
│   ├── __init__.py
│   ├── system_prompts.py # System prompt builders
│   └── templates.py      # Prompt templates
└── coach/
    ├── __init__.py
    ├── intervention_engine.py
    ├── user_assessment.py
    └── rules.py
```

### Core AIAssistant Class

```python
# brain/ai/assistant.py

from typing import Optional, List, Dict, Any, AsyncGenerator
from brain.ai.models import ProviderConfig, GenerationResult
from brain.ai.providers.factory import ProviderFactory
from brain.ai.vector_store import VectorStore
from brain.ai.memory import AssistantMemory
from brain.ai.context_retriever import ContextRetriever
from brain.ai.chat_session import ChatSession, MessageRole
from brain.ai.prompts.system_prompts import SystemPromptBuilder

class AIAssistant:
    """
    Main AI Assistant for Veryfyn.
    
    Combines:
    - Multi-provider LLM support
    - RAG context retrieval
    - Memory management
    - Chat session persistence
    """
    
    def __init__(
        self,
        provider_config: ProviderConfig,
        vector_store: Optional[VectorStore] = None
    ):
        self.provider = ProviderFactory.create(provider_config)
        self.vector_store = vector_store or VectorStore()
        self.memory = AssistantMemory(self.vector_store)
        self.retriever = ContextRetriever(self.vector_store)
        self.session: Optional[ChatSession] = None
    
    def initialize(self) -> bool:
        """Initialize the assistant."""
        if not self.provider.initialize():
            return False
        if not self.vector_store.initialize():
            return False
        return True
    
    def start_session(self, session_id: Optional[str] = None) -> ChatSession:
        """Start a new chat session."""
        import uuid
        self.session = ChatSession(
            session_id=session_id or str(uuid.uuid4())
        )
        return self.session
    
    def chat(
        self,
        message: str,
        include_context: bool = True
    ) -> GenerationResult:
        """
        Send a message and get a response.
        
        Args:
            message: User message
            include_context: Whether to include RAG context
        
        Returns:
            GenerationResult with response
        """
        if self.session is None:
            self.start_session()
        
        # Add user message to session
        self.session.add_message(MessageRole.USER, message)
        
        # Build context
        context = ""
        if include_context:
            context = self.memory.build_context(message)
        
        # Build system prompt
        system_prompt = SystemPromptBuilder.build(context=context)
        
        # Get messages for LLM
        messages = self.session.get_messages_for_llm(max_messages=10)
        
        # Add system prompt
        messages.insert(0, {
            "role": "system",
            "content": system_prompt
        })
        
        # Generate response
        result = self.provider.generate(
            prompt=message,
            context=[m["content"] for m in messages if m["role"] != "system"]
        )
        
        # Add response to session
        if result.success:
            self.session.add_message(MessageRole.ASSISTANT, result.content)
            self.memory.working.add_message("user", message)
            self.memory.working.add_message("assistant", result.content)
        
        return result
    
    async def chat_stream(
        self,
        message: str,
        include_context: bool = True
    ) -> AsyncGenerator[str, None]:
        """Stream response chunks."""
        # Similar to chat() but yields response chunks
        async for chunk in self.provider.generate_stream(message):
            yield chunk
```

---

## 6. Key Dependencies

```txt
# Core AI
langchain>=0.1.0
langchain-core>=0.1.0
llama-index>=0.10.0

# Vector Store
chromadb>=0.4.0

# Embeddings
sentence-transformers>=2.2.0

# LLM Providers
openai>=1.0.0
ollama>=0.1.0
anthropic>=0.18.0

# Token Counting
tiktoken>=0.5.0

# Utilities
pydantic>=2.0.0
python-dateutil>=2.8.0
```

---

## 7. Next Steps

1. **Implement `brain/ai/assistant.py`** - Main AIAssistant class
2. **Implement `brain/ai/chat_session.py`** - Session persistence
3. **Implement `brain/ai/context_retriever.py`** - RAG retrieval
4. **Implement `brain/ai/prompts/`** - Prompt templates
5. **Create `tracking_app/pages/ai_assistant.py`** - Streamlit UI
6. **Add tests** - `tests/test_ai_assistant.py`

---

## References

- LangChain Documentation: https://python.langchain.com/
- LlamaIndex Documentation: https://docs.llamaindex.ai/
- PrivateGPT: https://github.com/zylon-ai/private-gpt
- MemGPT: https://memgpt.readme.io/

---

*Research completed: February 20, 2026*