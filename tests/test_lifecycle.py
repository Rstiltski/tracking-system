"""
Tests for Data Lifecycle Management Module

Tests cover:
- Retention policies
- Soft delete and recovery
- Purge operations
- GDPR compliance

Run with: pytest tests/test_lifecycle.py -v
"""

import pytest
import tempfile
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import json
import shutil


# Import the lifecycle module
import sys
sys.path.insert(0, '.')

from brain.lifecycle import (
    LifecycleManager,
    RetentionEngine,
    ArchiveManager,
    PurgeManager,
    RecoveryManager,
    GDPRCompliance,
    RetentionPolicy,
    DeletedRecord,
    ErasureRequest,
    ErasureStatus,
    PurgeStatus,
    ResetType,
    RetentionAction,
    LifecycleResult,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    db_path = temp_dir / 'test_lifecycle.db'
    
    # Create database with test tables
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create test tables
    cursor.execute('''
        CREATE TABLE habits (
            id TEXT PRIMARY KEY,
            name TEXT,
            user_id TEXT,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE tasks (
            id TEXT PRIMARY KEY,
            title TEXT,
            user_id TEXT,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE habit_logs (
            id TEXT PRIMARY KEY,
            habit_id TEXT,
            user_id TEXT,
            created_at TEXT
        )
    ''')
    
    # Insert test data
    old_date = (datetime.now() - timedelta(days=400)).isoformat()
    recent_date = datetime.now().isoformat()
    
    cursor.execute(
        "INSERT INTO habits (id, name, user_id, created_at) VALUES (?, ?, ?, ?)",
        ('habit-1', 'Test Habit', 'user-1', old_date)
    )
    
    cursor.execute(
        "INSERT INTO tasks (id, title, user_id, created_at) VALUES (?, ?, ?, ?)",
        ('task-1', 'Old Task', 'user-1', old_date)
    )
    
    cursor.execute(
        "INSERT INTO tasks (id, title, user_id, created_at) VALUES (?, ?, ?, ?)",
        ('task-2', 'Recent Task', 'user-1', recent_date)
    )
    
    conn.commit()
    
    yield str(db_path)
    
    # Cleanup
    conn.close()
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_export_dir():
    """Create a temporary export directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield str(temp_dir)
    shutil.rmtree(temp_dir)


class TestRetentionEngine:
    """Tests for RetentionEngine."""
    
    def test_default_policies_loaded(self):
        """Test that default policies are loaded."""
        engine = RetentionEngine()
        policies = engine.get_all_policies()
        
        assert len(policies) > 0
        
        # Check habits policy (never delete)
        habits_policy = engine.get_policy('habits')
        assert habits_policy is not None
    
    def test_evaluate_keep_record(self):
        """Test that recent records are kept."""
        engine = RetentionEngine()
        
        record = {
            'id': 'test-1',
            'created_at': datetime.now() - timedelta(days=30)
        }
        
        action = engine.evaluate('tasks', record)
        assert action == RetentionAction.KEEP
    
    def test_evaluate_archive_record(self):
        """Test that old records should be archived."""
        engine = RetentionEngine()
        
        record = {
            'id': 'test-1',
            'created_at': datetime.now() - timedelta(days=120)
        }
        
        action = engine.evaluate('tasks', record)
        assert action == RetentionAction.ARCHIVE
    
    def test_habits_never_delete(self):
        """Test that habits are never marked for deletion."""
        engine = RetentionEngine()
        
        record = {
            'id': 'habit-1',
            'created_at': datetime.now() - timedelta(days=1000)
        }
        
        action = engine.evaluate('habits', record)
        assert action == RetentionAction.KEEP


class TestArchiveManager:
    """Tests for ArchiveManager."""
    
    def test_archive_record(self, temp_db):
        """Test archiving a record."""
        conn = sqlite3.connect(temp_db)
        
        # Create lifecycle tables first
        manager = LifecycleManager(db_connection=conn)
        
        archive = ArchiveManager(conn, recovery_days=30)
        
        # Archive a task
        deleted = archive.archive('tasks', 'task-1', reason='test')
        
        assert deleted.entity_type == 'tasks'
        assert deleted.entity_id == 'task-1'
        assert deleted.purge_status == PurgeStatus.RECOVERABLE
        assert deleted.is_recoverable()
        
        conn.close()
    
    def test_list_deleted_records(self, temp_db):
        """Test listing deleted records."""
        conn = sqlite3.connect(temp_db)
        manager = LifecycleManager(db_connection=conn)
        archive = ArchiveManager(conn)
        
        # Archive a task
        archive.archive('tasks', 'task-1', reason='test')
        
        # List deleted
        deleted = archive.list_deleted(recoverable_only=True)
        
        assert len(deleted) == 1
        assert deleted[0].entity_id == 'task-1'
        
        conn.close()
    
    def test_count_recoverable(self, temp_db):
        """Test counting recoverable records."""
        conn = sqlite3.connect(temp_db)
        manager = LifecycleManager(db_connection=conn)
        archive = ArchiveManager(conn)
        
        # Archive two tasks
        archive.archive('tasks', 'task-1', reason='test')
        
        count = archive.count_recoverable()
        assert count == 1
        
        conn.close()


class TestRecoveryManager:
    """Tests for RecoveryManager."""
    
    def test_can_recover(self, temp_db):
        """Test checking if record can be recovered."""
        conn = sqlite3.connect(temp_db)
        manager = LifecycleManager(db_connection=conn)
        archive = ArchiveManager(conn)
        recovery = RecoveryManager(conn)
        
        # Archive a task
        archive.archive('tasks', 'task-1')
        
        # Check if recoverable
        assert recovery.can_recover('tasks', 'task-1')
        
        conn.close()
    
    def test_recover_record(self, temp_db):
        """Test recovering a deleted record."""
        conn = sqlite3.connect(temp_db)
        manager = LifecycleManager(db_connection=conn)
        archive = ArchiveManager(conn)
        recovery = RecoveryManager(conn)
        
        # Archive a task
        archive.archive('tasks', 'task-1')
        
        # Recover it
        result = recovery.recover('tasks', 'task-1')
        
        assert result.success
        assert result.records_recovered == 1
        
        # Verify it's no longer in deleted records
        assert not recovery.can_recover('tasks', 'task-1')
        
        conn.close()


class TestPurgeManager:
    """Tests for PurgeManager."""
    
    def test_purge_expired(self, temp_db):
        """Test purging expired records."""
        conn = sqlite3.connect(temp_db)
        manager = LifecycleManager(db_connection=conn)
        archive = ArchiveManager(conn, recovery_days=0)  # Immediate expiry
        purge = PurgeManager(conn)
        
        # Archive a task with immediate expiry
        deleted = archive.archive('tasks', 'task-1')
        
        # Manually set recovery_until to past
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE deleted_records SET recovery_until = ? WHERE id = ?",
            ((datetime.now() - timedelta(days=1)).isoformat(), deleted.id)
        )
        conn.commit()
        
        # Purge expired
        count = purge.purge_expired()
        
        assert count == 1
        
        conn.close()


class TestLifecycleManager:
    """Tests for LifecycleManager."""
    
    def test_initialization(self, temp_db):
        """Test manager initialization."""
        manager = LifecycleManager(db_path=temp_db)
        
        assert manager.db is not None
        assert manager.retention is not None
        assert manager.archive is not None
        assert manager.purge is not None
        assert manager.recovery is not None
        
        manager.close()
    
    def test_archive_entity(self, temp_db):
        """Test archiving through manager."""
        manager = LifecycleManager(db_path=temp_db)
        
        deleted = manager.archive_entity('tasks', 'task-1', reason='test')
        
        assert deleted.entity_id == 'task-1'
        assert deleted.is_recoverable()
        
        manager.close()
    
    def test_recover_entity(self, temp_db):
        """Test recovery through manager."""
        manager = LifecycleManager(db_path=temp_db)
        
        # Archive then recover
        manager.archive_entity('tasks', 'task-1')
        result = manager.recover_entity('tasks', 'task-1')
        
        assert result.success
        assert result.records_recovered == 1
        
        manager.close()
    
    def test_count_recoverable(self, temp_db):
        """Test counting recoverable records."""
        manager = LifecycleManager(db_path=temp_db)
        
        # Archive a task
        manager.archive_entity('tasks', 'task-1')
        
        count = manager.count_recoverable()
        assert count == 1
        
        manager.close()


class TestGDPRCompliance:
    """Tests for GDPR compliance."""
    
    def test_export_user_data(self, temp_db, temp_export_dir):
        """Test exporting user data."""
        conn = sqlite3.connect(temp_db)
        manager = LifecycleManager(db_connection=conn)
        gdpr = GDPRCompliance(conn, export_dir=temp_export_dir)
        
        data = gdpr.export_user_data('user-1')
        
        assert 'user_id' in data
        assert data['user_id'] == 'user-1'
        assert 'data' in data
        assert 'summary' in data
        
        conn.close()
    
    def test_request_erasure(self, temp_db, temp_export_dir):
        """Test requesting erasure."""
        conn = sqlite3.connect(temp_db)
        manager = LifecycleManager(db_connection=conn)
        gdpr = GDPRCompliance(conn, export_dir=temp_export_dir)
        
        request = gdpr.request_erasure('user-1')
        
        assert request.user_id == 'user-1'
        assert request.status == ErasureStatus.PENDING
        assert request.verification_token is not None
        
        conn.close()
    
    def test_cancel_erasure_request(self, temp_db, temp_export_dir):
        """Test cancelling an erasure request."""
        conn = sqlite3.connect(temp_db)
        manager = LifecycleManager(db_connection=conn)
        gdpr = GDPRCompliance(conn, export_dir=temp_export_dir)
        
        # Create and cancel request
        request = gdpr.request_erasure('user-1')
        cancelled = gdpr.cancel_erasure_request(request.id, reason='Changed mind')
        
        assert cancelled
        
        # Verify status
        retrieved = gdpr.get_erasure_request(request.id)
        assert retrieved.status == ErasureStatus.CANCELLED
        
        conn.close()


class TestModels:
    """Tests for data models."""
    
    def test_retention_policy_to_dict(self):
        """Test RetentionPolicy serialization."""
        policy = RetentionPolicy(
            entity_type='tasks',
            archive_after_days=90,
            delete_after_days=365
        )
        
        data = policy.to_dict()
        
        assert data['entity_type'] == 'tasks'
        assert data['archive_after_days'] == 90
        assert data['delete_after_days'] == 365
    
    def test_retention_policy_from_dict(self):
        """Test RetentionPolicy deserialization."""
        data = {
            'id': 'test-id',
            'entity_type': 'tasks',
            'archive_after_days': 90,
            'delete_after_days': 365,
            'enabled': 1,
            'cascade_to': '',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        policy = RetentionPolicy.from_dict(data)
        
        assert policy.entity_type == 'tasks'
        assert policy.archive_after_days == 90
    
    def test_deleted_record_is_recoverable(self):
        """Test DeletedRecord recoverable check."""
        # Recoverable record
        record = DeletedRecord(
            entity_type='tasks',
            entity_id='task-1',
            recovery_until=datetime.now() + timedelta(days=30)
        )
        assert record.is_recoverable()
        
        # Expired record
        record.recovery_until = datetime.now() - timedelta(days=1)
        assert not record.is_recoverable()
    
    def test_erasure_request_can_execute(self):
        """Test ErasureRequest execution check."""
        # Cannot execute pending request
        request = ErasureRequest(status=ErasureStatus.PENDING)
        assert not request.can_execute()
        
        # Can execute approved request
        request.status = ErasureStatus.APPROVED
        assert request.can_execute()


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])