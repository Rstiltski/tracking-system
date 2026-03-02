"""
Data Export UI Page

Streamlit interface for exporting tracking data.
Supports JSON, CSV, and SQLite export formats.

Phase 5.1 - Data Export System
"""

import streamlit as st

from tracking_app.pages.data_export import (
    init_session_state,
    get_exporter,
    render_export_settings,
    render_module_preview,
    render_export_history,
    render_export_result,
)
from tracking_app.pages.data_export.components import run_export
from tracking_app.pages.data_export.helpers import get_all_module_names


# Page configuration
st.set_page_config(
    page_title="Data Export",
    page_icon="📤",
    layout="wide"
)


def main():
    """Main data export page."""
    # Initialize session state
    init_session_state()
    
    st.title("📤 Data Export")
    st.markdown("Export your tracking data to various formats for backup, migration, or analysis.")
    
    # Sidebar with export history
    with st.sidebar:
        render_export_history()
    
    # Get exporter
    exporter = get_exporter()
    
    if exporter is None:
        st.error("Export system is not available. Please ensure the brain module is installed.")
        st.stop()
    
    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        export_format, selected_modules, include_archived, compression, select_all = render_export_settings()
    
    with col2:
        all_modules = get_all_module_names()
        modules_to_show = all_modules if select_all else selected_modules
        render_module_preview(modules_to_show)
    
    # Export button
    st.markdown("---")
    
    if st.button("🚀 Start Export", type="primary", disabled=st.session_state.export_in_progress):
        st.session_state.export_in_progress = True
        
        result = run_export(
            exporter=exporter,
            export_format=export_format,
            selected_modules=selected_modules,
            include_archived=include_archived,
            compression=compression,
            select_all=select_all
        )
        
        if result:
            render_export_result(result, compression)
        
        exporter.close()


if __name__ == "__main__":
    main()