"""
UI components for the Data Export page.

Contains all render functions for the export interface.
"""

import streamlit as st
from pathlib import Path

from .constants import (
    FORMAT_OPTIONS,
    DEFAULT_INCLUDE_ARCHIVED,
    DEFAULT_COMPRESSION,
    DEFAULT_SELECT_ALL,
    MODULE_PREVIEW_LIMIT,
)
from .helpers import get_export_modules, get_all_module_names, execute_export


def render_export_history() -> None:
    """Render the export history in the sidebar."""
    st.header("Recent Exports")
    
    if st.session_state.last_export:
        export = st.session_state.last_export
        st.success(f"✓ {export['format'].upper()}")
        st.write(f"Records: {export['records']}")
        st.write(f"Size: {export['size']} bytes")
        if export.get('path'):
            st.code(export['path'], language=None)
    else:
        st.info("No exports yet")


def render_export_settings() -> tuple:
    """
    Render the export settings panel.
    
    Returns:
        Tuple of (selected_format, selected_modules, include_archived, compression)
    """
    st.subheader("Export Settings")
    
    # Format selection
    selected_format_name = st.selectbox(
        "Export Format",
        options=list(FORMAT_OPTIONS.keys()),
        help="JSON: Structured data, easy to read\nCSV: Spreadsheet compatible\nSQLite: Complete database backup"
    )
    export_format = FORMAT_OPTIONS[selected_format_name]
    
    # Module selection
    st.markdown("#### Modules to Export")
    
    all_modules = get_all_module_names()
    select_all = st.checkbox("Select All", value=DEFAULT_SELECT_ALL)
    
    if select_all:
        selected_modules = all_modules
        st.info(f"All {len(all_modules)} modules selected")
    else:
        export_modules = get_export_modules()
        selected_modules = st.multiselect(
            "Choose Modules",
            options=all_modules,
            default=all_modules,
            format_func=lambda x: export_modules.get(x, type('obj', (), {'display_name': x})()).display_name
        )
    
    # Additional options
    st.markdown("#### Options")
    include_archived = st.checkbox("Include archived data", value=DEFAULT_INCLUDE_ARCHIVED)
    compression = st.checkbox("Compress output (ZIP)", value=DEFAULT_COMPRESSION)
    
    return export_format, selected_modules if not select_all else [], include_archived, compression, select_all


def render_module_preview(selected_modules: list) -> None:
    """
    Render the module preview panel.
    
    Args:
        selected_modules: List of selected module names
    """
    st.subheader("Module Preview")
    
    export_modules = get_export_modules()
    
    for module_name in selected_modules[:MODULE_PREVIEW_LIMIT]:
        module = export_modules.get(module_name)
        if module:
            with st.expander(f"📦 {module.display_name}"):
                st.write(module.description)
                st.write(f"**Tables:** {', '.join(module.tables)}")
    
    if len(selected_modules) > MODULE_PREVIEW_LIMIT:
        st.info(f"... and {len(selected_modules) - MODULE_PREVIEW_LIMIT} more modules")


def render_export_result(result, compression: bool) -> None:
    """
    Render the export result.
    
    Args:
        result: Export result object
        compression: Whether compression was enabled
    """
    if result.success:
        st.session_state.last_export = {
            'format': result.format,
            'records': result.record_count,
            'size': result.file_size_bytes,
            'path': result.file_path
        }
        
        st.success("✓ Export complete!")
        st.metric("Records Exported", result.record_count)
        st.metric("File Size", f"{result.file_size_bytes:,} bytes")
        
        # Download link
        if result.file_path:
            file_path = Path(result.file_path)
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    st.download_button(
                        label="📥 Download Export",
                        data=f,
                        file_name=file_path.name,
                        mime="application/zip" if compression else "application/json"
                    )
    else:
        st.error(f"Export failed: {result.error_message}")


def run_export(exporter, export_format: str, selected_modules: list, 
               include_archived: bool, compression: bool, select_all: bool):
    """
    Run the export process.
    
    Args:
        exporter: DataExporter instance
        export_format: Format to export
        selected_modules: List of modules to export
        include_archived: Whether to include archived data
        compression: Whether to compress output
        select_all: Whether all modules are selected
        
    Returns:
        Export result or None
    """
    with st.spinner("Exporting data..."):
        try:
            result = execute_export(
                exporter=exporter,
                export_format=export_format,
                selected_modules=selected_modules if not select_all else [],
                include_archived=include_archived,
                compression=compression
            )
            return result
        except Exception as e:
            st.error(f"Error: {e}")
            return None
        finally:
            st.session_state.export_in_progress = False