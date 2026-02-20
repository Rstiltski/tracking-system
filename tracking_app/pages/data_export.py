"""
Data Export UI Page

Streamlit interface for exporting tracking data.
Supports JSON, CSV, and SQLite export formats.

Phase 5.1 - Data Export System
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from brain.data_export import (
    DataExporter,
    ExportFormat,
    EXPORT_MODULES,
)


def init_session_state():
    """Initialize session state variables."""
    if 'export_in_progress' not in st.session_state:
        st.session_state.export_in_progress = False
    if 'last_export' not in st.session_state:
        st.session_state.last_export = None


def main():
    st.set_page_config(
        page_title="Data Export",
        page_icon="📤",
        layout="wide"
    )
    
    init_session_state()
    
    st.title("📤 Data Export")
    st.markdown("Export your tracking data to various formats for backup, migration, or analysis.")
    
    # Sidebar with export history
    with st.sidebar:
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
    
    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Export Settings")
        
        # Format selection
        format_options = {
            'JSON': 'json',
            'CSV': 'csv',
            'SQLite': 'sqlite'
        }
        selected_format = st.selectbox(
            "Export Format",
            options=list(format_options.keys()),
            help="JSON: Structured data, easy to read\nCSV: Spreadsheet compatible\nSQLite: Complete database backup"
        )
        export_format = format_options[selected_format]
        
        # Module selection
        st.markdown("#### Modules to Export")
        
        all_modules = list(EXPORT_MODULES.keys())
        select_all = st.checkbox("Select All", value=True)
        
        if select_all:
            selected_modules = all_modules
            st.info(f"All {len(all_modules)} modules selected")
        else:
            selected_modules = st.multiselect(
                "Choose Modules",
                options=all_modules,
                default=all_modules,
                format_func=lambda x: EXPORT_MODULES[x].display_name
            )
        
        # Additional options
        st.markdown("#### Options")
        include_archived = st.checkbox("Include archived data", value=False)
        compression = st.checkbox("Compress output (ZIP)", value=True)
    
    with col2:
        st.subheader("Module Preview")
        
        for module_name in selected_modules[:5]:  # Show first 5
            module = EXPORT_MODULES.get(module_name)
            if module:
                with st.expander(f"📦 {module.display_name}"):
                    st.write(module.description)
                    st.write(f"**Tables:** {', '.join(module.tables)}")
        
        if len(selected_modules) > 5:
            st.info(f"... and {len(selected_modules) - 5} more modules")
    
    # Export button
    st.markdown("---")
    
    if st.button("🚀 Start Export", type="primary", disabled=st.session_state.export_in_progress):
        st.session_state.export_in_progress = True
        
        with st.spinner("Exporting data..."):
            try:
                # Get database path
                db_path = Path(__file__).parent.parent.parent / 'tracking.db'
                export_dir = Path(__file__).parent.parent.parent / 'exports'
                
                # Create exporter
                exporter = DataExporter(
                    db_path=str(db_path),
                    export_dir=str(export_dir)
                )
                
                # Create and execute request
                request = exporter.create_request(
                    user_id='default',
                    format=export_format,
                    modules=selected_modules if not select_all else [],
                    include_archived=include_archived,
                    compression=compression
                )
                
                result = exporter.execute(request.id)
                
                if result.success:
                    st.session_state.last_export = {
                        'format': export_format,
                        'records': result.record_count,
                        'size': result.file_size_bytes,
                        'path': result.file_path
                    }
                    
                    st.success(f"✓ Export complete!")
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
                
                exporter.close()
                
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                st.session_state.export_in_progress = False


if __name__ == "__main__":
    main()