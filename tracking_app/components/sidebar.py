"""
Categorized Navigation Sidebar

Provides a clean, organized sidebar navigation using expandable categories
to handle 30+ pages without cluttering the UI.

Categories:
    - 🚀 Overview (Dashboard, Calendar, Weekly Review)
    - ✅ Mastery (Habits, Stacks, Experiments, Analytics)
    - 📝 Planning (Tasks, Goals, Time, Journal)
    - ❤️ Wellness (Health, Emotion, Identity, Purpose)
    - 💰 Finance
    - 🏆 Gamification (Achievements, Rewards, Social)
    - ⚙️ System (Data Ops, Settings, Alerts)

Usage:
    from tracking_app.components.sidebar import render_categorized_sidebar
    
    render_categorized_sidebar()
"""

import streamlit as st
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Import theme selector for full theme support
from tracking_app.design.theme_selector import render_theme_selector, get_theme_options
from tracking_app.design.theme import apply_design_system


# Page category mapping based on Behavioral Science taxonomy
PAGE_CATEGORIES: Dict[str, List[tuple]] = {
    "🚀 Overview": [
        ("Dashboard", "🏠", "dashboard"),
        ("Calendar", "📅", "calendar"),
        ("Weekly View", "📆", "weekly"),
        ("Weekly Review", "🔄", "weekly_review"),
    ],
    "✅ Mastery": [
        ("Habits", "✅", "habits"),
        ("Habit Stacks", "🔗", "stacks"),
        ("Experiments", "🔬", "habit_experiments"),
        ("Analytics", "📈", "habit_analytics"),
        ("Templates", "📚", "template_sharing"),
    ],
    "📝 Planning": [
        ("Tasks", "📝", "tasks"),
        ("Goals", "🎯", "goals"),
        ("Time", "⏰", "time"),
        ("Journal", "📓", "journal"),
        ("Private Todos", "🔐", "private_todos"),
    ],
    "❤️ Wellness": [
        ("Health", "❤️", "health"),
        ("Emotional Health", "😊", "emotional_health"),
        ("Diary", "📔", "diary"),
        ("Energy", "⚡", "energy"),
        ("Identity", "🪞", "identity"),
        ("Purpose", "🌟", "purpose_tracker"),
    ],
    "💰 Finance": [
        ("Finances", "💰", "finances"),
    ],
    "🏆 Gamification": [
        ("Achievements", "🏆", "achievements"),
        ("Rewards Shop", "🎁", "rewards"),
        ("Leaderboards", "📊", "leaderboards"),
        ("Challenges", "💪", "challenges"),
        ("Friends", "👥", "friends"),
    ],
}


def render_categorized_sidebar() -> Optional[str]:
    """
    Render the categorized navigation sidebar.
    
    Returns:
        Optional[str]: The selected page path or None for native navigation
    """
    # Sidebar header with app branding
    st.sidebar.title("🎯 Tracking System")
    
    # User stats section
    _render_user_stats()
    
    st.sidebar.divider()
    
    # Render all category expanders
    for category, pages in PAGE_CATEGORIES.items():
        _render_category_expander(category, pages)
    
    st.sidebar.divider()
    
    # Theme toggle section
    _render_theme_toggle()
    
    # Sidebar footer
    _render_sidebar_footer()
    
    return None


def _render_user_stats() -> None:
    """Render user statistics at the top of sidebar."""
    st.sidebar.subheader("👤 Your Stats")
    
    # Placeholder for actual stats - in production, fetch from database
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("🔥 Streak", "0")
    with col2:
        st.metric("⭐ Points", "0")
    
    # Additional stats in expander
    with st.sidebar.expander("📊 More Stats"):
        st.write("**Weekly Progress:**")
        st.progress(0, text="Habits completed")
        st.write("**Monthly Goals:**")
        st.progress(0, text="Goals achieved")


def _render_category_expander(category: str, pages: List[tuple]) -> None:
    """
    Render a category as an expandable section.
    
    Args:
        category: Category name with emoji (e.g., "🚀 Overview")
        pages: List of tuples (display_name, icon, page_path)
    """
    # Extract emoji and name
    if " " in category:
        emoji, name = category.split(" ", 1)
    else:
        emoji = "📁"
        name = category
    
    # Create expander for the category
    with st.sidebar.expander(f"{category}", expanded=False):
        for display_name, icon, page_path in pages:
            # Create a page link using Streamlit's page link
            # This works with multi-page apps
            st.page_link(
                f"pages/{page_path}.py",
                label=f"{icon} {display_name}",
            )


def _render_theme_toggle() -> None:
    """Render full theme selector at the bottom of sidebar."""
    st.sidebar.subheader("🎨 Appearance")
    
    # Initialize theme in session state if not present
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'
    
    # Get current theme
    current_theme = st.session_state.get('theme', 'dark')
    
    # Apply the theme CSS
    apply_design_system(theme=current_theme)
    
    # Render the full theme selector
    with st.sidebar:
        render_theme_selector(
            location="sidebar",
            show_descriptions=True,
            show_preview=True
        )


def _render_sidebar_footer() -> None:
    """Render sidebar footer with actions."""
    st.sidebar.divider()
    
    # Unified settings access
    st.sidebar.page_link(
        "pages/settings.py",
        label="⚙️ Settings & System",
    )
    
    st.sidebar.subheader("🔧 Quick Actions")
    
    # Quick action buttons
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 Refresh", key="sidebar_refresh"):
            st.rerun()
    with col2:
        if st.button("❓ Help", key="sidebar_help"):
            st.sidebar.info("Use the categories above to navigate to different features!")
    
    # Version info
    st.sidebar.caption("📌 v1.0.0 | Tracking System")


# Alias for backward compatibility
def render_sidebar(**kwargs) -> Optional[str]:
    """
    Main sidebar rendering function.
    
    This is the entry point used by the application.
    
    Args:
        **kwargs: Additional keyword arguments (ignored for compatibility)
    
    Returns:
        Optional[str]: Result from categorized sidebar
    """
    return render_categorized_sidebar()


def create_categorized_sidebar():
    """
    Create a configured categorized sidebar instance.
    
    Returns:
        The result of rendering the categorized sidebar
    """
    return render_categorized_sidebar()
