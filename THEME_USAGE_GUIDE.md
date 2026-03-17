# 🎨 Theme Usage Guide

## Quick Start

### Using Themes in Any Page

```python
import streamlit as st
from tracking_app.design import apply_design_system

# Apply your chosen theme at the top of the page
apply_design_system(theme="bento_earth")

# Now build your page normally
st.title("My Page")
```

## Available Themes

| Theme | Key | Icon | Best For |
|-------|-----|------|----------|
| Light | `"light"` | ☀️ | Clean, professional interfaces |
| Dark | `"dark"` | 🌙 | Default, modern apps |
| **Bento Earth** | `"bento_earth"` | 🎨 | Wellness, lifestyle, elegant tracking |
| **Neobrutalist Forge** | `"neobrutalist_forge"` | 🔨 | Productivity, bold statements |
| **Calm Tide** | `"calm_tide"` | 🌊 | ADHD-friendly, gentle habits |
| **RPG Forge** | `"rpg_forge"` | ⚔️ | Gamification, competitive features |

## Theme Selector Component

Add a theme selector to your sidebar:

```python
import streamlit as st
from tracking_app.design import render_theme_selector

st.sidebar.title("Settings")
render_theme_selector(location="sidebar")
```

Or in the main content:

```python
from tracking_app.design import render_theme_selector

render_theme_selector(location="main", show_descriptions=True)
```

## Page Examples

### Example 1: Bento Earth Habits Page

```python
"""Habits Page - Bento Earth Theme"""
import streamlit as st
from tracking_app.design import apply_design_system

apply_design_system(theme="bento_earth")

st.title("✅ Habits")

# Your habit tracking content here
```

### Example 2: RPG Forge Dashboard

```python
"""Dashboard - RPG Forge Theme"""
import streamlit as st
from tracking_app.design import apply_design_system

apply_design_system(theme="rpg_forge")

st.title("⚔️ Dashboard")

# Show XP, levels, achievements
```

### Example 3: Calm Tide Journal

```python
"""Journal - Calm Tide Theme"""
import streamlit as st
from tracking_app.design import apply_design_system

apply_design_system(theme="calm_tide")

st.title("📔 Journal")

# Gentle, reflective writing interface
```

### Example 4: Neobrutalist Tasks

```python
"""Tasks - Neobrutalist Forge Theme"""
import streamlit as st
from tracking_app.design import apply_design_system

apply_design_system(theme="neobrutalist_forge")

st.title("📋 Tasks")

# Bold, high-contrast task list
```

## Using Theme Colors

Access theme colors programmatically:

```python
from tracking_app.design import get_theme_colors, get_current_theme

# Get current theme
theme = get_current_theme()

# Get theme colors
colors = get_theme_colors(theme)
print(colors["bg"])
print(colors["primary"])
```

## Custom CSS with Themes

Each theme adds a CSS class to the page. Use it for custom styling:

```python
st.markdown("""
<style>
/* Bento Earth specific styles */
.theme-bento_earth .my-custom-card {
    background: #faf6f0;
    border: 1.5px solid #dfd3c6;
}

/* RPG Forge specific styles */
.theme-rpg_forge .my-custom-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
}
</style>
""", unsafe_allow_html=True)
```

## Theme-Specific Components

### Bento Earth Components

```python
# Bento grid layout
st.markdown('<div class="bento-grid">', unsafe_allow_html=True)
# ... your bento cells ...
st.markdown('</div>', unsafe_allow_html=True)

# Bento cell
st.markdown(f"""
<div class="bento-cell" style="grid-column: span 6;">
    Your content here
</div>
""", unsafe_allow_html=True)
```

### RPG Forge Components

```python
# RPG card
st.markdown(f"""
<div class="rpg-card" style="padding: 20px;">
    Your gamified content here
</div>
""", unsafe_allow_html=True)

# XP bar
st.markdown(f"""
<div class="xp-bar" style="
    height: 12px;
    background: rgba(255,255,255,0.08);
    border-radius: 6px;
">
    <div style="
        width: 75%;
        height: 100%;
        background: linear-gradient(90deg, #6c63ff, #a78bfa);
        border-radius: 6px;
    "></div>
</div>
""", unsafe_allow_html=True)
```

## Best Practices

### 1. Apply Theme Early
Always apply the theme at the top of your page, before any content:

```python
✅ GOOD:
apply_design_system(theme="bento_earth")
st.title("Habits")

❌ BAD:
st.title("Habits")
apply_design_system(theme="bento_earth")  # Too late!
```

### 2. Consistent Theme Usage
Use the same theme throughout related pages:

```python
# All habit-related pages use Bento Earth
habits_page.py → apply_design_system("bento_earth")
habit_analytics.py → apply_design_system("bento_earth")
habit_settings.py → apply_design_system("bento_earth")
```

### 3. Let Users Choose
Provide a theme selector for user preference:

```python
with st.sidebar:
    render_theme_selector()
```

### 4. Test All Themes
Make sure your page looks good in all themes:

```python
# Test each theme
for theme in ["light", "dark", "bento_earth", "neobrutalist_forge", "calm_tide", "rpg_forge"]:
    apply_design_system(theme)
    # Verify layout works
```

## Migration Guide

### From Standard Light/Dark to Special Themes

**Before:**
```python
apply_design_system(theme="dark")
```

**After:**
```python
# Choose a special theme
apply_design_system(theme="bento_earth")
```

### Adding Theme Support to Existing Pages

1. Import the theme system:
```python
from tracking_app.design import apply_design_system
```

2. Apply theme at the top:
```python
apply_design_system(theme="bento_earth")  # or let user choose
```

3. Add theme selector (optional):
```python
from tracking_app.design import render_theme_selector
render_theme_selector(location="sidebar")
```

4. Test in all themes

## Troubleshooting

### Theme Not Applying
- Make sure `apply_design_system()` is called BEFORE any content
- Check that the theme key is correct (e.g., `"bento_earth"` not `"Bento Earth"`)

### Colors Look Wrong
- Clear browser cache
- Check if custom CSS is overriding theme colors
- Verify theme is being applied in the correct order

### Theme Selector Not Working
- Ensure session state is initialized
- Check that `st.rerun()` is called on theme change
- Verify imports are correct

## Complete Example

Here's a complete page with theme support:

```python
"""
Sample Page with Theme Support
"""
import streamlit as st
from tracking_app.design import (
    apply_design_system,
    render_theme_selector,
    get_current_theme,
)

# Apply theme (user's choice or default)
theme = st.session_state.get("theme", "bento_earth")
apply_design_system(theme=theme)

# Page config
st.set_page_config(page_title="Sample Page", layout="wide")

# Sidebar with theme selector
with st.sidebar:
    st.title("⚙️ Settings")
    render_theme_selector(location="sidebar")
    
    st.divider()
    st.caption(f"Current theme: {get_current_theme()}")

# Main content
st.title("📊 Sample Page")
st.write("This page supports all 6 themes!")

# Sample content
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Metric 1", "123")
with col2:
    st.metric("Metric 2", "456")
with col3:
    st.metric("Metric 3", "789")

# Sample card
st.markdown("""
<div style="
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-top: 20px;
">
    <h3>Themed Card</h3>
    <p>This card adapts to the current theme!</p>
</div>
""", unsafe_allow_html=True)
```

## Resources

- Theme System Summary: `THEME_SYSTEM_V2_SUMMARY.md`
- Design Tokens: `tracking_app/design/tokens.py`
- Theme Provider: `tracking_app/design/theme.py`
- Theme Selector: `tracking_app/design/theme_selector.py`
- Demo Page: `tracking_app/pages/habits_bento_earth.py`

---

**Happy Theming! 🎨**
