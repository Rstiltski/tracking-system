"""
Session state management for the Weekly Review page.
"""

from datetime import date
from typing import Any, Optional

# Conditional streamlit import for test compatibility
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None


def init_session_state() -> None:
    """Initialize session state variables for weekly review."""
    if not HAS_STREAMLIT:
        return

    # Storage initialization
    if 'storage' not in st.session_state:
        from tracking_app.storage import get_storage
        st.session_state.storage = get_storage()

    # Review cache
    if 'review_cache' not in st.session_state:
        st.session_state.review_cache = None

    # Selected week/year
    current_week = date.today().isocalendar().week
    current_year = date.today().isocalendar().year

    if 'selected_week' not in st.session_state:
        st.session_state.selected_week = current_week

    if 'selected_year' not in st.session_state:
        st.session_state.selected_year = current_year


def get_storage() -> Any:
    """Get the storage instance from session state."""
    if HAS_STREAMLIT and 'storage' in st.session_state:
        return st.session_state.storage
    return None


def get_review_cache() -> Optional[Any]:
    """Get cached review from session state."""
    if HAS_STREAMLIT and 'review_cache' in st.session_state:
        return st.session_state.review_cache
    return None


def set_review_cache(review: Any) -> None:
    """Set cached review in session state."""
    if HAS_STREAMLIT:
        st.session_state.review_cache = review


def clear_review_cache() -> None:
    """Clear cached review from session state."""
    if HAS_STREAMLIT and 'review_cache' in st.session_state:
        del st.session_state.review_cache


def get_selected_week() -> int:
    """Get selected week from session state."""
    if HAS_STREAMLIT and 'selected_week' in st.session_state:
        return st.session_state.selected_week
    return date.today().isocalendar().week


def set_selected_week(week: int) -> None:
    """Set selected week in session state."""
    if HAS_STREAMLIT:
        st.session_state.selected_week = week


def get_selected_year() -> int:
    """Get selected year from session state."""
    if HAS_STREAMLIT and 'selected_year' in st.session_state:
        return st.session_state.selected_year
    return date.today().isocalendar().year


def set_selected_year(year: int) -> None:
    """Set selected year in session state."""
    if HAS_STREAMLIT:
        st.session_state.selected_year = year