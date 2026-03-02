"""
Backup & Restore UI Page

Streamlit interface for managing database backups.
Supports full backups, restore, and verification.

Phase 5.3 - Backup & Restore System
"""

import streamlit as st

from tracking_app.pages.backup_restore import (
    init_session_state,
    get_backup_manager,
    render_create_backup,
    render_backup_list,
    render_settings,
    render_restore_confirm,
)
from tracking_app.pages.backup_restore.helpers import get_db_path


# Page configuration
st.set_page_config(
    page_title="Backup & Restore",
    page_icon="💾",
    layout="wide"
)


def main():
    """Main backup and restore page."""
    # Initialize session state
    init_session_state()
    
    st.title("💾 Backup & Restore")
    st.markdown("Create, manage, and restore database backups with SHA-256 verification.")
    
    # Get backup manager
    manager = get_backup_manager()
    
    if manager is None:
        st.error("Backup system is not available. Please ensure the brain module is installed.")
        st.stop()
    
    # Tabs for different operations
    tab1, tab2, tab3 = st.tabs(["📦 Create Backup", "📋 Backup List", "⚙️ Settings"])
    
    with tab1:
        render_create_backup(manager)
    
    with tab2:
        render_backup_list(manager)
    
    with tab3:
        render_settings(manager)
    
    # Restore confirmation dialog
    render_restore_confirm(get_db_path())


if __name__ == "__main__":
    main()