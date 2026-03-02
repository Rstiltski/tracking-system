"""
Session state management for the Template Sharing page.
"""

import streamlit as st
from typing import Any, Optional, List

from .constants import DEFAULT_USER_ID


def init_session_state() -> None:
    """Initialize session state variables for template sharing."""
    # Storage and user
    if 'storage' not in st.session_state:
        from tracking_app.storage import get_storage
        st.session_state.storage = get_storage()
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = DEFAULT_USER_ID
    
    # Search and filter state
    if 'template_search' not in st.session_state:
        st.session_state.template_search = ""
    
    if 'template_category' not in st.session_state:
        st.session_state.template_category = "All"
    
    # Selected tab
    if 'selected_tab' not in st.session_state:
        st.session_state.selected_tab = None
    
    # Cloned templates
    if 'cloned_templates' not in st.session_state:
        st.session_state.cloned_templates = []
    
    # Shared templates
    if 'shared_templates' not in st.session_state:
        st.session_state.shared_templates = []


def get_user_id() -> str:
    """Get the current user ID."""
    return st.session_state.user_id


def get_storage() -> Any:
    """Get the storage instance."""
    return st.session_state.storage


def get_template_search() -> str:
    """Get the current search query."""
    return st.session_state.template_search


def set_template_search(value: str) -> None:
    """Set the search query."""
    st.session_state.template_search = value


def get_template_category() -> str:
    """Get the selected category filter."""
    return st.session_state.template_category


def set_template_category(value: str) -> None:
    """Set the category filter."""
    st.session_state.template_category = value


def add_cloned_template(template_id: str) -> None:
    """Add a cloned template to the list."""
    if template_id not in st.session_state.cloned_templates:
        st.session_state.cloned_templates.append(template_id)


def add_shared_template(template: dict) -> None:
    """Add a shared template to the list."""
    st.session_state.shared_templates.append(template)


def get_cloned_templates() -> List[str]:
    """Get list of cloned template IDs."""
    return st.session_state.cloned_templates


def get_shared_templates() -> List[dict]:
    """Get list of shared templates."""
    return st.session_state.shared_templates