"""
Data Import Page - Streamlit UI

Python Streamlit interface for data import functionality.
Allows users to upload export files and import data.

All implementation is in Python 3.10+ using Streamlit
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
from datetime import datetime

from brain.data_import import DataImporter
from brain.data_import.models import ConflictStrategy


def show_data_import_page():
    """Render the data import page."""
    st.set_page_config(
        page_title="Import Data",
        page_icon="📥",
        layout="wide"
    )
    
    st.title("📥 Import Data")
    st.markdown("""
    Restore your data from a previous export or import from another system.
    
    **Supported formats:** JSON, CSV, ZIP (CSV collection)
    """)
    
    # Sidebar - Import settings
    with st.sidebar:
        st.header("Import Settings")
        
        # Conflict resolution strategy
        strategy = st.selectbox(
            "Conflict Resolution",
            options=[
                ConflictStrategy.SKIP,
                ConflictStrategy.OVERWRITE,
                ConflictStrategy.MERGE,
                ConflictStrategy.DUPLICATE,
            ],
            format_func=lambda x: x.value.title(),
            help="How to handle records that already exist"
        )
        
        # Dry run option
        dry_run = st.checkbox(
            "Preview Only (Dry Run)",
            value=True,
            help="Don't actually import, just show what would happen"
        )
        
        # Module selection
        available_modules = [
            "habits", "tasks", "goals", "transactions",
            "health_entries", "time_entries", "achievements"
        ]
        selected_modules = st.multiselect(
            "Modules to Import",
            options=available_modules,
            default=available_modules,
            help="Select which data types to import"
        )
    
    # Main content - File upload
    uploaded_file = st.file_uploader(
        "Choose an export file",
        type=["json", "csv", "zip"],
        help="Select a previously exported data file"
    )
    
    if uploaded_file is not None:
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
        with col3:
            file_type = uploaded_file.name.split('.')[-1].upper()
            st.metric("File Type", file_type)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        try:
            # Initialize importer
            from tracking_app.database import get_db
            db = get_db()
            importer = DataImporter(db_connection=db)
            
            # Preview import
            st.subheader("📊 Import Preview")
            
            with st.spinner("Analyzing file..."):
                preview = importer.preview(tmp_path, selected_modules)
            
            # Display preview
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Total Records",
                    preview.total_records,
                    help="Total number of records to import"
                )
            with col2:
                st.metric(
                    "Conflicts Detected",
                    preview.conflicts_detected,
                    help="Records that already exist in database"
                )
            with col3:
                st.metric(
                    "Est. Duration",
                    f"{preview.estimated_duration_seconds:.1f}s",
                    help="Estimated import time"
                )
            
            # Records by module
            if preview.records_by_module:
                st.write("**Records by Module:**")
                preview_df = st.dataframe(
                    {
                        "Module": list(preview.records_by_module.keys()),
                        "Records": list(preview.records_by_module.values()),
                    },
                    hide_index=True,
                    use_container_width=True,
                )
            
            # Warnings
            if preview.warnings:
                st.warning(f"⚠️ {len(preview.warnings)} warnings detected")
                for warning in preview.warnings:
                    st.write(f"- {warning}")
            
            # Import button
            st.subheader("🚀 Execute Import")
            
            if dry_run:
                st.info("ℹ️ Dry run mode - no data will be imported")
            
            if st.button(
                "Import Data" if not dry_run else "Preview Import",
                type="primary",
                disabled=preview.total_records == 0
            ):
                execute_import(
                    importer=importer,
                    file_path=tmp_path,
                    strategy=strategy,
                    modules=selected_modules,
                    dry_run=dry_run
                )
        
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    else:
        # No file uploaded - show instructions
        st.info("👆 Upload an export file to begin")
        
        st.markdown("""
        ### How to Import Data
        
        1. **Select Export File** - Choose a previously exported JSON, CSV, or ZIP file
        2. **Configure Settings** - Use the sidebar to set conflict resolution and modules
        3. **Preview** - Review what will be imported (automatic)
        4. **Import** - Click the import button to execute
        
        ### Conflict Resolution Strategies
        
        - **Skip** - Keep existing records, skip duplicates (safest)
        - **Overwrite** - Replace existing records with imported data
        - **Merge** - Combine fields from both records
        - **Duplicate** - Keep both records with new IDs
        
        ### Tips
        
        - Always preview before importing
        - Start with a dry run to see what will happen
        - Backup your data before large imports
        """)


def execute_import(
    importer: DataImporter,
    file_path: str,
    strategy: ConflictStrategy,
    modules: list,
    dry_run: bool
):
    """Execute the import operation."""
    from brain.notifications.engine import NotificationEngine
    
    with st.spinner("Importing data... Please wait."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Execute import
        status_text.text("Parsing file...")
        progress_bar.progress(20)
        
        result = importer.import_file(
            file_path=file_path,
            user_id="default",  # TODO: Get from session
            strategy=strategy,
            modules=modules,
            dry_run=dry_run
        )
        
        progress_bar.progress(100)
        
        # Display result
        if result.success:
            st.success("✅ Import completed successfully!")
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Records Imported",
                    result.records_imported,
                    help="Successfully imported records"
                )
            with col2:
                st.metric(
                    "Records Skipped",
                    result.records_skipped,
                    help="Records skipped due to conflicts"
                )
            with col3:
                st.metric(
                    "Records Failed",
                    result.records_failed,
                    help="Records that failed to import"
                )
            
            # Conflicts resolved
            if result.conflicts_resolved > 0:
                st.info(f"Resolved {result.conflicts_resolved} conflicts")
            
            # Dry run notice
            if dry_run:
                st.info("ℹ️ This was a preview. No data was actually imported.")
                st.button("Execute Real Import", type="primary")
            
            # Send notification
            try:
                engine = NotificationEngine(db=importer.db)
                engine.create_notification(
                    type="system",
                    title="Import Complete",
                    message=f"Successfully imported {result.records_imported} records",
                    priority="medium"
                )
            except Exception:
                pass  # Notifications might not be available
        
        else:
            st.error(f"❌ Import failed: {result.error_message}")
            
            # Show error details
            if result.details:
                with st.expander("Error Details"):
                    st.json(result.details)


if __name__ == "__main__":
    show_data_import_page()
