"""
Data Lifecycle UI Page

Streamlit interface for managing data retention and lifecycle.
Supports retention policies, GDPR compliance, and data reset.

Phase 5.4 - Data Lifecycle Management
"""

import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from brain.lifecycle import (
    LifecycleManager,
    RetentionPolicy,
    GDPRCompliance,
    ErasureStatus,
)


def init_session_state():
    """Initialize session state variables."""
    if 'show_reset_confirm' not in st.session_state:
        st.session_state.show_reset_confirm = False
    if 'show_erasure_confirm' not in st.session_state:
        st.session_state.show_erasure_confirm = False


def format_duration(days):
    """Format days into human readable duration."""
    if days >= 365:
        years = days // 365
        return f"{years} year{'s' if years > 1 else ''}"
    elif days >= 30:
        months = days // 30
        return f"{months} month{'s' if months > 1 else ''}"
    else:
        return f"{days} days"


def main():
    st.set_page_config(
        page_title="Data Lifecycle",
        page_icon="🔄",
        layout="wide"
    )
    
    init_session_state()
    
    st.title("🔄 Data Lifecycle Management")
    st.markdown("Manage data retention, GDPR compliance, and data reset options.")
    
    # Get database path
    db_path = Path(__file__).parent.parent.parent / 'tracking.db'
    
    # Create manager
    manager = LifecycleManager(db_path=str(db_path))
    
    # Tabs for different operations
    tab1, tab2, tab3 = st.tabs(["📋 Retention Policies", "🛡️ GDPR Compliance", "⚠️ Data Reset"])
    
    with tab1:
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
                result = manager.apply_retention_policies()
                
                if result.success:
                    st.success("✓ Retention policies applied!")
                    col_a, col_b = st.columns(2)
                    col_a.metric("Records Archived", result.records_archived)
                    col_b.metric("Records Purged", result.records_purged)
                else:
                    st.error(f"Failed: {result.error_message}")
        
        # Recoverable records
        st.markdown("---")
        st.subheader("Recoverable Records")
        
        recoverable = manager.count_recoverable()
        if recoverable > 0:
            st.info(f"📋 {recoverable} records are in the recovery window and can be restored.")
            
            deleted_records = manager.list_deleted_records()
            
            for record in deleted_records[:10]:
                with st.expander(f"🗑️ {record.entity_type}/{record.entity_id}"):
                    st.write(f"**Deleted:** {record.deleted_at.strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**Recoverable until:** {record.recovery_until.strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**Reason:** {record.deletion_reason}")
                    
                    if st.button("↩️ Recover", key=f"recover_{record.id}"):
                        result = manager.recover_entity(record.entity_type, record.entity_id)
                        if result.success:
                            st.success("✓ Record recovered!")
                        else:
                            st.error(f"Failed: {result.error_message}")
        else:
            st.info("No recoverable records at this time.")
    
    with tab2:
        st.subheader("GDPR Compliance")
        st.markdown("Exercise your rights under GDPR (General Data Protection Regulation).")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Right to Access (Article 15)")
            st.write("Export all data associated with your account.")
            
            if st.button("📥 Export My Data"):
                with st.spinner("Exporting your data..."):
                    gdpr = GDPRCompliance(db_path=str(db_path))
                    data = gdpr.export_user_data('default')
                    
                    st.success("✓ Data exported!")
                    st.json({
                        'tables': list(data.get('data', {}).keys()),
                        'summary': data.get('summary', {})
                    })
        
        with col2:
            st.markdown("#### Right to Portability (Article 20)")
            st.write("Get your data in a machine-readable format.")
            
            if st.button("📦 Export Portable"):
                with st.spinner("Creating portable export..."):
                    gdpr = GDPRCompliance(db_path=str(db_path))
                    export_dir = Path(__file__).parent.parent.parent / 'exports'
                    export_path = gdpr.export_portable_data('default')
                    
                    st.success(f"✓ Export created: `{export_path.name}`")
        
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
                    gdpr = GDPRCompliance(db_path=str(db_path))
                    request = gdpr.request_erasure('default')
                    st.success(f"✓ Erasure request created (ID: {request.id[:8]}...)")
                    st.info("Check your email for verification.")
                    st.session_state.show_erasure_confirm = False
            
            with col_b:
                if st.button("✗ Cancel"):
                    st.session_state.show_erasure_confirm = False
                    st.rerun()
    
    with tab3:
        st.subheader("Data Reset")
        st.warning("⚠️ These actions are destructive. Create a backup first!")
        
        reset_type = st.radio(
            "Reset Type",
            options=[
                "Module Reset (specific modules)",
                "Archive Reset (clear archived data)",
                "Full Reset (all data)"
            ],
            help="Choose what to reset"
        )
        
        if "Module" in reset_type:
            modules = st.multiselect(
                "Select Modules",
                options=['habits', 'tasks', 'goals', 'finances', 'health', 'time'],
                default=['habits']
            )
        else:
            modules = []
        
        create_backup = st.checkbox("Create backup before reset", value=True)
        
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
    
    # Cleanup
    manager.close()


if __name__ == "__main__":
    main()