"""
UI components for the Data Lifecycle page.

Contains all render functions for the lifecycle interface.
"""

import streamlit as st
from pathlib import Path

from .constants import (
    RESET_TYPES,
    RESET_MODULES,
    DEFAULT_CREATE_BACKUP,
    DEFAULT_RESET_MODULES,
    RECOVERY_DISPLAY_LIMIT,
    DEFAULT_USER_ID,
)
from .helpers import (
    format_duration,
    apply_retention_policies,
    recover_entity,
    export_user_data,
    export_portable_data,
    request_erasure,
)


def render_retention_policies(manager) -> None:
    """
    Render the retention policies tab.
    
    Args:
        manager: LifecycleManager instance
    """
    st.subheader("Retention Policies")
    st.markdown("Configure how long data is kept before archiving or deletion.")
    
    # Get all policies
    policies = manager.retention.get_all_policies()
    
    for policy in policies:
        with st.expander(f"📦 {policy.entity_type.title()}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Archive After", format_duration(policy.archive_after_days))
            
            with col2:
                if policy.delete_after_days:
                    st.metric("Delete After", format_duration(policy.delete_after_days))
                else:
                    st.metric("Delete After", "Never")
            
            with col3:
                status = "✓ Active" if policy.enabled else "✗ Disabled"
                st.metric("Status", status)
            
            if policy.cascade_to:
                st.write(f"**Cascade to:** {', '.join(policy.cascade_to)}")
    
    st.markdown("---")
    st.subheader("Apply Policies")
    
    if st.button("🔄 Run Retention Enforcement", type="primary"):
        with st.spinner("Applying retention policies..."):
            result = apply_retention_policies(manager)
            
            if result and result.success:
                st.success("✓ Retention policies applied!")
                col_a, col_b = st.columns(2)
                col_a.metric("Records Archived", result.records_archived)
                col_b.metric("Records Purged", result.records_purged)
            elif result:
                st.error(f"Failed: {result.error_message}")
            else:
                st.error("Failed to apply retention policies")
    
    # Recoverable records
    st.markdown("---")
    st.subheader("Recoverable Records")
    
    recoverable = manager.count_recoverable()
    if recoverable > 0:
        st.info(f"📋 {recoverable} records are in the recovery window and can be restored.")
        
        deleted_records = manager.list_deleted_records()
        
        for record in deleted_records[:RECOVERY_DISPLAY_LIMIT]:
            with st.expander(f"🗑️ {record.entity_type}/{record.entity_id}"):
                st.write(f"**Deleted:** {record.deleted_at.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Recoverable until:** {record.recovery_until.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Reason:** {record.deletion_reason}")
                
                if st.button("↩️ Recover", key=f"recover_{record.id}"):
                    result = recover_entity(manager, record.entity_type, record.entity_id)
                    if result and result.success:
                        st.success("✓ Record recovered!")
                    elif result:
                        st.error(f"Failed: {result.error_message}")
                    else:
                        st.error("Failed to recover record")
    else:
        st.info("No recoverable records at this time.")


def render_gdpr_compliance(db_path: str) -> None:
    """
    Render the GDPR compliance tab.
    
    Args:
        db_path: Path to the database
    """
    st.subheader("GDPR Compliance")
    st.markdown("Exercise your rights under GDPR (General Data Protection Regulation).")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Right to Access (Article 15)")
        st.write("Export all data associated with your account.")
        
        if st.button("📥 Export My Data"):
            with st.spinner("Exporting your data..."):
                try:
                    from brain.lifecycle import GDPRCompliance
                    gdpr = GDPRCompliance(db_path=str(db_path))
                    data = export_user_data(gdpr, DEFAULT_USER_ID)
                    
                    if data:
                        st.success("✓ Data exported!")
                        st.json({
                            'tables': list(data.get('data', {}).keys()),
                            'summary': data.get('summary', {})
                        })
                    else:
                        st.error("Failed to export data")
                except ImportError:
                    st.error("GDPR module not available")
    
    with col2:
        st.markdown("#### Right to Portability (Article 20)")
        st.write("Get your data in a machine-readable format.")
        
        if st.button("📦 Export Portable"):
            with st.spinner("Creating portable export..."):
                try:
                    from brain.lifecycle import GDPRCompliance
                    gdpr = GDPRCompliance(db_path=str(db_path))
                    export_path = export_portable_data(gdpr, DEFAULT_USER_ID)
                    
                    if export_path:
                        st.success(f"✓ Export created: `{Path(export_path).name}`")
                    else:
                        st.error("Failed to create portable export")
                except ImportError:
                    st.error("GDPR module not available")
    
    st.markdown("---")
    
    # Right to Erasure
    st.markdown("#### Right to Erasure (Article 17)")
    st.warning("⚠️ This will permanently delete all your data after a 30-day grace period.")
    
    if st.button("🔴 Request Data Erasure", type="secondary"):
        st.session_state.show_erasure_confirm = True
    
    if st.session_state.show_erasure_confirm:
        st.error("⚠️ **WARNING:** This action cannot be easily undone!")
        st.write("Your data will be deleted after a 30-day grace period.")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("✓ Yes, Request Erasure"):
                try:
                    from brain.lifecycle import GDPRCompliance
                    gdpr = GDPRCompliance(db_path=str(db_path))
                    request = request_erasure(gdpr, DEFAULT_USER_ID)
                    
                    if request:
                        st.success(f"✓ Erasure request created (ID: {request.id[:8]}...)")
                        st.info("Check your email for verification.")
                        st.session_state.show_erasure_confirm = False
                    else:
                        st.error("Failed to create erasure request")
                except ImportError:
                    st.error("GDPR module not available")
        
        with col_b:
            if st.button("✗ Cancel"):
                st.session_state.show_erasure_confirm = False
                st.rerun()


def render_data_reset() -> None:
    """Render the data reset tab."""
    st.subheader("Data Reset")
    st.warning("⚠️ These actions are destructive. Create a backup first!")
    
    reset_type = st.radio(
        "Reset Type",
        options=RESET_TYPES,
        help="Choose what to reset"
    )
    
    modules = []
    if "Module" in reset_type:
        modules = st.multiselect(
            "Select Modules",
            options=RESET_MODULES,
            default=DEFAULT_RESET_MODULES
        )
    
    create_backup = st.checkbox("Create backup before reset", value=DEFAULT_CREATE_BACKUP)
    
    if st.button("🗑️ Reset Data", type="primary"):
        st.session_state.show_reset_confirm = True
    
    if st.session_state.show_reset_confirm:
        st.error("⚠️ **FINAL WARNING:** This will permanently delete data!")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("✓ Yes, Reset", type="primary"):
                st.info("Reset functionality would execute here.")
                st.session_state.show_reset_confirm = False
        
        with col_b:
            if st.button("✗ Cancel"):
                st.session_state.show_reset_confirm = False
                st.rerun()