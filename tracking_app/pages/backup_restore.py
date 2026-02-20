"""
Backup & Restore UI Page

Streamlit interface for managing database backups.
Supports full backups, restore, and verification.

Phase 5.3 - Backup & Restore System
"""

import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from brain.backup import (
    BackupManager,
    BackupType,
    BackupStatus,
    RestoreEngine,
    RetentionPolicy,
    BackupValidator,
)


def init_session_state():
    """Initialize session state variables."""
    if 'backup_in_progress' not in st.session_state:
        st.session_state.backup_in_progress = False
    if 'restore_in_progress' not in st.session_state:
        st.session_state.restore_in_progress = False
    if 'show_restore_confirm' not in st.session_state:
        st.session_state.show_restore_confirm = False
    if 'selected_backup' not in st.session_state:
        st.session_state.selected_backup = None


def format_size(size_bytes):
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def main():
    st.set_page_config(
        page_title="Backup & Restore",
        page_icon="💾",
        layout="wide"
    )
    
    init_session_state()
    
    st.title("💾 Backup & Restore")
    st.markdown("Create, manage, and restore database backups with SHA-256 verification.")
    
    # Get paths
    db_path = Path(__file__).parent.parent.parent / 'tracking.db'
    backup_dir = Path(__file__).parent.parent.parent / 'backups'
    
    # Create backup manager
    manager = BackupManager(str(db_path), str(backup_dir))
    
    # Tabs for different operations
    tab1, tab2, tab3 = st.tabs(["📦 Create Backup", "📋 Backup List", "⚙️ Settings"])
    
    with tab1:
        st.subheader("Create New Backup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            backup_type = st.selectbox(
                "Backup Type",
                options=["Full Backup", "Incremental"],
                index=0,
                help="Full: Complete database copy\nIncremental: Only changes since last backup"
            )
            
            add_verification = st.checkbox(
                "Verify after backup",
                value=True,
                help="Verify backup integrity with SHA-256 checksum"
            )
        
        with col2:
            st.info(f"""
            **Current Database:**
            - Path: `{db_path.name}`
            - Size: {format_size(db_path.stat().st_size) if db_path.exists() else 'N/A'}
            """)
        
        if st.button("🚀 Create Backup", type="primary", disabled=st.session_state.backup_in_progress):
            st.session_state.backup_in_progress = True
            
            with st.spinner("Creating backup..."):
                try:
                    job = manager.create_backup(user_id='default')
                    
                    if job.status == BackupStatus.COMPLETED:
                        st.success("✓ Backup created successfully!")
                        
                        col_a, col_b, col_c = st.columns(3)
                        col_a.metric("File Size", format_size(job.file_size_bytes))
                        col_b.metric("Records", job.record_count)
                        col_c.metric("Duration", f"{(job.completed_at - job.started_at).total_seconds():.1f}s")
                        
                        st.code(f"Checksum: {job.checksum[:32]}...", language=None)
                        st.code(f"Path: {job.file_path}", language=None)
                        
                        if add_verification:
                            verified = manager.verify_backup(job.id)
                            if verified:
                                st.success("✓ Backup verified successfully")
                            else:
                                st.warning("⚠ Backup verification failed")
                    else:
                        st.error(f"Backup failed: {job.error_message}")
                        
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    st.session_state.backup_in_progress = False
    
    with tab2:
        st.subheader("Available Backups")
        
        # Get backup list
        backups = manager.list_backups()
        
        if not backups:
            st.info("No backups found. Create your first backup!")
        else:
            for backup in backups:
                with st.expander(
                    f"📦 {backup.created_at.strftime('%Y-%m-%d %H:%M')} - {format_size(backup.file_size_bytes)}",
                    expanded=False
                ):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.write(f"**Type:** {backup.backup_type.value}")
                        st.write(f"**Status:** {backup.status.value}")
                        st.write(f"**Records:** {backup.record_count}")
                    
                    with col_b:
                        st.write(f"**Size:** {format_size(backup.file_size_bytes)}")
                        st.write(f"**Checksum:** `{backup.checksum[:16]}...`")
                        
                        if backup.verified_at:
                            st.write(f"**Verified:** {backup.verified_at.strftime('%Y-%m-%d %H:%M')}")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("✓ Verify", key=f"verify_{backup.id}"):
                            with st.spinner("Verifying..."):
                                if manager.verify_backup(backup.id):
                                    st.success("✓ Verified!")
                                else:
                                    st.error("Verification failed")
                    
                    with col2:
                        if st.button("📥 Restore", key=f"restore_{backup.id}"):
                            st.session_state.selected_backup = backup
                            st.session_state.show_restore_confirm = True
                    
                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_{backup.id}"):
                            Path(backup.file_path).unlink(missing_ok=True)
                            st.success("Backup deleted")
                            st.rerun()
    
    with tab3:
        st.subheader("Retention Policy")
        
        daily = st.number_input("Daily backups to keep", min_value=1, max_value=30, value=7)
        weekly = st.number_input("Weekly backups to keep", min_value=1, max_value=12, value=4)
        monthly = st.number_input("Monthly backups to keep", min_value=1, max_value=24, value=12)
        
        if st.button("Apply Retention Policy"):
            policy = RetentionPolicy(daily=daily, weekly=weekly, monthly=monthly)
            to_delete = policy.evaluate(backups)
            st.info(f"{len(to_delete)} backups would be removed")
        
        st.markdown("---")
        st.subheader("Schedule")
        st.info("Backups can be scheduled to run automatically. Configure in the scheduler settings.")
    
    # Restore confirmation dialog
    if st.session_state.show_restore_confirm and st.session_state.selected_backup:
        st.warning("⚠️ **Warning:** Restoring will overwrite your current database!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✓ Yes, Restore", type="primary"):
                backup = st.session_state.selected_backup
                
                with st.spinner("Restoring..."):
                    try:
                        engine = RestoreEngine(verify_checksum=True, create_safety_backup=True)
                        result = engine.restore(
                            backup_path=Path(backup.file_path),
                            target_path=db_path,
                            expected_checksum=backup.checksum
                        )
                        
                        if result.success:
                            st.success(f"✓ Restored! {result.records_restored} records")
                        else:
                            st.error(f"Restore failed: {result.error_message}")
                    except Exception as e:
                        st.error(f"Error: {e}")
                
                st.session_state.show_restore_confirm = False
                st.session_state.selected_backup = None
        
        with col2:
            if st.button("✗ Cancel"):
                st.session_state.show_restore_confirm = False
                st.session_state.selected_backup = None
                st.rerun()


if __name__ == "__main__":
    main()