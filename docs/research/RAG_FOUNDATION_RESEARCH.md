# RAG Foundation Research

**Phase 6.1: Retrieval-Augmented Generation (RAG) Implementation Research**

**Created:** February 20, 2026
**Status:** Complete

---

## Overview

This document consolidates research on RAG (Retrieval-Augmented Generation) systems for personal tracking applications. RAG enables AI assistants to query and reason over user data by combining:

1. **Vector Database** - Semantic search over embedded documents
2. **Embedding Models** - Convert text to vector representations
3. **LLM Integration** - Generate responses using retrieved context

---

## Core Concepts

### 1. Retrieval-Augmented Generation (RAG)

RAG is a technique that enhances LLM responses by retrieving relevant context from a knowledge base before generating answers.

```
User Query → Embedding → Vector Search → Context Retrieval → LLM → Response
```

**Benefits:**
- Grounds responses in actual data
- Reduces hallucinations
- Enables querying private data
- No model training required

### 2. Vector Databases

Vector databases store documents as high-dimensional vectors, enabling semantic similarity search.

| Database | Type | Strengths | Use Case |
|----------|------|-----------|----------|
| **ChromaDB** | Embedded | Easy setup, Python-native | Local apps |
| **Pinecone** | Cloud | Scalable, managed | Production |
| **Weaviate** | Hybrid | GraphQL, modules | Enterprise |
| **Qdrant** | Rust | Fast, filtering | High-performance |
| **FAISS** | Library | Meta's algorithm | Research |

**Recommendation:** ChromaDB for TrackLife (embedded, Python-native, works locally)

### 3. Embedding Models

Embedding models convert text into dense vector representations.

| Model | Dimensions | Speed | Quality | License |
|-------|------------|-------|---------|---------|
| **all-MiniLM-L6-v2** | 384 | Fast | Good | Apache 2.0 |
| **all-mpnet-base-v2** | 768 | Medium | Better | Apache 2.0 |
| **e5-large-v2** | 1024 | Slower | Best | MIT |
| **OpenAI text-embedding-3-small** | 1536 | API | Excellent | Commercial |
| **Cohere embed-v3** | 1024 | API | Excellent | Commercial |

**Recommendation:** `all-MiniLM-L6-v2` for local (fast, good quality), OpenAI API as cloud option

### 4. LLM Providers

| Provider | Type | Models | API Key | Local |
|----------|------|--------|---------|-------|
| **Ollama** | Local | llama3, mistral, etc. | No | ✅ |
| **OpenAI** | Cloud | gpt-4o, gpt-4o-mini | Yes | ❌ |
| **Anthropic** | Cloud | claude-3-opus, claude-3-haiku | Yes | ❌ |
| **Google** | Cloud | gemini-1.5-pro, gemini-1.5-flash | Yes | ❌ |
| **Groq** | Cloud | llama-3.1-8b, mixtral | Yes | ❌ |

---

## Key Public Repositories

### 1. ChromaDB (chromadb/chroma)
- **URL:** https://github.com/chromadb/chroma
- **Purpose:** Vector database for AI applications
- **Key Features:**
  - Embedded mode (no server required)
  - Python-first API
  - Built-in embedding functions
  - Persistent storage

```python
import chromadb
from chromadb.utils import embedding_functions

# Initialize
client = chromadb.PersistentClient(path="./chroma_db")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Create collection
collection = client.create_collection(
    name="habits",
    embedding_function=ef
)

# Add documents
collection.add(
    documents=["I completed my morning workout", "Skipped meditation today"],
    metadatas=[{"type": "habit"}, {"type": "habit"}],
    ids=["habit_1", "habit_2"]
)

# Query
results = collection.query(
    query_texts=["exercise habits"],
    n_results=5
)
```

### 2. LangChain (langchain-ai/langchain)
- **URL:** https://github.com/langchain-ai/langchain
- **Purpose:** Framework for LLM applications
- **Key Features:**
  - Multi-provider support
  - RAG pipelines
  - Document loaders
  - Memory management

```python
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

# Embeddings
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Vector store
vectorstore = Chroma(
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# LLM
llm = Ollama(model="llama3")

# RAG chain
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever()
)

response = qa.invoke("What habits did I miss this week?")
```

### 3. LlamaIndex (run-llama/llama_index)
- **URL:** https://github.com/run-llama/llama_index
- **Purpose:** Data framework for LLM applications
- **Key Features:**
  - Document indexing
  - Query engines
  - Multi-modal support
  - Custom retrievers

### 4. Ollama Python (ollama/ollama-python)
- **URL:** https://github.com/ollama/ollama-python
- **Purpose:** Python SDK for Ollama
- **Key Features:**
  - Simple API
  - Streaming support
  - Embedding generation

```python
import ollama

# Generate response
response = ollama.chat(model='llama3', messages=[
    {'role': 'user', 'content': 'Why is my energy low?'}
])

# Generate embeddings
embedding = ollama.embeddings(
    model='nomic-embed-text',
    prompt='I completed my morning workout'
)
```

### 5. Sentence Transformers (UKPLab/sentence-transformers)
- **URL:** https://github.com/UKPLab/sentence-transformers
- **Purpose:** Embedding generation
- **Key Features:**
  - 100+ pre-trained models
  - Fine-tuning support
  - Multi-lingual models

```python
from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
embeddings = model.encode([
    "I completed my morning workout",
    "Skipped meditation today"
])
```

### 6. PrivateGPT (zylon-ai/private-gpt)
- **URL:** https://github.com/zylon-ai/private-gpt
- **Purpose:** Private Q&A with documents
- **Key Features:**
  - Fully local RAG
  - Multiple LLM support
  - Document ingestion
  - API server

### 7. Quivr (QuivrHQ/quivr)
- **URL:** https://github.com/QuivrHQ/quivr
- **Purpose:** Personal AI assistant with RAG
- **Key Features:**
  - Multi-modal (text, images, audio)
  - Supabase vector store
  - Chat history

---

## Architecture Patterns

### Pattern 1: Simple RAG Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Documents  │───▶│  Embedding  │───▶│  Vector DB  │
└─────────────┘    │   Model     │    │  (ChromaDB) │
                   └─────────────┘    └──────┬──────┘
                                             │
┌─────────────┐    ┌─────────────┐           │
│  User Query │───▶│  Embedding  │           │
└─────────────┘    │   Model     │───┬───────┘
                   └─────────────┘   │
                                     ▼
                   ┌─────────────────────────┐
                   │    Semantic Search      │
                   │  (Top-K Relevant Docs)  │
                   └───────────┬─────────────┘
                               │
                               ▼
                   ┌─────────────────────────┐
                   │   Context + Query       │
                   │   ─────────────────────  │
                   │   Query: "Why tired?"   │
                   │   Context: Sleep logs   │
                   │            Mood data    │
                   └───────────┬─────────────┘
                               │
                               ▼
                   ┌─────────────────────────┐
                   │      LLM Provider       │
                   │   (Ollama / OpenAI)     │
                   └───────────┬─────────────┘
                               │
                               ▼
                   ┌─────────────────────────┐
                   │      AI Response        │
                   └─────────────────────────┘
```

### Pattern 2: Multi-Provider Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AIProviderFactory                            │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Ollama     │  │   OpenAI     │  │  Anthropic   │          │
│  │   Provider   │  │   Provider   │  │   Provider   │          │
│  │   (Local)    │  │   (Cloud)    │  │   (Cloud)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│                           ▼                                     │
│                  ┌─────────────────┐                            │
│                  │  AIProviderBase │                            │
│                  │  (Abstract)      │                            │
│                  └─────────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Recommendations

### 1. Module Structure

```
brain/ai/
├── __init__.py           # Module exports
├── models.py             # Data models (ProviderConfig, etc.)
├── providers/
│   ├── __init__.py
│   ├── base.py           # AIProviderBase ABC
│   ├── factory.py        # Provider factory
│   ├── ollama_provider.py
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── gemini_provider.py
│   └── groq_provider.py
├── api_keys.py           # Secure key management
├── embeddings.py         # Embedding engine
└── vector_store.py       # ChromaDB wrapper
```

### 2. Provider Interface

```python
from abc import ABC, abstractmethod
from typing import List, Optional, AsyncGenerator

class AIProviderBase(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def generate(self, prompt: str, context: List[str] = None) -> str:
        """Generate response from prompt and context."""
        pass
    
    @abstractmethod
    async def generate_stream(self, prompt: str, context: List[str] = None) -> AsyncGenerator[str, None]:
        """Stream response for real-time display."""
        pass
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Generate embedding vector for text."""
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        pass
```

### 3. Embedding Strategy

For personal tracking data, use **hybrid embeddings**:

| Data Type | Embedding Strategy |
|-----------|-------------------|
| Habits | Embed habit name + description + completion notes |
| Tasks | Embed title + description + tags |
| Health | Embed formatted summary (e.g., "Slept 7 hours, mood: good") |
| Journal | Embed full text with date context |

**Document Format:**
```python
def format_habit_document(habit, completion):
    return f"""
Date: {completion.date}
Habit: {habit.name}
Status: {'Completed' if completion.completed else 'Missed'}
Notes: {completion.notes or 'No notes'}
Streak: {habit.streak} days
Score: {habit.score:.0%}
""".strip()
```

### 4. API Key Security

```python
import os
import json
import base64
from pathlib import Path

class APIKeyManager:
    ENV_KEY_MAPPING = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
    }
    
    def get_key(self, provider: str) -> Optional[str]:
        # Priority: env var > streamlit secrets > encrypted file
        if env_key := self.ENV_KEY_MAPPING.get(provider):
            if key := os.environ.get(env_key):
                return key
        
        # Try Streamlit secrets
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and provider in st.secrets:
                return st.secrets[provider]
        except ImportError:
            pass
        
        # Try encrypted local storage
        return self._load_from_storage(provider)
```

---

## Performance Considerations

### Embedding Generation

| Approach | Speed | Memory | Use Case |
|----------|-------|--------|----------|
| **Batch** | Fast | High | Initial indexing |
| **Incremental** | Medium | Low | Real-time updates |
| **Background** | Async | Variable | Large datasets |

### Vector Search

| Parameter | Impact | Recommendation |
|-----------|--------|----------------|
| `n_results` | More = slower | 5-10 for chat |
| `where` filter | Faster | Use for date filtering |
| `include` fields | Less transfer | Only needed fields |

### Memory Usage

| Component | Memory | Optimization |
|-----------|--------|--------------|
| Embedding model | ~500MB | Load once, reuse |
| ChromaDB index | Variable | Periodic cleanup |
| LLM (Ollama) | 4-8GB | Run separately |

---

## Testing Strategy

### Unit Tests

```python
def test_ollama_provider_no_key_required():
    """Ollama should work without API key."""
    config = ProviderConfig(provider=AIProvider.OLLAMA)
    assert config.validate() == True

def test_openai_provider_requires_key():
    """OpenAI should require API key."""
    config = ProviderConfig(provider=AIProvider.OPENAI)
    assert config.validate() == False
    config.api_key = "sk-test"
    assert config.validate() == True

def test_embedding_generation():
    """Embedding should produce correct dimensions."""
    engine = EmbeddingEngine()
    embedding = engine.embed("Test text")
    assert len(embedding) == 384  # all-MiniLM-L6-v2

def test_vector_store_crud():
    """Vector store should support CRUD operations."""
    store = VectorStore()
    store.add("doc1", "Test content", {"source": "test"})
    results = store.search("Test", n_results=1)
    assert len(results) == 1
    store.delete("doc1")
    assert store.count() == 0
```

### Integration Tests

```python
def test_full_rag_pipeline():
    """Test complete RAG pipeline."""
    # 1. Create provider
    provider = ProviderFactory.create(ProviderConfig(provider=AIProvider.OLLAMA))
    
    # 2. Create embedding engine
    engine = EmbeddingEngine()
    
    # 3. Create vector store
    store = VectorStore()
    
    # 4. Index documents
    docs = ["I slept 7 hours", "I exercised today"]
    store.add_batch(docs, embeddings=[engine.embed(d) for d in docs])
    
    # 5. Query
    query = "How did I sleep?"
    context = store.search(query, n_results=1)
    
    # 6. Generate response
    response = provider.generate(query, context=[context[0].content])
    
    assert len(response) > 0
    assert "7 hours" in response.lower()
```

---

## Dependencies

```txt
# Core RAG
chromadb>=0.4.0
sentence-transformers>=2.2.0

# Local LLM
ollama>=0.1.0

# Cloud Providers (optional)
openai>=1.0.0
anthropic>=0.18.0
google-generativeai>=0.3.0
groq>=0.4.0

# ML Runtime
torch>=2.0.0
numpy>=1.24.0
```

---

## References

- ChromaDB: https://docs.trychroma.com/
- Ollama: https://ollama.ai/
- Sentence Transformers: https://www.sbert.net/
- LangChain: https://python.langchain.com/
- PrivateGPT: https://github.com/zylon-ai/private-gpt

---

## Cross-References

| Document | Content |
|----------|---------|
| [PHASE_6_AI_INTEGRATION.md](../../phases/PHASE_6_AI_INTEGRATION.md) | Implementation specification |
| [AI_AND_PREDICTION.md](AI_AND_PREDICTION.md) | AI research |
| [TECHNICAL_ARCHITECTURES.md](TECHNICAL_ARCHITECTURES.md) | Architecture patterns |

---

*Research completed: February 20, 2026*