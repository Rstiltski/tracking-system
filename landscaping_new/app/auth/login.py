"""
Authentication Module

Handles authentication-related functionality for the application.
Following the architecture rules, this separates authentication concerns
from other application logic.
"""
from __future__ import annotations
import streamlit as st
import bcrypt
from typing import Dict, Any, Optional
from database.queries.users import authenticate_user, create_user as db_create_user

def show_login_page() -> None:
    """Display the login page."""
    st.title("Landscaping Management System")
    st.subheader("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if username and password:
                user = authenticate_user(username, password)
                if user:
                    # Successful login
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.session_state.last_activity = __import__('time').time()
                    st.success(f"Welcome back, {user['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please enter both username and password")

def show_first_time_setup() -> None:
    """Display the first-time setup page for creating the initial admin user."""
    st.title("First-Time Setup")
    st.subheader("Create Initial Admin Account")
    
    with st.form("setup_form"):
        username = st.text_input("Admin Username", value="admin")
        email = st.text_input("Admin Email", value="admin@landscaping.com")
        password = st.text_input("Admin Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        submitted = st.form_submit_button("Create Admin Account")
        
        if submitted:
            if not username or not email or not password:
                st.error("All fields are required")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                try:
                    user = db_create_user(username=username, email=email, password=password, role='admin')
                    if user:
                        st.success("Admin account created successfully! Please log in.")
                        st.rerun()
                    else:
                        st.error("Failed to create admin account")
                except ValueError as e:
                    st.error(f"Error creating account: {str(e)}")

def show_password_change_form() -> None:
    """Display form for mandatory password change."""
    st.title("Password Change Required")
    st.subheader("Please change your password")
    
    with st.form("password_change_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("Change Password")
        
        if submitted:
            if not current_password or not new_password or not confirm_new_password:
                st.error("All fields are required")
            elif new_password != confirm_new_password:
                st.error("New passwords do not match")
            elif len(new_password) < 8:
                st.error("New password must be at least 8 characters long")
            else:
                # Attempt to change password
                from database.queries.users import change_password
                success = change_password(st.session_state.user['id'], new_password, current_password)
                
                if success:
                    # Update session state to reflect password change requirement is fulfilled
                    st.session_state.user['must_change_password'] = 0
                    st.success("Password changed successfully!")
                    st.rerun()
                else:
                    st.error("Current password is incorrect")

def logout() -> None:
    """Handle user logout."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.current_page = "Home"
    st.success("Logged out successfully")
    st.rerun()