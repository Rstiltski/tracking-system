"""
Dashboard Page

The main dashboard page for the application.
"""
from __future__ import annotations
import streamlit as st
from database.queries.misc import get_system_stats

def render_dashboard_page() -> None:
    """Render the dashboard page."""
    st.title("Dashboard")
    st.write("Welcome to the Landscaping Management System Dashboard!")
    
    # Get system stats
    try:
        stats = get_system_stats()
        
        # Display summary cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="Customers", value=stats.get('customer_count', 0))
        with col2:
            st.metric(label="Active Jobs", value=stats.get('job_count', 0))
        with col3:
            st.metric(label="Team Members", value=stats.get('user_count', 0))
        with col4:
            st.metric(label="Database Size", value=f"{stats.get('database_size_mb', 0)} MB")
    except Exception as e:
        st.error(f"Could not load system stats: {str(e)}")
    
    # Recent activity section
    st.subheader("Recent Activity")
    st.write("This section would show recent activity in the system.")
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Create New Job"):
            st.session_state.current_page = "Jobs"
            st.rerun()
    with col2:
        if st.button("Add New Customer"):
            st.session_state.current_page = "Customers"
            st.rerun()
    with col3:
        if st.button("View Schedule"):
            st.session_state.current_page = "Schedule"
            st.rerun()
    
    # System status
    st.subheader("System Status")
    st.success("All systems operational")