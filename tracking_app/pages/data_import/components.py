"""
UI components for the Data Import page.

Contains all render functions for the import interface.
"""

import streamlit as st

from .constants import (
    SUPPORTED_FILE_TYPES,
    AVAILABLE_MODULES,
    DEFAULT_DRY_RUN,
    DEFAULT_SELECTED_MODULES,
    CONFLICT_HELP,
    CONFLICT_STRATEGY_DESCRIPTIONS,
)
from .helpers import (
    get_file_info,
    preview_import,
    execute_import,
    send_import_notification,
    cleanup_temp_file,
)


def render_import_settings() -> tuple:
    """
    Render the import settings panel in the sidebar.
    
    Returns:
        Tuple of (strategy, dry_run, selected_modules)
    """
    st.header("Import Settings")
    
    # Conflict resolution strategy
    try:
        from brain.data_import.models import ConflictStrategy
        
        strategy = st.selectbox(
            "Conflict Resolution",
            options=[
                ConflictStrategy.SKIP,
                ConflictStrategy.OVERWRITE,
                ConflictStrategy.MERGE,
                ConflictStrategy.DUPLICATE,
            ],
            format_func=lambda x: x.value.title(),
            help=CONFLICT_HELP
        )
    except ImportError:
        # Fallback if brain module not available
        strategy = st.selectbox(
            "Conflict Resolution",
            options=["skip", "overwrite", "merge", "duplicate"],
            help=CONFLICT_HELP
        )
    
    # Dry run option
    dry_run = st.checkbox(
        "Preview Only (Dry Run)",
        value=DEFAULT_DRY_RUN,
        help="Don't actually import, just show what would happen"
    )
    
    # Module selection
    selected_modules = st.multiselect(
        "Modules to Import",
        options=AVAILABLE_MODULES,
        default=DEFAULT_SELECTED_MODULES,
        help="Select which data types to import"
    )
    
    return strategy, dry_run, selected_modules


def render_file_upload():
    """
    Render the file upload widget.
    
    Returns:
        Uploaded file object or None
    """
    return st.file_uploader(
        "Choose an export file",
        type=SUPPORTED_FILE_TYPES,
        help="Select a previously exported data file"
    )


def render_file_info(uploaded_file) -> None:
    """
    Render file information display.
    
    Args:
        uploaded_file: Streamlit uploaded file object
    """
    info = get_file_info(uploaded_file)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("File Name", info["name"])
    with col2:
        st.metric("File Size", f"{info['size_kb']:.1f} KB")
    with col3:
        st.metric("File Type", info["type"])


def render_import_preview(preview) -> None:
    """
    Render the import preview panel.
    
    Args:
        preview: Preview result object
    """
    st.subheader("📊 Import Preview")
    
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
        st.dataframe(
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


def render_import_result(result, dry_run: bool) -> None:
    """
    Render the import result.
    
    Args:
        result: Import result object
        dry_run: Whether this was a dry run
    """
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
    else:
        st.error(f"❌ Import failed: {result.error_message}")
        
        # Show error details
        if result.details:
            with st.expander("Error Details"):
                st.json(result.details)


def render_instructions() -> None:
    """Render import instructions when no file is uploaded."""
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


def run_import_process(
    importer,
    file_path: str,
    strategy,
    modules: list,
    dry_run: bool
):
    """
    Run the import process with progress display.
    
    Args:
        importer: DataImporter instance
        file_path: Path to the import file
        strategy: Conflict resolution strategy
        modules: List of modules to import
        dry_run: Whether this is a dry run
        
    Returns:
        Import result or None
    """
    with st.spinner("Importing data... Please wait."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Execute import
        status_text.text("Parsing file...")
        progress_bar.progress(20)
        
        result = execute_import(
            importer=importer,
            file_path=file_path,
            strategy=strategy,
            modules=modules,
            dry_run=dry_run
        )
        
        progress_bar.progress(100)
        
        if result and result.success and not dry_run:
            # Send notification
            send_import_notification(importer, result.records_imported)
        
        return result