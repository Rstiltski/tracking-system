# AI and Prediction Research

**Artificial intelligence and predictive analytics for personal tracking systems.**

---

## Overview

This document covers AI integration patterns, predictive analytics models, and machine learning approaches applicable to personal tracking systems.

**Updated:** March 8, 2026 - Added AI Assistant Memory Management System (DECISION_037)

---

## 🧠 AI Assistant Memory Management System (DECISION_037)

**Enhanced thinking infrastructure for AI assistants working on this project.**

### Architecture Overview

The AI Assistant Memory Management System implements advanced AI agent patterns from 2024-2025 research:

```
┌─────────────────────────────────────────────────────────────┐
│                  AI ASSISTANT MEMORY SYSTEM                  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Memory    │  │  Reference  │  │    Task     │        │
│  │   Manager   │  │    Index    │  │ Decomposer  │        │
│  │             │  │             │  │             │        │
│  │ - Compression│  │ - Lazy load │  │ - Hierarchy │        │
│  │ - Relevance  │  │ - Metadata  │  │ - Deps      │        │
│  │ - Retrieval  │  │ - Tags      │  │ - Templates │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Session Context                         │   │
│  │  - Sliding window (10 interactions)                  │   │
│  │  - Summarization (older interactions)                │   │
│  │  - Persistence (across conversations)                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Files

| Component | File | Lines | Purpose |
|-----------|------|-------|---------|
| Memory Manager | `brain/ai_assistant/memory_manager.py` | ~300 | Compression, retrieval, relevance scoring |
| Reference Index | `brain/ai_assistant/reference_index.py` | ~350 | Reference-by-substitution pattern |
| Task Decomposer | `brain/ai_assistant/task_decomposer.py` | ~450 | Hierarchical decomposition |
| Session Context | `brain/ai_assistant/session_context.py` | ~350 | Sliding window, persistence |

**Total:** ~1,450 lines of Python code

### AI Agent Patterns Implemented

| Pattern | Research Source | Implementation |
|---------|-----------------|----------------|
| **ReAct Loop** | Yao et al. (2023) | Thought→Action→Observation→Reflection |
| **Memory Compression** | AI Agent Research | Sliding window + summarization |
| **Reference-by-Substitution** | AI Agent Research | Lightweight IDs for large files |
| **Intent-Driven Retrieval** | AI Agent Research | Goal-specific memory lookup |
| **Hierarchical Decomposition** | Wang et al. (2023) | Task trees with dependencies |
| **Stateful Memory** | AI Agent Research | Session persistence |

### Usage Example

```python
from brain.ai_assistant import (
    MemoryManager,
    ReferenceIndex,
    TaskDecomposer,
    SessionContext
)

# Initialize components
memory = MemoryManager()
index = ReferenceIndex()
decomposer = TaskDecomposer()
context = SessionContext()

# Before responding to user
relevant = memory.get_relevant_decisions(intent="Adding new feature")
task_tree = decomposer.decompose("Add correlation analysis")
context.add_interaction(role="user", content="Add new feature")

# Show ReAct thinking
print("🤔 THOUGHT: Analyzing request...")
print("📋 ACTION: Loading relevant decisions...")
print("👁️ OBSERVATION: Found DECISION_030 about navigation...")
print("💭 REFLECTION: This aligns with existing patterns...")

# After completing task
memory.log_decision(
    choice="Using pattern X",
    reasoning="Matches existing architecture",
    implication="Consistent with MOD_001"
)
```

### Memory Compression Strategy

**Sliding Window:**
- Keep last 10 interactions in active memory
- Summarize interactions 11-50
- Archive interactions 51+ with timestamp decay

**Relevance Scoring:**
```python
relevance_score = (
    keyword_match * 0.4 +      # Keyword matching
    intent_match * 0.3 +       # Intent alignment
    recency * 0.2 +            # Time decay
    decision_impact * 0.1      # Impact weight
)
```

**Timestamp Decay:**
```python
decay_factor = 0.5 ** (age.total_seconds() / half_life.total_seconds())
# half_life = 24 hours
```

### Task Decomposition Templates

Built-in templates for common task types:

| Template | Pattern Keywords | Subtasks |
|----------|-----------------|----------|
| Feature Addition | add, create, implement | 8 subtasks |
| Bug Fix | fix, bug, error, issue | 6 subtasks |
| Analysis | analyze, review, examine | 5 subtasks |
| Refactoring | refactor, restructure | 6 subtasks |
| Documentation | document, write docs | 5 subtasks |

### Integration with 5-File Memory

| 5-File Memory | Enhancement |
|---------------|-------------|
| **ACTIVE PROMPT** | SessionContext manages sliding window |
| **SESSION STATE** | SessionContext persists to session_state.json |
| **DECISION LOG** | MemoryManager reads, compresses, retrieves |
| **PRIME DIRECTIVE** | ReferenceIndex stores lightweight references |
| **PATTERN LIBRARY** | TaskDecomposer applies templates |

### Documentation

- **Main Documentation:** `brain/ai_assistant/README.md`
- **Implementation:** `brain/ai_assistant/*.py`
- **Decision Log:** DECISION_037 in `decisions.log`
- **Quick Reference:** `NEXT_STEP.md`

---

## Predictive Context Sensitivity (PCS)

### Definition

**Predictive Context Sensitivity (PCS)** measures how predictable a behavior is based on context variables, rather than just counting days.

### Research Foundation

From academic research on habit formation:
- Traditional view: "66 days to form a habit"
- PCS view: A habit is formed when behavior becomes predictable from context

### Algorithm: LASSO Regression

LASSO (Least Absolute Shrinkage and Selection Operator) regression identifies which context variables best predict behavior.

```python
from sklearn.linear_model import Lasso
import numpy as np

def calculate_pcs(behavior_data, context_data):
    """
    Calculate Predictive Context Sensitivity score.
    
    behavior_data: Binary array of behavior occurrence (1 = did, 0 = didn't)
    context_data: Matrix of context variables (time, location, previous actions, etc.)
    """
    # Fit LASSO model
    model = Lasso(alpha=0.1)
    model.fit(context_data, behavior_data)
    
    # R² score indicates predictability
    pcs_score = model.score(context_data, behavior_data)
    
    # Identify important context variables
    important_features = np.where(model.coef_ != 0)[0]
    
    return {
        "pcs_score": pcs_score,  # 0.0 to 1.0
        "important_features": important_features,
        "coefficients": model.coef_
    }
```

### Context Variables

| Variable | Description | Example Values |
|----------|-------------|----------------|
| **Time of Day** | Hour bucket | Morning, Afternoon, Evening |
| **Day of Week** | Weekday/Weekend | Monday, Saturday |
| **Location** | GPS or semantic | Home, Work, Gym |
| **Previous Action** | What came before | "Woke up", "Finished work" |
| **Sleep Quality** | Previous night's sleep | 1-10 scale |
| **Stress Level** | Self-reported or HRV | Low, Medium, High |
| **Weather** | Environmental context | Sunny, Rainy, Cold |

### Implementation for TrackLife

```javascript
// Track context for each habit completion
const contextFeatures = {
    hour: new Date().getHours(),
    dayOfWeek: new Date().getDay(),
    location: await getCurrentLocation(),
    previousAction: getLastLoggedAction(),
    sleepQuality: getSleepQuality(),
    stressLevel: getStressLevel()
};

// Calculate PCS score
function calculatePCS(habitId) {
    const completions = getHabitCompletions(habitId);
    const contexts = completions.map(c => c.context);
    
    // Use simplified correlation-based approach
    // (Full LASSO would require ML library)
    let predictability = 0;
    
    // Check time consistency
    const hours = contexts.map(c => c.hour);
    const hourVariance = variance(hours);
    predictability += (1 - normalizeVariance(hourVariance)) * 0.3;
    
    // Check location consistency
    const locations = contexts.map(c => c.location);
    const locationConsistency = modeFrequency(locations);
    predictability += locationConsistency * 0.3;
    
    // Check day-of-week consistency
    const days = contexts.map(c => c.dayOfWeek);
    const dayConsistency = modeFrequency(days);
    predictability += dayConsistency * 0.2;
    
    // Check previous action consistency
    const prevActions = contexts.map(c => c.previousAction);
    const actionConsistency = modeFrequency(prevActions);
    predictability += actionConsistency * 0.2;
    
    return predictability; // 0.0 to 1.0
}
```

### Output Interpretation

| PCS Score | Interpretation |
|-----------|----------------|
| 0.0 - 0.3 | Not yet a habit, highly variable |
| 0.3 - 0.5 | Developing, some patterns emerging |
| 0.5 - 0.7 | Moderate habit strength |
| 0.7 - 0.85 | Strong habit, context-driven |
| 0.85 - 1.0 | Automatic behavior, fully habitual |

---

## Burnout Prediction

### Definition

Burnout prediction uses multiple data streams to detect early warning signs of burnout before it occurs.

### Model Architecture

```python
# Random Forest-based burnout prediction
from sklearn.ensemble import RandomForestClassifier
import numpy as np

class BurnoutPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.feature_names = [
            'sleep_duration_avg',
            'sleep_quality_avg',
            'task_completion_rate',
            'work_hours_avg',
            'hrv_avg',  # Heart Rate Variability
            'mood_avg',
            'exercise_frequency',
            'social_interaction_score'
        ]
    
    def extract_features(self, user_data, days=14):
        """Extract features from last N days of data."""
        return np.array([
            np.mean(user_data['sleep_duration'][-days:]),
            np.mean(user_data['sleep_quality'][-days:]),
            np.mean(user_data['task_completion'][-days:]),
            np.sum(user_data['work_hours'][-days:]) / days,
            np.mean(user_data['hrv'][-days:]) if 'hrv' in user_data else 50,
            np.mean(user_data['mood'][-days:]),
            np.sum(user_data['exercise'][-days:]) / days,
            np.mean(user_data['social'][-days:])
        ])
    
    def predict_burnout_risk(self, user_data):
        """Predict burnout risk score (0-100)."""
        features = self.extract_features(user_data)
        
        # If model not trained, use heuristic
        if not hasattr(self, 'is_trained'):
            return self.heuristic_burnout_score(features)
        
        probability = self.model.predict_proba([features])[0][1]
        return int(probability * 100)
    
    def heuristic_burnout_score(self, features):
        """Heuristic burnout calculation without ML model."""
        score = 0
        
        # Sleep factors (40% weight)
        sleep_avg = features[0]
        if sleep_avg < 6:
            score += 40
        elif sleep_avg < 7:
            score += 20
        elif sleep_avg >= 7.5:
            score -= 10
        
        # Task completion (25% weight)
        task_rate = features[2]
        if task_rate < 0.5:
            score += 25
        elif task_rate < 0.7:
            score += 10
        
        # Work hours (20% weight)
        work_hours = features[3]
        if work_hours > 10:
            score += 20
        elif work_hours > 8:
            score += 10
        
        # Mood (15% weight)
        mood_avg = features[5]
        if mood_avg < 3:
            score += 15
        elif mood_avg < 5:
            score += 5
        
        return min(100, max(0, score))
```

### Input Features

| Feature | Source | Weight |
|---------|--------|--------|
| **Sleep Duration** | Health tracking | High |
| **Sleep Quality** | Health tracking | High |
| **Task Completion Rate** | Task tracking | Medium |
| **Work Hours** | Time tracking | Medium |
| **HRV** | Wearable (optional) | High |
| **Mood** | Self-report | Medium |
| **Exercise Frequency** | Health tracking | Low |
| **Social Interaction** | Calendar/manual | Low |

### Risk Levels

| Score | Level | Action |
|-------|-------|--------|
| 0-30 | Low | Continue normal tracking |
| 31-50 | Moderate | Monitor closely, suggest rest |
| 51-70 | High | Recommend recovery activities |
| 71-100 | Critical | Alert user, suggest professional help |

### Intervention System

```javascript
const burnoutInterventions = {
    low: {
        message: "You're doing great! Keep up the good work.",
        suggestions: []
    },
    moderate: {
        message: "You might be pushing too hard. Consider taking breaks.",
        suggestions: [
            "Schedule a 15-minute walk",
            "Go to bed 30 minutes earlier tonight",
            "Take a screen break"
        ]
    },
    high: {
        message: "Warning: You're showing signs of burnout. Please prioritize rest.",
        suggestions: [
            "Cancel non-essential tasks today",
            "Take a full rest day tomorrow",
            "Practice a relaxation technique"
        ],
        autoActions: [
            "Reduce daily task targets by 25%",
            "Disable non-critical notifications"
        ]
    },
    critical: {
        message: "Critical: Please take immediate action for your wellbeing.",
        suggestions: [
            "Stop all non-essential activities",
            "Contact a friend or family member",
            "Consider speaking with a professional"
        ],
        autoActions: [
            "Switch to 'Recovery Mode'",
            "Pause all habit reminders",
            "Show crisis resources"
        ]
    }
};
```

---

## Correlation Engine

### Overview

Automatically discover relationships between different tracked metrics.

### Correlation Methods

#### Pearson Correlation

For linear relationships between continuous variables.

```javascript
function pearsonCorrelation(x, y) {
    const n = x.length;
    
    // Calculate means
    const meanX = x.reduce((a, b) => a + b, 0) / n;
    const meanY = y.reduce((a, b) => a + b, 0) / n;
    
    // Calculate components
    let sumNum = 0, sumDenX = 0, sumDenY = 0;
    
    for (let i = 0; i < n; i++) {
        const dx = x[i] - meanX;
        const dy = y[i] - meanY;
        sumNum += dx * dy;
        sumDenX += dx * dx;
        sumDenY += dy * dy;
    }
    
    return sumNum / Math.sqrt(sumDenX * sumDenY);
}
```

#### Spearman Correlation

For ordinal data or non-linear monotonic relationships.

```javascript
function spearmanCorrelation(x, y) {
    // Convert to ranks
    const rankX = getRanks(x);
    const rankY = getRanks(y);
    
    // Apply Pearson to ranks
    return pearsonCorrelation(rankX, rankY);
}

function getRanks(arr) {
    const sorted = [...arr].sort((a, b) => a - b);
    return arr.map(v => sorted.indexOf(v) + 1);
}
```

#### Time-Lag Correlation

For detecting delayed effects (e.g., sleep affects tomorrow's mood).

```javascript
function laggedCorrelation(x, y, lagDays) {
    // Shift y by lagDays
    const xSlice = x.slice(0, -lagDays);
    const ySlice = y.slice(lagDays);
    
    return pearsonCorrelation(xSlice, ySlice);
}

// Find optimal lag
function findOptimalLag(x, y, maxLag = 7) {
    let bestCorr = -1;
    let bestLag = 0;
    
    for (let lag = 0; lag <= maxLag; lag++) {
        const corr = Math.abs(laggedCorrelation(x, y, lag));
        if (corr > bestCorr) {
            bestCorr = corr;
            bestLag = lag;
        }
    }
    
    return { lag: bestLag, correlation: bestCorr };
}
```

### Insight Generation

```javascript
function generateInsights(metrics) {
    const insights = [];
    const pairs = getMetricPairs(metrics);
    
    for (const [metricA, metricB] of pairs) {
        // Direct correlation
        const directCorr = pearsonCorrelation(metricA.values, metricB.values);
        
        if (Math.abs(directCorr) > 0.5) {
            insights.push({
                type: 'correlation',
                metrics: [metricA.name, metricB.name],
                strength: directCorr,
                message: formatCorrelationMessage(metricA.name, metricB.name, directCorr)
            });
        }
        
        // Time-lag correlation
        const { lag, correlation } = findOptimalLag(metricA.values, metricB.values);
        
        if (Math.abs(correlation) > 0.5 && lag > 0) {
            insights.push({
                type: 'lagged_correlation',
                metrics: [metricA.name, metricB.name],
                lag: lag,
                strength: correlation,
                message: formatLaggedMessage(metricA.name, metricB.name, lag, correlation)
            });
        }
    }
    
    return insights.sort((a, b) => Math.abs(b.strength) - Math.abs(a.strength));
}

function formatCorrelationMessage(a, b, corr) {
    const direction = corr > 0 ? 'higher' : 'lower';
    const strength = Math.abs(corr) > 0.7 ? 'strongly' : 'moderately';
    return `Your ${a} is ${strength} correlated with ${b}. ` +
           `When ${a} is high, ${b} tends to be ${direction}.`;
}

function formatLaggedMessage(a, b, lag, corr) {
    const direction = corr > 0 ? 'higher' : 'lower';
    return `Your ${a} affects your ${b} ${lag} day${lag > 1 ? 's' : ''} later. ` +
           `Good ${a} leads to ${direction} ${b} the next day.`;
}
```

---

## Local RAG (Retrieval-Augmented Generation)

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER QUERY                               │
│              "Why have I been tired lately?"                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  EMBEDDING MODEL                             │
│              (all-MiniLM-L6-v2)                              │
│         Converts query to vector representation             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    VECTOR DATABASE                           │
│                     (ChromaDB)                               │
│     Semantic search for relevant personal data              │
│                                                              │
│  Results:                                                   │
│  - Sleep data: avg 5.2 hrs last week                        │
│  - Mood logs: "feeling exhausted" (3 entries)               │
│  - Exercise: skipped 4 workouts                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      LOCAL LLM                               │
│                      (Ollama)                                │
│     Generates response based on retrieved context           │
│                                                              │
│  Response:                                                  │
│  "Based on your data, you've been averaging only 5.2 hours  │
│   of sleep this week, which is below your usual 7 hours.    │
│   You've also skipped 4 workouts and logged feeling         │
│   exhausted multiple times. Try prioritizing sleep..."      │
└─────────────────────────────────────────────────────────────┘
```

### Implementation

```javascript
// RAG system for TrackLife
class LocalRAG {
    constructor() {
        this.embedder = null;  // Will use Transformers.js or API
        this.vectorDb = null;  // ChromaDB or similar
        this.llm = null;       // Ollama connection
    }
    
    async initialize() {
        // Initialize embedding model
        // Option 1: Use Transformers.js (runs in browser)
        // Option 2: Use Ollama embeddings API
        
        // Initialize vector database
        // Option 1: ChromaDB (requires backend)
        // Option 2: IndexedDB with vector search
        
        // Initialize LLM connection
        this.llm = new OllamaConnection('http://localhost:11434');
    }
    
    async indexData(data) {
        // Convert all tracked data to embeddings
        const documents = this.prepareDocuments(data);
        
        for (const doc of documents) {
            const embedding = await this.getEmbedding(doc.content);
            await this.vectorDb.add({
                id: doc.id,
                embedding: embedding,
                metadata: doc.metadata,
                content: doc.content
            });
        }
    }
    
    async query(question) {
        // 1. Embed the question
        const queryEmbedding = await this.getEmbedding(question);
        
        // 2. Search for relevant context
        const results = await this.vectorDb.search(queryEmbedding, { k: 5 });
        
        // 3. Build context
        const context = results.map(r => r.content).join('\n\n');
        
        // 4. Generate response
        const response = await this.llm.generate({
            model: 'llama3',
            prompt: this.buildPrompt(question, context),
            stream: false
        });
        
        return response;
    }
    
    buildPrompt(question, context) {
        return `You are a helpful personal health assistant. Answer the user's question based on their personal data.

Personal Data Context:
${context}

User Question: ${question}

Provide a helpful, personalized response based on the data above. If the data doesn't contain relevant information, say so.`;
    }
}
```

### Ollama Integration

```javascript
class OllamaConnection {
    constructor(baseUrl = 'http://localhost:11434') {
        this.baseUrl = baseUrl;
    }
    
    async generate({ model, prompt, stream = false }) {
        const response = await fetch(`${this.baseUrl}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model, prompt, stream })
        });
        
        return await response.json();
    }
    
    async embed({ model, prompt }) {
        const response = await fetch(`${this.baseUrl}/api/embeddings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model, prompt })
        });
        
        const data = await response.json();
        return data.embedding;
    }
}
```

---

## Digital Coach

### Concept

The Digital Coach is a proactive AI that:
1. Monitors user's data continuously
2. Detects patterns and anomalies
3. Intervenes with suggestions before problems occur
4. Adapts to user's preferences and responses

### Implementation

```javascript
class DigitalCoach {
    constructor() {
        this.rules = [];
        this.learningHistory = [];
    }
    
    async analyze(userData) {
        const interventions = [];
        
        // Check burnout risk
        const burnoutRisk = this.calculateBurnoutRisk(userData);
        if (burnoutRisk > 50) {
            interventions.push({
                type: 'burnout_warning',
                severity: burnoutRisk > 70 ? 'high' : 'medium',
                message: this.generateBurnoutMessage(burnoutRisk),
                suggestions: this.getRecoverySuggestions(userData)
            });
        }
        
        // Check habit patterns
        const habitInsights = this.analyzeHabits(userData.habits);
        interventions.push(...habitInsights);
        
        // Check correlations
        const correlations = this.findCorrelations(userData);
        interventions.push(...correlations);
        
        return interventions;
    }
    
    async generateDailyBriefing(userData) {
        const summary = await this.rag.query(
            `Summarize my yesterday and provide recommendations for today. ` +
            `Include: sleep quality, habit completion, mood, and any patterns.`
        );
        
        return {
            date: new Date().toISOString().split('T')[0],
            summary: summary,
            recommendations: this.getDailyRecommendations(userData),
            focusAreas: this.identifyFocusAreas(userData)
        };
    }
    
    async checkInterventionNeeded(userData) {
        // Proactive intervention logic
        const today = new Date();
        const hour = today.getHours();
        
        // Morning check (8-9 AM)
        if (hour >= 8 && hour < 9) {
            if (!userData.habits.some(h => h.name === 'Morning Routine' && h.completedToday)) {
                return {
                    type: 'reminder',
                    message: "Good morning! Don't forget your morning routine.",
                    timing: 'now'
                };
            }
        }
        
        // Evening check (9-10 PM)
        if (hour >= 21 && hour < 22) {
            const incompleteHabits = userData.habits.filter(h => !h.completedToday);
            if (incompleteHabits.length > 0) {
                return {
                    type: 'evening_review',
                    message: `You have ${incompleteHabits.length} habits remaining. ` +
                             `Would you like to reschedule them for tomorrow?`,
                    actions: ['reschedule', 'complete_now', 'skip']
                };
            }
        }
        
        return null;
    }
}
```

---

## Implementation Checklist

### Phase 2: Intelligence Layer

- [ ] Implement correlation engine (Pearson, Spearman)
- [ ] Add time-lag analysis
- [ ] Create insight generation
- [ ] Build PCS calculation

### Phase 3: Prediction

- [ ] Implement burnout prediction model
- [ ] Add intervention system
- [ ] Create risk level display

### Phase 6: AI Integration

- [ ] Set up Ollama connection
- [ ] Implement embedding generation
- [ ] Set up vector database
- [ ] Build RAG query system
- [ ] Create Digital Coach

---

## References

- PCS Research: https://pmc.ncbi.nlm.nih.gov/articles/PMC10151500/
- Burnout Prediction: https://pmc.ncbi.nlm.nih.gov/articles/PMC12414203/
- Ollama: https://ollama.ai/
- ChromaDB: https://www.trychroma.com/

---

## Cross-References

| Related Document | Content |
|------------------|---------|
| [RESEARCH_SUMMARY.md](RESEARCH_SUMMARY.md) | Overview of all research |
| [TECHNICAL_ARCHITECTURES.md](TECHNICAL_ARCHITECTURES.md) | RAG architecture |
| [docs/specs/CORRELATION_ENGINE_SPEC.md](../specs/CORRELATION_ENGINE_SPEC.md) | Implementation spec |
| [docs/specs/LOCAL_RAG_SPEC.md](../specs/LOCAL_RAG_SPEC.md) | RAG implementation |

---

*Last updated: February 2026*