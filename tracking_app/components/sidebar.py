"""
Sidebar Component - Categorized Navigation System

Provides consistent, categorized sidebar navigation across all pages.
Supports feature toggles via system_config.json to enable/disable categories.

Usage:
    from tracking_app.components.sidebar import render_sidebar
"""
import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any, List
import os
import json


def _load_system_config() -> Dict[str, Any]:
    """
    Load the system configuration file for feature toggles.
    
    Returns:
        Dictionary containing system configuration with category settings
    """
    config_path = os.path.join(os.path.dirname(__file__), '..', 'system_config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default config if file not found
        return {
            "categories": {},
            "ui_settings": {
                "show_user_stats": True,
                "show_theme_toggle": True,
                "show_streak_freeze": False,
                "collapsed_by_default": False
            }
        }
    except json.JSONDecodeError:
        st.error("⚠️ Invalid system_config.json format")
        return {"categories": {}, "ui_settings": {}}


def _render_nav_link(label: str, page_file: str):
    """
    Render a navigation link using link_button for universal compatibility.
    
    Args:
        label: Display label for the link
        page_file: Page filename without extension
    """
    # Use link_button which works in both multi-page and standalone contexts
    # The href points to the page route
    st.link_button(label, f"/{page_file}", use_container_width=True)


def _render_category_expander(icon: str, label: str, pages: List[str], is_collapsed: bool = True):
    """
    Render a collapsible category section with navigation links.
    
    Args:
        icon: Emoji icon for the category
        label: Category display label
        pages: List of page filenames to include
        is_collapsed: Whether the expander should be collapsed by default
    """
    if not pages:
        return
    
    with st.expander(f"{icon} {label}", expanded=not is_collapsed):
        for page_file in pages:
            # Convert snake_case to Title Case for display
            page_name = page_file.replace("_", " ").title()
            # Add emoji based on page type
            emoji_map = {
                "dashboard": "🏠", "calendar": "📅", "weekly": "📊", "weekly_review": "🔄",
                "habits": "✅", "stacks": "🔗", "habit_analytics": "📈", "habit_experiments": "🧪", "template_sharing": "📚",
                "tasks": "📋", "goals": "🎯", "time": "⏱️", "journal": "📔", "private_todos": "🔒",
                "health": "💪", "emotional_health": "❤️",
                "finances": "💰",
                "achievements": "🏆", "rewards": "🎁", "leaderboards": "📊", "challenges": "⚔️", "friends": "👥",
                "notification_settings": "⚙️", "habit_reminders": "⏰", "task_alerts": "📋", "goal_alerts": "🎯",
                "data_export": "📤", "data_import": "📥", "backup_restore": "💾", "data_lifecycle": "🔄",
                "insights": "💡", "diary": "📖"
            }
            page_emoji = emoji_map.get(page_file, "📄")
            _render_nav_link(f"{page_emoji} {page_name}", page_file)


def render_sidebar(show_streak_freeze: bool = False):
    """
    Render the main sidebar with categorized navigation.
    
    Displays:
    - App title and logo
    - User stats (Level, XP)
    - Categorized navigation using expandable sections
    - Optional Streak Freeze section (for habits page)
    - Theme toggle
    
    Categories are loaded from system_config.json and can be toggled on/off.
    
    Args:
        show_streak_freeze: If True, show streak freeze inventory section
    """
    with st.sidebar:
        # Logo/Title
        st.title("🎯 Veryfyn")
        st.caption("Personal Tracking System")
        st.divider()
        
        # User Stats
        level = st.session_state.get('user_level', 1)
        xp = st.session_state.get('user_xp', 0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Level", level)
        with col2:
            st.metric("XP", xp)
        
        # XP Progress Bar
        from tracking_app.components.session import get_xp_for_level
        current_xp = xp
        current_level = level
        next_level_xp = get_xp_for_level(current_level + 1)
        current_level_xp = get_xp_for_level(current_level)
        
        if next_level_xp > current_level_xp:
            progress = (current_xp - current_level_xp) / (next_level_xp - current_level_xp)
            # Ensure progress is always between 0 and 1
            progress = max(0.0, min(1.0, progress))
            st.progress(progress, text=f"Progress to Level {current_level + 1}")
        
        st.divider()
        
        # Streak Freeze Inventory (optional - shown on habits page)
        if show_streak_freeze:
            _render_streak_freeze_section()
            st.divider()
        
        # Load system configuration for feature toggles
        config = _load_system_config()
        categories = config.get('categories', {})
        ui_settings = config.get('ui_settings', {})
        collapsed_by_default = ui_settings.get('collapsed_by_default', True)
        
        # Main Navigation - Categorized
        for category_key, category_config in categories.items():
            if not category_config.get('enabled', True):
                continue  # Skip disabled categories
            
            icon = category_config.get('icon', '📄')
            label = category_config.get('label', category_key.title())
            pages = category_config.get('pages', [])
            
            if pages:
                _render_category_expander(icon, label, pages, is_collapsed=collapsed_by_default)
        
        st.divider()
        
        # Theme toggle
        if st.button("🌙 Toggle Theme", use_container_width=True):
            current_theme = st.session_state.get('theme', 'light')
            new_theme = "dark" if current_theme == "light" else "light"
            st.session_state.theme = new_theme
            # Save to storage
            if 'storage' in st.session_state:
                st.session_state.storage.set_user_data('theme', new_theme)
            st.rerun()
        
        # Footer
        st.divider()
        st.caption(f"Version 2.0.0")
        st.caption(f"© {datetime.now().year} Veryfyn")


def _render_streak_freeze_section():
    """Render streak freeze inventory section."""
    try:
        from brain.models.streak import StreakFreeze
    except ImportError:
        st.caption("❄️ Streak Freeze unavailable")
        return
    
    # Load streak freeze inventory
    storage = st.session_state.get('storage')
    if not storage:
        return
    
    freeze_data = storage.get_user_data("streak_freeze", None)
    
    if freeze_data:
        streak_freeze = StreakFreeze.from_dict(freeze_data)
    else:
        streak_freeze = StreakFreeze(count=1)  # Start with 1 free freeze
    
    st.subheader("❄️ Streak Freezes")
    
    # Display freeze count with visual indicator
    freeze_progress = streak_freeze.count / streak_freeze.max_freezes
    st.progress(freeze_progress, text=f"{streak_freeze.count}/{streak_freeze.max_freezes} available")
    
    # Purchase freeze button
    if not streak_freeze.is_maxed:
        xp = st.session_state.get('user_xp', 0)
        if st.button(f"🛒 Buy Freeze ({streak_freeze.xp_cost} XP)", 
                    help="Purchase a streak freeze to protect your streaks",
                    use_container_width=True):
            success, new_xp = streak_freeze.purchase_freeze(xp)
            if success:
                st.session_state.user_xp = new_xp
                storage.set_user_data("streak_freeze", streak_freeze.to_dict())
                if 'storage' in st.session_state:
                    st.session_state.storage.set_xp(new_xp)
                st.success("❄️ Streak Freeze purchased!")
                st.rerun()
            else:
                st.error(f"Not enough XP! Need {streak_freeze.xp_cost} XP.")
    else:
        st.caption("✅ Max freezes reached!")
    
    # Update session state for use in other functions
    st.session_state.streak_freeze = streak_freeze


__all__ = ["render_sidebar"]