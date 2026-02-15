"""
Navigation Module

Handles sidebar navigation and page routing for the application.
Following the architecture rules, this provides centralized navigation management.
"""
from __future__ import annotations
import streamlit as st
from typing import Dict, Any, Callable
from app.auth.session import get_user_role, has_permission

def render_sidebar() -> None:
    """Render the application sidebar with navigation."""
    user_role = get_user_role()
    
    # Display user info
    if st.session_state.user:
        st.sidebar.markdown(f"**Welcome, {st.session_state.user['username']}**")
        st.sidebar.markdown(f"*Role: {st.session_state.user['role']}*")
        st.sidebar.divider()
    
    # Navigation based on user role
    if user_role == 'admin':
        render_admin_navigation()
    elif user_role == 'manager':
        render_manager_navigation()
    elif user_role == 'staff':
        render_staff_navigation()
    elif user_role == 'customer':
        render_customer_navigation()
    else:
        # Guest/Not logged in
        st.sidebar.info("Please log in to access features")
    
    # Common navigation items
    st.sidebar.divider()
    
    # Logout button
    if st.session_state.get('authenticated', False):
        if st.sidebar.button("Logout", key="logout_btn"):
            # Import here to avoid circular imports
            from app.auth.login import logout
            logout()

def render_admin_navigation() -> None:
    """Render navigation for admin users."""
    st.sidebar.header("Admin Panel")
    
    # Dashboard
    if st.sidebar.button("📊 Dashboard", key="nav_dashboard"):
        st.session_state.current_page = "Dashboard"
        st.rerun()
    
    # Customer Management
    if st.sidebar.button("👥 Customers", key="nav_customers"):
        st.session_state.current_page = "Customers"
        st.rerun()
    
    # Job Management
    if st.sidebar.button("📝 Jobs", key="nav_jobs"):
        st.session_state.current_page = "Jobs"
        st.rerun()
    
    # Staff Management
    if st.sidebar.button("👷 Staff", key="nav_staff"):
        st.session_state.current_page = "Staff"
        st.rerun()
    
    # Scheduling
    if st.sidebar.button("📅 Schedule", key="nav_schedule"):
        st.session_state.current_page = "Schedule"
        st.rerun()
    
    # Invoicing
    if st.sidebar.button("💰 Invoices", key="nav_invoices"):
        st.session_state.current_page = "Invoices"
        st.rerun()
    
    # Reports
    if st.sidebar.button("📈 Reports", key="nav_reports"):
        st.session_state.current_page = "Reports"
        st.rerun()
    
    # AI Assistant
    if st.sidebar.button("🤖 AI Assistant", key="nav_ai_assistant"):
        st.session_state.current_page = "AI Assistant"
        st.rerun()
    
    # Admin Settings
    if st.sidebar.button("⚙️ Admin Settings", key="nav_admin_settings"):
        st.session_state.current_page = "Admin Settings"
        st.rerun()

def render_manager_navigation() -> None:
    """Render navigation for manager users."""
    st.sidebar.header("Management")
    
    # Dashboard
    if st.sidebar.button("📊 Dashboard", key="nav_dashboard"):
        st.session_state.current_page = "Dashboard"
        st.rerun()
    
    # Customer Management
    if st.sidebar.button("👥 Customers", key="nav_customers"):
        st.session_state.current_page = "Customers"
        st.rerun()
    
    # Job Management
    if st.sidebar.button("📝 Jobs", key="nav_jobs"):
        st.session_state.current_page = "Jobs"
        st.rerun()
    
    # Scheduling
    if st.sidebar.button("📅 Schedule", key="nav_schedule"):
        st.session_state.current_page = "Schedule"
        st.rerun()
    
    # Invoicing
    if st.sidebar.button("💰 Invoices", key="nav_invoices"):
        st.session_state.current_page = "Invoices"
        st.rerun()
    
    # Reports
    if st.sidebar.button("📈 Reports", key="nav_reports"):
        st.session_state.current_page = "Reports"
        st.rerun()
    
    # AI Assistant
    if st.sidebar.button("🤖 AI Assistant", key="nav_ai_assistant"):
        st.session_state.current_page = "AI Assistant"
        st.rerun()

def render_staff_navigation() -> None:
    """Render navigation for staff users."""
    st.sidebar.header("Staff Tools")
    
    # Dashboard
    if st.sidebar.button("📊 Dashboard", key="nav_dashboard"):
        st.session_state.current_page = "Dashboard"
        st.rerun()
    
    # My Jobs
    if st.sidebar.button("📝 My Jobs", key="nav_my_jobs"):
        st.session_state.current_page = "My Jobs"
        st.rerun()
    
    # Time Tracking
    if st.sidebar.button("⏱️ Time Tracking", key="nav_time_tracking"):
        st.session_state.current_page = "Time Tracking"
        st.rerun()
    
    # Schedule
    if st.sidebar.button("📅 My Schedule", key="nav_my_schedule"):
        st.session_state.current_page = "My Schedule"
        st.rerun()

def render_customer_navigation() -> None:
    """Render navigation for customer users."""
    st.sidebar.header("Customer Portal")
    
    # Dashboard
    if st.sidebar.button("🏠 Home", key="nav_customer_home"):
        st.session_state.current_page = "Customer Home"
        st.rerun()
    
    # My Jobs
    if st.sidebar.button("📝 My Jobs", key="nav_customer_jobs"):
        st.session_state.current_page = "Customer Jobs"
        st.rerun()
    
    # Invoices
    if st.sidebar.button("💰 My Invoices", key="nav_customer_invoices"):
        st.session_state.current_page = "Customer Invoices"
        st.rerun()
    
    # Messages
    if st.sidebar.button("💬 Messages", key="nav_customer_messages"):
        st.session_state.current_page = "Customer Messages"
        st.rerun()

def get_page_handler(page_name: str) -> Callable[[], None]:
    """Get the handler function for a specific page."""
    # This would map page names to their respective handler functions
    # For now, we'll return a generic handler
    handlers = {
        "Dashboard": render_dashboard_page,
        "Customers": render_customers_page,
        "Jobs": render_jobs_page,
        "Staff": render_staff_page,
        "Schedule": render_schedule_page,
        "Invoices": render_invoices_page,
        "Reports": render_reports_page,
        "AI Assistant": render_ai_assistant_page,
        "Admin Settings": render_admin_settings_page,
        "My Jobs": render_my_jobs_page,
        "Time Tracking": render_time_tracking_page,
        "My Schedule": render_my_schedule_page,
        "Customer Home": render_customer_home_page,
        "Customer Jobs": render_customer_jobs_page,
        "Customer Invoices": render_customer_invoices_page,
        "Customer Messages": render_customer_messages_page,
    }
    
    return handlers.get(page_name, render_default_page)

def render_current_page() -> bool:
    """Render the currently selected page."""
    current_page = st.session_state.get('current_page', 'Dashboard')
    handler = get_page_handler(current_page)
    
    if handler:
        handler()
        return True
    else:
        return False

def render_dashboard_page() -> None:
    """Render the dashboard page."""
    st.title("Dashboard")
    st.write("Welcome to the Landscaping Management System Dashboard!")
    
    # Display summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Customers", value="12", delta="+2 from last week")
    with col2:
        st.metric(label="Active Jobs", value="8", delta="-1 from yesterday")
    with col3:
        st.metric(label="Completed Today", value="3", delta="+1 from yesterday")
    with col4:
        st.metric(label="Pending Invoices", value="$2,450", delta="+$250 from last week")

def render_customers_page() -> None:
    """Render the customers page."""
    st.title("Customer Management")
    st.write("Manage your customers here.")
    
    # This would include customer list, add customer form, etc.
    st.info("Customer management functionality coming soon...")

def render_jobs_page() -> None:
    """Render the jobs page."""
    st.title("Job Management")
    st.write("Manage your jobs here.")
    
    # This would include job list, add job form, etc.
    st.info("Job management functionality coming soon...")

def render_staff_page() -> None:
    """Render the staff page."""
    st.title("Staff Management")
    st.write("Manage your staff members here.")
    
    # This would include staff list, add staff form, etc.
    st.info("Staff management functionality coming soon...")

def render_schedule_page() -> None:
    """Render the schedule page."""
    st.title("Schedule")
    st.write("View and manage your schedule here.")
    
    # This would include calendar view, scheduling tools, etc.
    st.info("Scheduling functionality coming soon...")

def render_invoices_page() -> None:
    """Render the invoices page."""
    st.title("Invoice Management")
    st.write("Manage your invoices here.")
    
    # This would include invoice list, create invoice form, etc.
    st.info("Invoice management functionality coming soon...")

def render_reports_page() -> None:
    """Render the reports page."""
    st.title("Reports")
    st.write("View system reports here.")
    
    # This would include various reports
    st.info("Reporting functionality coming soon...")

def render_ai_assistant_page() -> None:
    """Render the AI assistant page."""
    st.title("AI Assistant")
    st.write("Interact with the AI assistant here.")
    
    # This would include AI chat interface
    st.info("AI assistant functionality coming soon...")

def render_admin_settings_page() -> None:
    """Render the admin settings page."""
    st.title("Admin Settings")
    st.write("Configure system settings here.")
    
    # This would include system configuration options
    st.info("Admin settings functionality coming soon...")

def render_my_jobs_page() -> None:
    """Render the staff's jobs page."""
    st.title("My Jobs")
    st.write("View jobs assigned to you.")
    
    # This would include jobs assigned to the current user
    st.info("My jobs functionality coming soon...")

def render_time_tracking_page() -> None:
    """Render the time tracking page."""
    st.title("Time Tracking")
    st.write("Track your work hours here.")
    
    # This would include time tracking functionality
    st.info("Time tracking functionality coming soon...")

def render_my_schedule_page() -> None:
    """Render the staff's schedule page."""
    st.title("My Schedule")
    st.write("View your personal schedule.")
    
    # This would include personal calendar view
    st.info("My schedule functionality coming soon...")

def render_customer_home_page() -> None:
    """Render the customer home page."""
    st.title("Customer Portal")
    st.write("Welcome to your customer portal.")
    
    # This would include customer-specific dashboard
    st.info("Customer portal functionality coming soon...")

def render_customer_jobs_page() -> None:
    """Render the customer's jobs page."""
    st.title("My Jobs")
    st.write("View jobs associated with your account.")
    
    # This would include jobs linked to the customer
    st.info("Customer jobs functionality coming soon...")

def render_customer_invoices_page() -> None:
    """Render the customer's invoices page."""
    st.title("My Invoices")
    st.write("View and pay your invoices here.")
    
    # This would include invoices for the customer
    st.info("Customer invoices functionality coming soon...")

def render_customer_messages_page() -> None:
    """Render the customer's messages page."""
    st.title("Messages")
    st.write("View messages from our team.")
    
    # This would include messaging functionality
    st.info("Customer messaging functionality coming soon...")

def render_default_page() -> None:
    """Render the default page when no specific page is found."""
    st.title("Page Not Found")
    st.error(f"Page '{st.session_state.get('current_page', 'Unknown')}' not found.")
    st.write("Please select a valid page from the navigation menu.")