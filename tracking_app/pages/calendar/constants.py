"""
Constants for the Calendar page.

Contains calendar configuration and display settings.
"""

import streamlit as st
from typing import Dict, List
from datetime import date

# Page configuration
PAGE_TITLE = "📅 Calendar - Veryfyn"
PAGE_ICON = "📅"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# Calendar display settings
CALENDAR_DAYS_SHOW = 42  # 6 weeks x 7 days
MONTH_NAV_OFFSET = 12  # Months to navigate ahead/behind

# Completion color thresholds
COMPLETION_FULL = 1.0  # 100% complete
COMPLETION_HIGH = 0.75  # 75%+ complete
COMPLETION_MEDIUM = 0.5  # 50%+ complete
COMPLETION_LOW = 0.25  # 25%+ complete
COMPLETION_NONE = 0.0  # Nothing completed

# Color scale for completion rates
COMPLETION_COLORS = {
    "complete": "#22c55e",      # Green - all done
    "high": "#4ade80",          # Light green - mostly done
    "medium": "#facc15",        # Yellow - half done
    "low": "#fb923c",           # Orange - some done
    "missed": "#ef4444",        # Red - missed
    "no_data": "#e5e7eb",       # Gray - no habits
    "future": "#f3f4f6",        # Light gray - future
    "today": "#3b82f6",         # Blue - today highlight
}

# Weekday labels
WEEKDAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEKDAY_LABELS_FULL = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]

# Month names
MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# Heatmap settings
HEATMAP_MONTHS = 12  # Show 12 months of history

# Day detail settings
MAX_DETAIL_ITEMS = 10  # Max items to show in day detail

# Cached lookup functions
@st.cache_data(ttl=3600, show_spinner=False)
def get_completion_color(rate: float) -> str:
    """
    Get color for completion rate using O(1) lookup.
    
    Args:
        rate: Completion rate (0.0 to 1.0)
        
    Returns:
        Hex color code
    """
    if rate >= COMPLETION_FULL:
        return COMPLETION_COLORS["complete"]
    elif rate >= COMPLETION_HIGH:
        return COMPLETION_COLORS["high"]
    elif rate >= COMPLETION_MEDIUM:
        return COMPLETION_COLORS["medium"]
    elif rate >= COMPLETION_LOW:
        return COMPLETION_COLORS["low"]
    elif rate > COMPLETION_NONE:
        return COMPLETION_COLORS["missed"]
    else:
        return COMPLETION_COLORS["no_data"]


@st.cache_data(ttl=3600, show_spinner=False)
def get_month_name(month: int) -> str:
    """
    Get month name from number using O(1) lookup.
    
    Args:
        month: Month number (1-12)
        
    Returns:
        Month name
    """
    if 1 <= month <= 12:
        return MONTH_NAMES[month - 1]
    return ""


@st.cache_data(ttl=3600, show_spinner=False)
def get_weekday_label(day_index: int, full: bool = False) -> str:
    """
    Get weekday label from index using O(1) lookup.
    
    Args:
        day_index: Day index (0=Monday, 6=Sunday)
        full: Return full name if True
        
    Returns:
        Weekday label
    """
    labels = WEEKDAY_LABELS_FULL if full else WEEKDAY_LABELS
    if 0 <= day_index < 7:
        return labels[day_index]
    return ""
