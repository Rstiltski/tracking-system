# 🧪 Habit Experiments Module

A/B testing and experiments for habits in the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Experiment types, durations |
| [`helpers.py`](helpers.py) | Experiment logic |
| [`session_state.py`](session_state.py) | Experiments state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **A/B Testing**: Test habit variations
- **Control Groups**: Compare with baseline
- **Duration Settings**: Set experiment duration
- **Results Analysis**: Analyze experiment results
- **Recommendations**: Get recommendations based on results

---

## Public API

### Constants

```python
from tracking_app.pages.habit_experiments import (
    EXPERIMENT_TYPES,    # Experiment type options
    DURATION_OPTIONS,    # Duration presets
    RESULT_METRICS,      # Measurement metrics
)
```

### Helper Functions

```python
from tracking_app.pages.habit_experiments import (
    create_experiment,   # Create new experiment
    record_result,       # Record experiment result
    analyze_experiment,  # Analyze results
)
```

### Components

```python
from tracking_app.pages.habit_experiments import (
    render_header,       # Page header
    render_experiment_list, # Active experiments
    render_experiment_form, # Creation form
    render_results,      # Results display
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.habit_experiments import (
    init_session_state,
    render_header,
    render_experiment_list,
    render_experiment_form,
)

init_session_state()
render_header()
render_experiment_list()
render_experiment_form()
```

---

## Dependencies

- `streamlit` - UI framework
- `datetime` - Date handling
- `statistics` - Statistical analysis

---

## Related Pages

- **Habits**: Habit management
- **Habit Analytics**: Habit analytics
- **Insights**: General insights