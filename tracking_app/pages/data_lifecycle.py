"""
Data Lifecycle UI Page

Streamlit interface for managing data retention and lifecycle.
Supports retention policies, GDPR compliance, and data reset.

Phase 5.4 - Data Lifecycle Management
"""

import streamlit as st
from pathlib import Path

from tracking_app.pages.data_lifecycle import (
    init_session_state,
    get_lifecycle_manager,
    render_retention_policies,
    render_gdpr_compliance,
    render_data_reset,
)
from tracking_app.pages.data_lifecycle.constants import DEFAULT_DB_NAME


# Page configuration
st.set_page_config(
    page_title="Data Lifecycle",
    page_icon="🔄",
    layout="wide"
)


def main():
    """Main data lifecycle page."""
    # Initialize session state
    init_session_state()
    
    st.title("🔄 Data Lifecycle Management")
    st.markdown("Manage data retention, GDPR compliance, and data reset options.")
    
    # Get database path
    db_path = Path(__file__).parent.parent / DEFAULT_DB_NAME
    
    # Create manager
    manager = get_lifecycle_manager()
    
    if manager is None:
        st.error("Lifecycle management is not available. Please ensure the brain module is installed.")
        st.stop()
    
    # Tabs for different operations
    tab1, tab2, tab3 = st.tabs(["📋 Retention Policies", "🛡️ GDPR Compliance", "⚠️ Data Reset"])
    
    with tab1:
        render_retention_policies(manager)
    
    with tab2:
        render_gdpr_compliance(db_path)
    
    with tab3:
        render_data_reset()
    
    # Cleanup
    manager.close()


if __name__ == "__main__":
    main()