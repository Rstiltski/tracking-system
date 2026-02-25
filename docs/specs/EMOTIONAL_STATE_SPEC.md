# Emotional State Specification - RGB Neurotransmitter Model

**Feature:** RGB Neurotransmitter-Based Emotion Tracking
**Location:** `brain/models/emotional_state.py`
**Version:** 1.0.0
**Created:** February 2026

---

## 🧭 Quick Navigation

| Want to... | Go to... |
|------------|----------|
| **Get started** | [Usage Examples](#usage-examples) |
| **Understand the model** | [The RGB Model](#the-rgb-model) |
| **See API reference** | [API Reference](#api-reference) |
| **Integrate with other modules** | [Integration Guide](#integration-guide) |
| **Troubleshoot issues** | [Common Errors](#common-errors) |

---

## Overview

This module implements a scientifically-grounded emotion tracking system based on the "Chemical RGB" model of human emotions. The three primary neurotransmitters (Dopamine, Norepinephrine, Serotonin) combine like RGB colors to produce the full spectrum of human emotional states.

### Why This Model?

Traditional mood tracking uses simple scales (good/bad) or basic categories (happy/sad). The RGB model provides:

1. **Nuanced Tracking**: Capture complex emotional states, not just simple labels
2. **Visual Representation**: Each emotion maps to a real color
3. **Pattern Detection**: Analyze trends in neurotransmitter levels
4. **Scientific Basis**: Based on actual brain chemistry research

---

## The RGB Model

### Primary Neurotransmitters

| Neurotransmitter | Color | Core Function | High Level | Low Level |
|-----------------|-------|---------------|------------|-----------|
| **Dopamine** | Red | Reward/Pleasure | Joy, excitement | Anhedonia |
| **Norepinephrine** | Blue | Arousal/Alert | Focus, anxiety | Fatigue |
| **Serotonin** | Green | Stability/Satiety | Contentment | Sadness |

### Secondary Emotions (Combinations)

| Emotion | Dopamine | Norepinephrine | Serotonin | Hex Color |
|---------|----------|----------------|-----------|-----------|
| Joyful | 0.9 | 0.3 | 0.7 | #e6b34d |
| Excited | 0.85 | 0.8 | 0.5 | #d980cc |
| Content | 0.6 | 0.2 | 0.8 | #99cc33 |
| Calm | 0.4 | 0.15 | 0.7 | #66b32d |
| Anxious | 0.3 | 0.9 | 0.25 | #4d6640 |
| Stressed | 0.35 | 0.85 | 0.3 | #59d94d |
| Sad | 0.2 | 0.35 | 0.2 | #335933 |
| Angry | 0.4 | 0.95 | 0.25 | #66f240 |

### Modifiers (Optional)

| Modifier | Function | Effect |
|----------|----------|--------|
| **Oxytocin** | Bonding/Trust | Adds warmth to emotional state |
| **Endorphins** | Euphoria/Pain relief | Increases brightness |
| **GABA** | Calm/Inhibition | Reduces intensity |

---

## Usage Examples

### Creating an Emotional State

```python
from brain.models.emotional_state import EmotionalState, EmotionPreset

# Method 1: Create from neurotransmitter values
state = EmotionalState.create(
    dopamine=0.8,
    norepinephrine=0.3,
    serotonin=0.7,
    notes="Feeling great after morning run!"
)

# Method 2: Create from preset
state = EmotionalState.from_preset(EmotionPreset.JOYFUL)

# Method 3: Create with modifiers
state = EmotionalState.create(
    dopamine=0.75,
    norepinephrine=0.35,
    serotonin=0.7,
    oxytocin=0.85,  # Feeling loving
    endorphins=0.4,  # Runner's high
    notes="After spending time with family"
)
```

### Getting Emotional Color

```python
# Get hex color for visualization
color = state.hex_color  # Returns '#cc4db3'

# Get RGB tuple
rgb = state.rgb_tuple  # Returns (204, 179, 77)

# Display in UI
print(f"Your emotional color: {state.hex_color}")
```

### Getting Emotion Label

```python
# Get secondary emotion
emotion = state.get_secondary_emotion()
# Returns: {
#     "label": "Joyful",
#     "description": "Pure happiness and satisfaction",
#     "emoji": "😊",
#     "category": "positive"
# }

print(f"{emotion['emoji']} You're feeling {emotion['label']}")
```

### Saving to Database

```python
from brain.models.emotional_state import EmotionalStateManager

# Initialize manager
manager = EmotionalStateManager(db_path="tracking.db")

# Create and save state
state = EmotionalState.create(
    dopamine=0.8,
    serotonin=0.7,
    notes="Great presentation!"
)
state_id = manager.save(state)
print(f"Saved state with ID: {state_id}")
```

### Retrieving States

```python
# Get recent states
recent = manager.get_recent(days=7)

# Get states by date range
from datetime import datetime
states = manager.get_by_date_range(
    start_date=datetime(2026, 2, 1),
    end_date=datetime(2026, 2, 14)
)

# Get single state by ID
state = manager.get_by_id("abc12345")
```

### Analyzing Patterns

```python
from brain.models.emotional_state import EmotionAnalyzer

analyzer = EmotionAnalyzer(manager)

# Get average levels
avg = analyzer.get_average_levels(days=7)
print(f"Average dopamine: {avg.dopamine:.2f}")

# Get dominant emotion
dominant = analyzer.get_dominant_emotion(days=7)
print(f"Most common emotion: {dominant['label']} ({dominant['percentage']:.0f}%)")

# Detect patterns
patterns = analyzer.detect_patterns(days=30)
for p in patterns:
    if p["type"] == "warning":
        print(f"⚠️ {p['label']}: {p['description']}")

# Get weekly summary
summary = analyzer.get_weekly_summary()
print(f"Weekly color trend: {summary['color_trend']}")
```

---

## API Reference

### Classes

#### `NeurotransmitterLevels`

```python
@dataclass
class NeurotransmitterLevels:
    dopamine: float = 0.5       # 0.0-1.0
    norepinephrine: float = 0.5  # 0.0-1.0
    serotonin: float = 0.5       # 0.0-1.0
```

**Properties:**
| Property | Returns | Description |
|----------|---------|-------------|
| `rgb_tuple` | `Tuple[int, int, int]` | RGB values (0-255) |
| `hex_color` | `str` | Hex color string |

**Methods:**
| Method | Returns | Description |
|--------|---------|-------------|
| `to_dict()` | `Dict[str, float]` | Serialize to dictionary |
| `from_dict(data)` | `NeurotransmitterLevels` | Deserialize from dictionary |

---

#### `EmotionalModifiers`

```python
@dataclass
class EmotionalModifiers:
    oxytocin: float = 0.0     # 0.0-1.0
    endorphins: float = 0.0   # 0.0-1.0
    gaba: float = 0.0         # 0.0-1.0
```

---

#### `EmotionalState`

```python
@dataclass
class EmotionalState:
    id: str
    timestamp: datetime
    primaries: NeurotransmitterLevels
    modifiers: Optional[EmotionalModifiers] = None
    notes: str = ""
    triggers: List[str] = []
```

**Factory Methods:**
| Method | Description |
|--------|-------------|
| `create(d, n, s, ...)` | Create from neurotransmitter values |
| `from_preset(preset)` | Create from predefined emotion |
| `from_dict(data)` | Deserialize from dictionary |

**Properties:**
| Property | Returns | Description |
|----------|---------|-------------|
| `hex_color` | `str` | Hex color for visualization |
| `rgb_tuple` | `Tuple[int, int, int]` | RGB values |
| `brightness` | `float` | Overall brightness (0.0-1.0) |

**Methods:**
| Method | Returns | Description |
|--------|---------|-------------|
| `get_secondary_emotion()` | `Dict` | Get emotion label, description, emoji |
| `get_emotion_category()` | `str` | Get emotion category |
| `to_dict()` | `Dict` | Serialize to dictionary |

---

#### `EmotionalStateManager`

```python
class EmotionalStateManager:
    def __init__(self, db_path: str = "tracking.db"): ...
```

**Methods:**
| Method | Returns | Description |
|--------|---------|-------------|
| `save(state)` | `str` | Save state, return ID |
| `get_by_id(id)` | `Optional[EmotionalState]` | Get by ID |
| `get_recent(days, limit)` | `List[EmotionalState]` | Get recent states |
| `get_by_date_range(start, end)` | `List[EmotionalState]` | Get by date range |
| `delete(id)` | `bool` | Delete state |

---

#### `EmotionAnalyzer`

```python
class EmotionAnalyzer:
    def __init__(self, manager: EmotionalStateManager): ...
```

**Methods:**
| Method | Returns | Description |
|--------|---------|-------------|
| `get_average_levels(days)` | `NeurotransmitterLevels` | Average levels |
| `get_dominant_emotion(days)` | `Dict` | Most common emotion |
| `detect_patterns(days)` | `List[Dict]` | Detected patterns |
| `get_weekly_summary()` | `Dict` | Weekly statistics |

---

#### `EmotionPreset` Enum

```python
class EmotionPreset(str, Enum):
    JOYFUL = "joyful"
    EXCITED = "excited"
    CONTENT = "content"
    CALM = "calm"
    ANXIOUS = "anxious"
    STRESSED = "stressed"
    SAD = "sad"
    DEPRESSED = "depressed"
    ANGRY = "angry"
    FEARFUL = "fearful"
    NEUTRAL = "neutral"
    HOPEFUL = "hopeful"
    GRATEFUL = "grateful"
    LOVING = "loving"
    OVERWHELMED = "overwhelmed"
```

---

## Integration Guide

### With Streamlit Page

```python
# tracking_app/pages/emotional_health.py
import streamlit as st
from brain.models.emotional_state import (
    EmotionalState, EmotionalStateManager, EmotionAnalyzer, EmotionPreset
)

def main():
    st.title("🌈 Emotional Health")
    
    # Initialize manager
    if 'emotion_manager' not in st.session_state:
        st.session_state.emotion_manager = EmotionalStateManager()
    
    manager = st.session_state.emotion_manager
    
    # Quick preset selection
    st.subheader("Quick Log")
    preset = st.selectbox(
        "How are you feeling?",
        options=list(EmotionPreset),
        format_func=lambda p: f"{EmotionalState.from_preset(p).get_secondary_emotion()['emoji']} {p.value.title()}"
    )
    
    # Custom sliders (expandable)
    with st.expander("Advanced: Adjust Neurotransmitters"):
        dopamine = st.slider("Dopamine (Joy/Reward)", 0.0, 1.0, 0.5)
        norepinephrine = st.slider("Norepinephrine (Stress/Energy)", 0.0, 1.0, 0.5)
        serotonin = st.slider("Serotonin (Satisfaction)", 0.0, 1.0, 0.5)
    
    # Notes
    notes = st.text_area("Notes (optional)")
    
    # Save button
    if st.button("Log Emotion"):
        state = EmotionalState.create(
            dopamine=dopamine,
            norepinephrine=norepinephrine,
            serotonin=serotonin,
            notes=notes
        )
        manager.save(state)
        st.success(f"Logged: {state}")
        
        # Show color
        st.markdown(
            f"<div style='width:50px;height:50px;background:{state.hex_color};"
            f"border-radius:50%;margin:10px auto;'></div>",
            unsafe_allow_html=True
        )
    
    # Show recent states
    st.subheader("Recent Emotions")
    recent = manager.get_recent(days=7)
    for state in recent[:10]:
        emotion = state.get_secondary_emotion()
        st.write(f"{emotion['emoji']} {emotion['label']} - {state.timestamp.strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()
```

### With Health Module

```python
# In tracking_app/pages/health.py - Replace simple mood tracking

# Old code:
# mood = st.selectbox("Mood", ["great", "good", "okay", "bad"])

# New code:
from brain.models.emotional_state import EmotionalState, EmotionPreset

st.subheader("How are you feeling?")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("😊 Great"):
        state = EmotionalState.from_preset(EmotionPreset.JOYFUL)
        
with col2:
    if st.button("😐 Okay"):
        state = EmotionalState.from_preset(EmotionPreset.NEUTRAL)
        
with col3:
    if st.button("😔 Low"):
        state = EmotionalState.from_preset(EmotionPreset.SAD)
```

### With Charts

```python
import plotly.graph_objects as go
from brain.models.emotional_state import EmotionalStateManager

manager = EmotionalStateManager()
states = manager.get_recent(days=30)

# Create color-coded timeline
fig = go.Figure()

# Add emotion markers
fig.add_trace(go.Scatter(
    x=[s.timestamp for s in states],
    y=[s.primaries.dopamine for s in states],
    mode='markers+lines',
    marker=dict(
        color=[s.hex_color for s in states],
        size=15
    ),
    name='Emotional States'
))

fig.update_layout(title="Emotional Timeline")
st.plotly_chart(fig)
```

---

## Common Errors

### ValueError: Values Outside Range

**Error:**
```
ValueError: dopamine value 1.5 is outside valid range (0.0-1.0)
```

**Cause:** Passing a neurotransmitter value outside 0.0-1.0 range.

**Solution:** The `__post_init__` method automatically clamps values, but you should validate user input:

```python
# ✅ Good - Validate before creating
dopamine = min(1.0, max(0.0, user_input))

# ❌ Bad - Pass unvalidated input
state = EmotionalState.create(dopamine=user_raw_input)
```

---

### TypeError: Non-Numeric Values

**Error:**
```
TypeError: float() argument must be a string or a real number, not 'NoneType'
```

**Cause:** Passing `None` or non-numeric values.

**Solution:**
```python
# ✅ Good - Provide defaults
state = EmotionalState.create(
    dopamine=user_input or 0.5,  # Default to neutral
    norepinephrine=another_input or 0.5,
    serotonin=third_input or 0.5
)

# ❌ Bad - Pass None
state = EmotionalState.create(
    dopamine=None,  # Will cause error
    ...
)
```

---

### Database Not Initialized

**Error:**
```
sqlite3.OperationalError: no such table: emotional_states
```

**Cause:** Database table not created.

**Solution:**
```python
# The EmotionalStateManager automatically creates the table on init
manager = EmotionalStateManager()  # This creates the table

# If issues persist, manually initialize:
manager._init_table()
```

---

## What NOT To Do

### ❌ Don't Store Raw User Input

```python
# ❌ BAD - User could enter any value
dopamine = float(input("Enter dopamine: "))
state = EmotionalState.create(dopamine=dopamine)

# ✅ GOOD - Validate and clamp
dopamine = max(0.0, min(1.0, float(input("Enter dopamine (0-1): "))))
state = EmotionalState.create(dopamine=dopamine)
```

### ❌ Don't Skip Timestamps

```python
# ❌ BAD - No timestamp tracking
state = EmotionalState.create(dopamine=0.8)
# timestamp defaults to now(), but what if you're backfilling?

# ✅ GOOD - Always provide timestamp when backfilling
from datetime import datetime
state = EmotionalState.create(
    dopamine=0.8,
    _timestamp=datetime(2026, 2, 20, 14, 30)  # Explicit timestamp
)
```

### ❌ Don't Ignore Modifiers

```python
# ❌ BAD - Ignoring the power of modifiers
state = EmotionalState.create(
    dopamine=0.8,  # High joy
    # But what if user just had a bonding moment?
)

# ✅ GOOD - Capture full context
state = EmotionalState.create(
    dopamine=0.8,
    serotonin=0.7,
    oxytocin=0.9,  # Captures bonding moment
    notes="After great conversation with friend"
)
```

### ❌ Don't Forget to Save

```python
# ❌ BAD - Create but don't save
state = EmotionalState.create(dopamine=0.8, notes="...")
# Lost if not saved!

# ✅ GOOD - Always save to database
manager = EmotionalStateManager()
state = EmotionalState.create(dopamine=0.8, notes="...")
manager.save(state)
```

---

## Database Schema

```sql
CREATE TABLE emotional_states (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    dopamine REAL NOT NULL,
    norepinephrine REAL NOT NULL,
    serotonin REAL NOT NULL,
    oxytocin REAL DEFAULT 0.0,
    endorphins REAL DEFAULT 0.0,
    gaba REAL DEFAULT 0.0,
    notes TEXT,
    triggers TEXT,           -- JSON array
    hex_color TEXT,          -- Computed color
    emotion_label TEXT,      -- Computed label
    emotion_category TEXT    -- Computed category
);

CREATE INDEX idx_emotional_states_timestamp ON emotional_states(timestamp);
```

---

## Testing

```python
# tests/test_emotional_state.py
import pytest
from brain.models.emotional_state import (
    EmotionalState, NeurotransmitterLevels, EmotionalModifiers,
    EmotionPreset, EmotionalStateManager, EmotionAnalyzer
)

def test_neurotransmitter_clamping():
    """Values should be clamped to 0.0-1.0 range."""
    levels = NeurotransmitterLevels(dopamine=1.5, norepinephrine=-0.5)
    assert levels.dopamine == 1.0
    assert levels.norepinephrine == 0.0

def test_hex_color():
    """Should return correct hex color."""
    levels = NeurotransmitterLevels(dopamine=1.0, norepinephrine=0.0, serotonin=0.0)
    assert levels.hex_color == "#ff0000"  # Pure red

def test_preset_joyful():
    """Joyful preset should have high dopamine."""
    state = EmotionalState.from_preset(EmotionPreset.JOYFUL)
    assert state.primaries.dopamine >= 0.8
    assert state.primaries.norepinephrine < 0.5

def test_secondary_emotion():
    """Should detect correct secondary emotion."""
    state = EmotionalState.create(dopamine=0.9, norepinephrine=0.3, serotonin=0.7)
    emotion = state.get_secondary_emotion()
    assert emotion["label"] == "Joyful"

def test_manager_save_and_retrieve():
    """Should save and retrieve emotional state."""
    manager = EmotionalStateManager(db_path=":memory:")
    state = EmotionalState.create(dopamine=0.8, notes="Test")
    
    state_id = manager.save(state)
    retrieved = manager.get_by_id(state_id)
    
    assert retrieved is not None
    assert retrieved.primaries.dopamine == 0.8
    assert retrieved.notes == "Test"
```

---

## References

- National Institutes of Health - Monoamine neurotransmitters research
- North London Collegiate School - Chemical emotion model
- Cleveland Clinic - Neurotransmitter functions

---

## Cross-References

| Want to... | Go to... |
|------------|----------|
| **See health module** | [tracking_app/pages/health.py](../../tracking_app/pages/health.py) |
| **Understand brain models** | [brain/models/](../../brain/models/) |
| **Read project rules** | [PROJECT_RULES.md](../../PROJECT_RULES.md) |
| **See feature map** | [FEATURE_MAP.md](../../FEATURE_MAP.md) |

---

*Last updated: February 2026*