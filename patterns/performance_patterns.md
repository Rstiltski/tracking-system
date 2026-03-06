# Performance Patterns

Reusable code patterns for performance optimization in the tracking system.

---

## Caching Pattern

### Purpose
Reduce database queries and improve response times by caching frequently accessed data.

### Pattern: @cached Decorator

```python
from brain.utils import cached

@cached(ttl=60, key_prefix="habits")
def get_habits():
    """Get all habits - cached for 60 seconds."""
    return storage.get_habits()

# Force cache clear
get_habits.cache_clear()
```

### Pattern: Cache Class

```python
from brain.utils import Cache

cache = Cache(max_size=1000, default_ttl=300)

# Set value
cache.set("user:123", {"name": "John"}, ttl=60)

# Get value
user = cache.get("user:123")

# Invalidate pattern
cache.invalidate_pattern("user:")
```

---

## Profiling Pattern

### Purpose
Identify slow operations and measure performance.

### Pattern: @timed Decorator

```python
from brain.utils import timed

@timed(category="database")
def query_data():
    return db.fetch_all("SELECT * FROM habits")
```

### Pattern: Context Manager

```python
from brain.utils import timed

with timed("complex_operation", category="processing"):
    # ... code to measure
    result = process_data()
```

### Pattern: Get Slow Operations

```python
from brain.utils import get_performance_logger

perf = get_performance_logger()
slow_ops = perf.get_slow_operations(threshold_ms=100)
```

---

## Pagination Pattern

### Purpose
Handle large datasets efficiently with pagination.

### Pattern: Paginator

```python
from brain.utils import Paginator

paginator = Paginator(page_size=20)
page = paginator.paginate(
    query="SELECT * FROM habits ORDER BY created_at DESC",
    count_query="SELECT COUNT(*) FROM habits",
    db=db,
    page=1
)

print(f"Page {page.page_number} of {page.total_pages}")
print(f"Items: {len(page.items)}")
```

### Pattern: Cursor Pagination

```python
from brain.utils import CursorPaginator

paginator = CursorPaginator(page_size=20)
page = paginator.paginate(
    query="SELECT * FROM habit_entries WHERE habit_id = ?",
    db=db,
    cursor=None,
    cursor_column="entry_date",
    params=(habit_id,)
)

# Next page
next_page = paginator.paginate(..., cursor=page.cursor)
```

---

## Debouncing Pattern

### Purpose
Reduce rapid function calls for UI updates.

### Pattern: @debounce Decorator

```python
from brain.utils import debounce

@debounce(delay_ms=300)
def on_search(query):
    """Search triggered after 300ms of no input."""
    return perform_search(query)
```

### Pattern: @throttle Decorator

```python
from brain.utils import throttle

@throttle(interval_ms=100)
def on_scroll(position):
    """Called at most once every 100ms."""
    update_scroll_position(position)
```

### Pattern: Rate Limiter

```python
from brain.utils import RateLimiter

limiter = RateLimiter(max_calls=10, window_seconds=60)

if limiter.can_call():
    result = api_call()
    limiter.record_call()
else:
    wait_time = limiter.wait_time()
```

---

## Lazy Loading Pattern

### Purpose
Load data on demand to reduce memory usage.

### Pattern: LazyLoader

```python
from brain.utils import LazyLoader

lazy_habits = LazyLoader(lambda: storage.get_habits())

# Data not loaded yet
print("Loader created")

# Access triggers loading
habits = lazy_habits.get()  # Now loads
```

### Pattern: LazyIterator

```python
from brain.utils import LazyIterator

iterator = LazyIterator(
    chunk_loader=lambda offset, limit: storage.get_habit_entries(
        habit_id="abc",
        start_date=start,
        end_date=end
    ),
    chunk_size=100
)

for entry in iterator:
    process_entry(entry)
```

### Pattern: LazyHabitEntries

```python
from brain.utils import LazyHabitEntries

lazy_entries = LazyHabitEntries(storage, habit_id)

# Get all entries (loaded on demand)
all_entries = lazy_entries.all()

# Get entries for specific month
march_entries = lazy_entries.for_month(2024, 3)
```

---

## Responsive UI Pattern

### Purpose
Create mobile-responsive Streamlit components.

### Pattern: ResponsiveLayout

```python
from tracking_app.components.responsive import ResponsiveLayout

layout = ResponsiveLayout()

# Check breakpoint
if layout.is_mobile():
    st.write("Mobile view")
elif layout.is_tablet():
    st.write("Tablet view")
else:
    st.write("Desktop view")

# Responsive columns
with layout.columns() as cols:
    with cols[0]:
        st.write("Column 1")
```

### Pattern: TouchFriendly

```python
from tracking_app.components.responsive import TouchFriendly

# Touch-friendly button (min 44px touch target)
TouchFriendly.button("Save", key="save_btn")

# Icon button
TouchFriendly.icon_button("💾", "Save", key="save_icon")
```

### Pattern: MobileNavigation

```python
from tracking_app.components.responsive import MobileNavigation

# Hamburger menu for mobile
selected = MobileNavigation.hamburger_menu(
    items=[
        {"label": "Dashboard", "icon": "📊", "key": "dashboard"},
        {"label": "Habits", "icon": "🎯", "key": "habits"},
        {"label": "Tasks", "icon": "✅", "key": "tasks"},
    ]
)
```

### Pattern: ResponsiveChart

```python
from tracking_app.components.responsive import ResponsiveChart

# Get chart dimensions
height = ResponsiveChart.get_chart_height(default_height=400)
width = ResponsiveChart.get_chart_width()

# Simplify for mobile
config = ResponsiveChart.simplify_for_mobile(chart_config)
```

---

## Combined Patterns

### Pattern: Cached + Lazy + Paginated

```python
from brain.utils import cached, Paginator, LazyLoader

@cached(ttl=120, key_prefix="habit_entries")
def get_habit_entries_page(habit_id, page=1):
    paginator = Paginator(page_size=50)
    return paginator.paginate(
        query="SELECT * FROM habit_entries WHERE habit_id = ? ORDER BY entry_date DESC",
        count_query="SELECT COUNT(*) FROM habit_entries WHERE habit_id = ?",
        db=db,
        page=page,
        params=(habit_id,)
    )

# Usage
page = get_habit_entries_page("habit_123", page=1)
```

### Pattern: Timed + Cached

```python
from brain.utils import timed, cached

@timed(category="database")
@cached(ttl=60)
def get_dashboard_data():
    """Cached dashboard data with timing."""
    return {
        "habits": storage.get_habits(),
        "tasks": storage.get_tasks(),
        "goals": storage.get_goals()
    }
```

---

**Created:** March 6, 2026  
**Version:** 1.0.0