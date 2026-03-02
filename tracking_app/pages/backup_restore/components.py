"""
UI components for the Backup & Restore page.

Contains all render functions for the backup interface.
"""

import streamlit as st
from pathlib import Path

from .constants import (
    DEFAULT_USER_ID,
    DEFAULT_DAILY_BACKUPS,
    DEFAULT_WEEKLY_BACKUPS,
    DEFAULT_MONTHLY_BACKUPS,
    MIN_DAILY_BACKUPS,
    MAX_DAILY_BACKUPS,
    MIN_WEEKLY_BACKUPS,
    MAX_WEEKLY_BACKUPS,
    MIN_MONTHLY_BACKUPS,
    MAX_MONTHLY_BACKUPS,
)
from .helpers import (
    format_size,
    get_backup_manager,
    get_db_path,
    get_restore_engine,
    get_retention_policy,
)


def render_create_backup(manager) -> None:
    """Render the create backup tab."""
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
        db_path = get_db_path()
        st.info(f"""
        **Current Database:**
        - Path: `{db_path.name}`
        - Size: {format_size(db_path.stat().st_size) if db_path.exists() else 'N/A'}
        """)
    
    if st.button("🚀 Create Backup", type="primary", disabled=st.session_state.backup_in_progress):
        st.session_state.backup_in_progress = True
        
        with st.spinner("Creating backup..."):
            try:
                from brain.backup import BackupStatus
                
                job = manager.create_backup(user_id=DEFAULT_USER_ID)
                
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
                    
            except ImportError:
                st.error("Backup system requires the brain module.")
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                st.session_state.backup_in_progress = False


def render_backup_list(manager) -> None:
    """Render the backup list tab."""
    st.subheader("Available Backups")
    
    # Get backup list
    backups = manager.list_backups()
    
    if not backups:
        st.info("No backups found. Create your first backup!")
        return
    
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


def render_settings(manager) -> None:
    """Render the settings tab."""
    st.subheader("Retention Policy")
    
    daily = st.number_input(
        "Daily backups to keep",
        min_value=MIN_DAILY_BACKUPS,
        max_value=MAX_DAILY_BACKUPS,
        value=DEFAULT_DAILY_BACKUPS
    )
    weekly = st.number_input(
        "Weekly backups to keep",
        min_value=MIN_WEEKLY_BACKUPS,
        max_value=MAX_WEEKLY_BACKUPS,
        value=DEFAULT_WEEKLY_BACKUPS
    )
    monthly = st.number_input(
        "Monthly backups to keep",
        min_value=MIN_MONTHLY_BACKUPS,
        max_value=MAX_MONTHLY_BACKUPS,
        value=DEFAULT_MONTHLY_BACKUPS
    )
    
    if st.button("Apply Retention Policy"):
        policy = get_retention_policy(daily, weekly, monthly)
        if policy:
            backups = manager.list_backups()
            to_delete = policy.evaluate(backups)
            st.info(f"{len(to_delete)} backups would be removed")
        else:
            st.error("Retention policy requires the brain module.")
    
    st.markdown("---")
    st.subheader("Schedule")
    st.info("Backups can be scheduled to run automatically. Configure in the scheduler settings.")


def render_restore_confirm(db_path: Path) -> None:
    """Render the restore confirmation dialog."""
    if not st.session_state.show_restore_confirm or not st.session_state.selected_backup:
        return
    
    st.warning("⚠️ **Warning:** Restoring will overwrite your current database!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✓ Yes, Restore", type="primary"):
            backup = st.session_state.selected_backup
            
            with st.spinner("Restoring..."):
                try:
                    engine = get_restore_engine()
                    if engine:
                        result = engine.restore(
                            backup_path=Path(backup.file_path),
                            target_path=db_path,
                            expected_checksum=backup.checksum
                        )
                        
                        if result.success:
                            st.success(f"✓ Restored! {result.records_restored} records")
                        else:
                            st.error(f"Restore failed: {result.error_message}")
                    else:
                        st.error("Restore requires the brain module.")
                except Exception as e:
                    st.error(f"Error: {e}")
            
            st.session_state.show_restore_confirm = False
            st.session_state.selected_backup = None
    
    with col2:
        if st.button("✗ Cancel"):
            st.session_state.show_restore_confirm = False
            st.session_state.selected_backup = None
            st.rerun()