# Phase 10: Caching System Enhancement

## Current State Analysis

Found **27 instances** of `@st.cache_data` across the codebase:

| File | Count | TTL Used |
|------|-------|-----------|
| constants.py (multiple pages) | 18 | 3600s (1 hour) |
| helpers.py | 4 | 300s (5 min) |
| lazy_loader.py | 2 | 300s |
| charts.py | 1 | 60s |
| dashboard/utils | 2 | N/A (tips) |

---

## Optimization Opportunities

### 1. TTL Strategy Refinement

Current TTLs are too uniform. Recommended:

| Data Type | Recommended TTL | Rationale |
|-----------|----------------|------------|
| Static constants (icons, categories) | 86400s (24h) | Never changes |
| User preferences | 3600s (1h) | Changes rarely |
| Session data | 300s (5min) | Medium-term |
| Dynamic calculations | 60-120s | Real-time needed |
| Chart data | 30-60s | High variability |

### 2. Cache Invalidation Strategy

**Problem**: Streamlit's default cache invalidation is based on function arguments. For database-backed data, this is insufficient.

**Solution**: Implement a cache key system:

```python
# Cache key with version/timestamp
def get_cache_key(prefix: str, version: int) -> str:
    return f"{prefix}_v{version}"

# Manual invalidation via session state
if 'cache_version' not in st.session_state:
    st.session_state.cache_version = 1

# Use in cached functions
@st.cache_data(ttl=300)
def get_data(_version: int):
    return load_from_db()
```

### 3. Function-Specific Optimizations

#### Constants Functions (18 instances)
- **Current**: TTL 3600s, no spinner
- **Issue**: Some are loaded even when unused
- **Fix**: Add `show_spinner=False` where missing, consider lazy loading

#### Habits Helpers
```python
# Current (line 26-27)
@st.cache_data(ttl=300)
def get_habits_batch_data(habit_ids: str, _storage_hash: str) -> Dict[str, Dict]:
```

**Issue**: `habit_ids` as string may cause cache fragmentation
**Fix**: Use hash of sorted list instead

#### Charts
```python
# Current (line 189)
@st.cache_data(ttl=60)
def cache_chart_data(data_hash: str, data: Dict) -> Dict:
```

**Issue**: Dict as parameter won't cache properly
**Fix**: Use data hash only, recalculate if needed

### 4. New Caching Utilities

Create `brain/utils/caching.py`:

```python
import streamlit as st
from functools import wraps
from typing import Any, Callable, Optional
import hashlib
import json

def smart_cache(ttl: int = 300, max_entries: int = 100):
    """Enhanced caching with automatic key generation."""
    def decorator(func: Callable) -> Callable:
        @st.cache_data(ttl=ttl, max_entries=max_entries, show_spinner=False)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

def invalidate_caches(*cache_names: str):
    """Manually invalidate specific caches."""
    for name in cache_names:
        if name in st.session_state:
            st.session_state[name] += 1

def hash_args(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()
```

### 5. Cache Warming Strategy

Add startup cache warming:

```python
def warm_caches():
    """Pre-load frequently accessed data."""
    # Warm constant caches
    get_icon_index_map()
    get_priority_index_map()
    get_goal_icon_index_map()
    
    # Warm user-specific caches  
    load_user_preferences()
    load_dashboard_data()
```

---

## Implementation Priority

| Priority | Task | Effort |
|----------|------|--------|
| High | Fix broken cache functions (charts, habits) | Low |
| High | Add cache warming utility | Medium |
| Medium | Refine TTL values by data type | Medium |
| Medium | Implement cache invalidation system | High |
| Low | Add cache monitoring/metrics | Medium |

---

## Testing Strategy

1. **Cache Hit Rate**: Track how often cached vs fresh data is used
2. **Memory Impact**: Monitor memory usage with different TTLs
3. **Stale Data**: Verify data freshness with TTL=0 for comparison

---

## Files to Modify

```
brain/utils/
├── caching.py          (NEW)
└── __init__.py         (update exports)

tracking_app/pages/*/
├── constants.py        (TTL refinement)
└── helpers.py          (cache key fixes)
```

---

*Last updated: March 2026*
