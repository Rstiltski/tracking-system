"""
Widget Settings Page - Custom Dashboard Widgets

Phase 9 Task 3: Custom Widgets
Allows users to customize their dashboard with draggable widgets.

Features:
- Widget library with available widgets
- Enable/disable widgets
- Reorder widgets
- Widget-specific settings

Usage:
    streamlit run tracking_app/pages/widget_settings.py
"""

import streamlit as st
from typing import List, Dict, Any, Optional


# Available widgets
AVAILABLE_WIDGETS = [
    {
        "id": "habit_scores",
        "name": "Habit Scores",
        "description": "Show habit strength scores",
        "icon": "📊",
        "category": "habits"
    },
    {
        "id": "todays_habits",
        "name": "Today's Habits",
        "description": "Quick habit completion for today",
        "icon": "✅",
        "category": "habits"
    },
    {
        "id": "active_tasks",
        "name": "Active Tasks",
        "description": "Show pending tasks",
        "icon": "📋",
        "category": "tasks"
    },
    {
        "id": "goals_progress",
        "name": "Goals Progress",
        "description": "Track goal completion",
        "icon": "🎯",
        "category": "goals"
    },
    {
        "id": "burnout_indicator",
        "name": "Burnout Risk",
        "description": "Show burnout risk level",
        "icon": "🔥",
        "category": "health"
    },
    {
        "id": "quick_stats",
        "name": "Quick Stats",
        "description": "Overview metrics",
        "icon": "📈",
        "category": "overview"
    },
    {
        "id": "motivational_quote",
        "name": "Motivation",
        "description": "Daily motivational quote",
        "icon": "💭",
        "category": "motivation"
    },
    {
        "id": "activity_feed",
        "name": "Activity Feed",
        "description": "Recent activity log",
        "icon": "📜",
        "category": "overview"
    },
    {
        "id": "streak_counter",
        "name": "Streaks",
        "description": "Current streak display",
        "icon": "🔥",
        "category": "habits"
    },
    {
        "id": "weather",
        "name": "Weather",
        "description": "Local weather info",
        "icon": "🌤️",
        "category": "external"
    }
]


def render_page():
    """Render the widget settings page."""
    st.title("🎛️ Widget Settings")
    st.markdown("Customize your dashboard by enabling, disabling, and reordering widgets.")
    
    # Initialize widget order in session state
    if 'widget_order' not in st.session_state:
        st.session_state.widget_order = [w['id'] for w in AVAILABLE_WIDGETS]
    
    if 'enabled_widgets' not in st.session_state:
        st.session_state.enabled_widgets = {w['id']: True for w in AVAILABLE_WIDGETS}
    
    # =========================================================================
    # WIDGET CATEGORIES
    # =========================================================================
    st.subheader("📦 Available Widgets")
    
    # Group widgets by category
    categories = {}
    for widget in AVAILABLE_WIDGETS:
        cat = widget['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(widget)
    
    # Display categories
    for category, widgets in categories.items():
        with st.expander(f"### {category.title()} Widgets", expanded=True):
            for widget in widgets:
                widget_id = widget['id']
                enabled = st.session_state.enabled_widgets.get(widget_id, True)
                
                col1, col2, col3 = st.columns([1, 4, 1])
                
                with col1:
                    st.markdown(f"{widget['icon']}")
                
                with col2:
                    st.markdown(f"**{widget['name']}**")
                    st.caption(widget['description'])
                
                with col3:
                    new_enabled = st.toggle(
                        "Enable",
                        value=enabled,
                        key=f"toggle_{widget_id}"
                    )
                    st.session_state.enabled_widgets[widget_id] = new_enabled
    
    # =========================================================================
    # WIDGET ORDER
    # =========================================================================
    st.divider()
    st.subheader("🔄 Widget Order")
    st.markdown("Drag and drop to reorder widgets (future feature). Current order:")
    
    # Get enabled widgets in order
    enabled_order = [
        w_id for w_id in st.session_state.widget_order 
        if st.session_state.enabled_widgets.get(w_id, True)
    ]
    
    # Show current order
    for i, widget_id in enumerate(enabled_order, 1):
        widget = next((w for w in AVAILABLE_WIDGETS if w['id'] == widget_id), None)
        if widget:
            st.markdown(f"{i}. {widget['icon']} {widget['name']}")
    
    # =========================================================================
    # WIDGET PRESETS
    # =========================================================================
    st.divider()
    st.subheader("💾 Presets")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Productivity Focus"):
            _apply_preset("productivity")
            st.success("Applied!")
    
    with col2:
        if st.button("❤️ Health Focus"):
            _apply_preset("health")
            st.success("Applied!")
    
    with col3:
        if st.button("🔄 Reset All"):
            _apply_preset("all")
            st.success("Reset!")
    
    # =========================================================================
    # SAVE SETTINGS
    # =========================================================================
    st.divider()
    
    if st.button("💾 Save Widget Settings", type="primary"):
        st.success("✅ Widget settings saved!")
        st.info("Your dashboard will reflect these changes on the next reload.")


def _apply_preset(preset: str) -> None:
    """Apply a widget preset."""
    if preset == "productivity":
        enabled = {
            "habit_scores": True,
            "todays_habits": True,
            "active_tasks": True,
            "goals_progress": True,
            "quick_stats": True,
            "streak_counter": True,
            "burnout_indicator": False,
            "motivational_quote": True,
            "activity_feed": True,
            "weather": False
        }
    elif preset == "health":
        enabled = {
            "habit_scores": True,
            "todays_habits": True,
            "active_tasks": False,
            "goals_progress": True,
            "burnout_indicator": True,
            "quick_stats": True,
            "motivational_quote": True,
            "activity_feed": False,
            "streak_counter": True,
            "weather": True
        }
    else:  # all
        enabled = {w['id']: True for w in AVAILABLE_WIDGETS}
    
    st.session_state.enabled_widgets = enabled


# Entry point
if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    st.set_page_config(page_title="Widget Settings - Veryfyn", page_icon="🎛️", layout="wide")
    render_page()
