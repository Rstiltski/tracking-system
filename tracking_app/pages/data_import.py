"""
Data Import Page - Streamlit UI

Python Streamlit interface for data import functionality.
Allows users to upload export files and import data.

All implementation is in Python 3.10+ using Streamlit
"""

import streamlit as st

from tracking_app.pages.data_import import (
    init_session_state,
    get_importer,
    render_import_settings,
    render_file_upload,
    render_file_info,
    render_import_preview,
    render_import_result,
    render_instructions,
)
from tracking_app.pages.data_import.helpers import save_uploaded_file, cleanup_temp_file, preview_import
from tracking_app.pages.data_import.components import run_import_process


# Page configuration
st.set_page_config(
    page_title="Import Data",
    page_icon="📥",
    layout="wide"
)


def main():
    """Main data import page."""
    # Initialize session state
    init_session_state()
    
    st.title("📥 Import Data")
    st.markdown("""
    Restore your data from a previous export or import from another system.
    
    **Supported formats:** JSON, CSV, ZIP (CSV collection)
    """)
    
    # Sidebar - Import settings
    with st.sidebar:
        strategy, dry_run, selected_modules = render_import_settings()
    
    # Get importer
    importer = get_importer()
    
    if importer is None:
        st.error("Import system is not available. Please ensure the brain module is installed.")
        st.stop()
    
    # Main content - File upload
    uploaded_file = render_file_upload()
    
    if uploaded_file is not None:
        # Display file info
        render_file_info(uploaded_file)
        
        # Save to temporary file
        tmp_path, error = save_uploaded_file(uploaded_file)
        
        if error:
            st.error(f"Error saving file: {error}")
            st.stop()
        
        try:
            # Preview import
            with st.spinner("Analyzing file..."):
                preview = preview_import(importer, tmp_path, selected_modules)
            
            if preview:
                render_import_preview(preview)
                
                # Import button
                st.subheader("🚀 Execute Import")
                
                if dry_run:
                    st.info("ℹ️ Dry run mode - no data will be imported")
                
                if st.button(
                    "Import Data" if not dry_run else "Preview Import",
                    type="primary",
                    disabled=preview.total_records == 0
                ):
                    result = run_import_process(
                        importer=importer,
                        file_path=tmp_path,
                        strategy=strategy,
                        modules=selected_modules,
                        dry_run=dry_run
                    )
                    
                    if result:
                        render_import_result(result, dry_run)
            else:
                st.error("Could not analyze the file. Please check the format.")
        
        finally:
            # Clean up temp file
            cleanup_temp_file(tmp_path)
    
    else:
        # No file uploaded - show instructions
        render_instructions()


if __name__ == "__main__":
    main()