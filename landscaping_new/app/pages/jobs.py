"""
Jobs Page

Handles job management functionality.
"""
from __future__ import annotations
import streamlit as st
from database.queries.jobs_core import list_jobs, create_job, get_job, update_job, list_jobs_for_customer
from database.queries.customers import list_customers

def render_jobs_page() -> None:
    """Render the jobs page."""
    st.title("Job Management")
    
    # Tabs for different job operations
    tab1, tab2, tab3 = st.tabs(["View Jobs", "Add Job", "Edit Job"])
    
    with tab1:
        st.subheader("All Jobs")
        try:
            jobs = list_jobs()
            if jobs:
                for job in jobs:
                    with st.expander(f"[{job['status'].upper()}] {job['title']} - {job['customer_name']}"):
                        col1, col2, col3 = st.columns(3)
                        col1.write(f"**ID:** {job['id']}")
                        col2.write(f"**Status:** {job['status']}")
                        col3.write(f"**Scheduled:** {job['scheduled_date'] or 'Not scheduled'}")
                        
                        if job['completed_date']:
                            col1.write(f"**Completed:** {job['completed_date']}")
                        
                        if st.button(f"Select Job {job['id']}", key=f"select_job_{job['id']}"):
                            st.session_state.selected_job = job
                            st.rerun()
            else:
                st.info("No jobs found. Add a job using the 'Add Job' tab.")
        except Exception as e:
            st.error(f"Error loading jobs: {str(e)}")
    
    with tab2:
        st.subheader("Add New Job")
        try:
            customers = list_customers()
            if customers:
                customer_options = {f"{c['name']} (ID: {c['id']})": c['id'] for c in customers}
                selected_customer_display = st.selectbox("Select Customer*", list(customer_options.keys()))
                selected_customer_id = customer_options[selected_customer_display]
            else:
                st.error("No customers found. Please add a customer first.")
                selected_customer_id = None
        except Exception as e:
            st.error(f"Error loading customers: {str(e)}")
            selected_customer_id = None
        
        with st.form("add_job_form"):
            title = st.text_input("Job Title*", help="Enter the job title")
            description = st.text_area("Description", help="Enter a detailed description of the job")
            status = st.selectbox("Status", ["pending", "in_progress", "completed", "cancelled"], index=0)
            scheduled_date = st.date_input("Scheduled Date", help="Select the date for the job")
            
            submitted = st.form_submit_button("Add Job")
            if submitted:
                if title and selected_customer_id:
                    try:
                        job = create_job(
                            customer_id=selected_customer_id,
                            title=title,
                            description=description,
                            scheduled_date=str(scheduled_date) if scheduled_date else None,
                            status=status
                        )
                        if job:
                            st.success(f"Job '{title}' added successfully with ID: {job['id']}")
                        else:
                            st.error("Failed to add job")
                    except Exception as e:
                        st.error(f"Error adding job: {str(e)}")
                else:
                    st.error("Job title and customer selection are required")
    
    with tab3:
        st.subheader("Edit Job")
        if 'selected_job' in st.session_state:
            job = st.session_state.selected_job
            st.write(f"Editing job: **{job['title']}** (ID: {job['id']})")
            
            with st.form("edit_job_form"):
                title = st.text_input("Job Title", value=job['title'])
                description = st.text_area("Description", value=job['description'] or "")
                status = st.selectbox("Status", 
                                    ["pending", "in_progress", "completed", "cancelled"], 
                                    index=["pending", "in_progress", "completed", "cancelled"].index(job['status']))
                scheduled_date = st.date_input("Scheduled Date", value=job['scheduled_date'] if job['scheduled_date'] else None)
                
                submitted = st.form_submit_button("Update Job")
                if submitted:
                    try:
                        success = update_job(
                            job['id'],
                            title=title,
                            description=description,
                            status=status,
                            scheduled_date=str(scheduled_date) if scheduled_date else None
                        )
                        if success:
                            st.success("Job updated successfully")
                            # Refresh the job data
                            updated_job = get_job(job['id'])
                            if updated_job:
                                st.session_state.selected_job = updated_job
                        else:
                            st.error("Failed to update job")
                    except Exception as e:
                        st.error(f"Error updating job: {str(e)}")
        else:
            st.info("Select a job from the 'View Jobs' tab to edit.")