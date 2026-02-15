"""
Session Management Module

Handles session state initialization and management for the application.
Following the architecture rules, this centralizes session state management.
"""
from __future__ import annotations
import streamlit as st
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

def initialize_session_state() -> None:
    """Initialize all required session state variables."""
    # Authentication state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = time.time()
    
    # Navigation state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
    
    # UI state
    if 'show_sidebar' not in st.session_state:
        st.session_state.show_sidebar = True
    
    if 'theme' not in st.session_state:
        st.session_state.theme = "light"
    
    # Feature flags and settings
    if 'feature_flags' not in st.session_state:
        st.session_state.feature_flags = {}
    
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {}
    
    # Temporary state for forms
    if 'temp_data' not in st.session_state:
        st.session_state.temp_data = {}
    
    # Neural link handshake state
    if 'neural_handshake' not in st.session_state:
        st.session_state.neural_handshake = None
    
    # Company information (loaded from settings)
    if 'company_name' not in st.session_state:
        st.session_state.company_name = "Landscaping Co."
    
    # AI provider settings
    if 'current_provider' not in st.session_state:
        st.session_state.current_provider = 'local'
    
    if 'chat_mode' not in st.session_state:
        st.session_state.chat_mode = 'coding'

def handle_magic_links() -> None:
    """Handle magic links (password reset, invitation links, etc.)."""
    query_params = st.query_params
    
    # Handle password reset token
    if "reset_token" in query_params:
        token = query_params["reset_token"]
        # Process password reset token
        # This would validate the token and show password reset form
        st.session_state.show_password_reset = True
        st.session_state.reset_token = token
    
    # Handle invitation token
    if "invite_token" in query_params:
        token = query_params["invite_token"]
        # Process invitation token
        # This would validate the token and show account creation form
        st.session_state.show_invitation_form = True
        st.session_state.invite_token = token
    
    # Handle customer portal token
    if "customer_token" in query_params:
        token = query_params["customer_token"]
        # Process customer portal token
        st.session_state.customer_authenticated = True
        st.session_state.customer_token = token

def check_session_timeout() -> bool:
    """Check if the session has timed out and handle accordingly."""
    timeout_duration = 60 * 60  # 1 hour in seconds
    
    # Check if user has been inactive too long
    if time.time() - st.session_state.last_activity > timeout_duration:
        # Session timed out
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.current_page = "Home"
        st.warning("Your session has expired due to inactivity. Please log in again.")
        st.rerun()
        return True
    
    # Update last activity
    st.session_state.last_activity = time.time()
    return False

def initialize_neural_link() -> None:
    """Initialize neural link handshake with AI systems."""
    # This would establish a connection with AI systems
    # For now, we'll just set a timestamp
    st.session_state.neural_handshake = {
        'connected': True,
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }

def update_last_activity() -> None:
    """Update the last activity timestamp."""
    st.session_state.last_activity = time.time()

def is_user_authenticated() -> bool:
    """Check if the user is authenticated."""
    return st.session_state.get('authenticated', False)

def get_current_user() -> Optional[Dict[str, Any]]:
    """Get the current authenticated user."""
    return st.session_state.get('user')

def get_user_role() -> Optional[str]:
    """Get the role of the current user."""
    user = get_current_user()
    return user.get('role') if user else None

def has_permission(permission: str) -> bool:
    """Check if the current user has a specific permission."""
    user = get_current_user()
    if not user:
        return False
    
    # For now, implement basic role-based permissions
    role = user.get('role', 'guest')
    
    # Define role permissions
    permissions = {
        'admin': ['read', 'write', 'delete', 'admin'],
        'manager': ['read', 'write', 'delete'],
        'staff': ['read', 'write'],
        'customer': ['read']
    }
    
    user_perms = permissions.get(role, [])
    return permission in user_perms or 'admin' in user_perms

def require_permission(permission: str) -> bool:
    """Decorator-like function to require a specific permission."""
    if not has_permission(permission):
        st.error(f"You don't have permission to perform this action ({permission})")
        return False
    return True