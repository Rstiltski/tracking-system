"""
Tests for Backup System

Comprehensive test suite for the backup and restore functionality.
Tests cover all major components:
- BackupManager
- BackupVerifier
- DeduplicationEngine
- RetentionPolicy
- RestoreEngine
- BackupValidator
"""

import pytest
import tempfile
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import json
import os

# Import backup system components
from brain.backup import (
    BackupManager,
    BackupVerifier,
    TieredVerifier,
    ManifestManager,
    DeduplicationEngine,
    NoOpDedupEngine,
    DedupDatabase,
    RetentionPolicy,
    RetentionManager,
    RestoreEngine,
    RestorePlanner,
    BackupValidator,
    BackupHealthChecker,
    ScheduleBuilder,
    BackupJob,
    BackupSchedule,
    BackupType,
    BackupStatus,
    BackupFrequency,
    BackupManifest,
    DedupRecord,
)


# ============ Fixtures ============

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    dir_path = Path(tempfile.mkdtemp())
    yield dir_path
    shutil.rmtree(dir_path, ignore_errors=True)


@pytest.fixture
def temp_db(temp_dir):
    """Create a temporary test database."""
    db_path = temp_dir / "test_tracking.db"
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create test tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert test data
    cursor.execute("INSERT INTO habits (name) VALUES ('Test Habit 1')")
    cursor.execute("INSERT INTO habits (name) VALUES ('Test Habit 2')")
    cursor.execute("INSERT INTO habit_logs (habit_id) VALUES (1)")
    cursor.execute("INSERT INTO habit_logs (habit_id) VALUES (1)")
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def backup_manager(temp_dir, temp_db):
    """Create a BackupManager instance for testing."""
    backup_dir = temp_dir / "backups"
    manager = BackupManager(
        db_path=str(temp_db),
        backup_dir=str(backup_dir)
    )
    yield manager


# ============ BackupVerifier Tests ============

class TestBackupVerifier:
    """Tests for BackupVerifier class."""
    
    def test_generate_checksum(self, temp_dir):
        """Test SHA-256 checksum generation."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!")
        
        verifier = BackupVerifier()
        checksum = verifier.generate_checksum(test_file)
        
        # SHA-256 produces 64 hex characters
        assert len(checksum) == 64
        assert isinstance(checksum, str)
    
    def test_verify_matching_checksum(self, temp_dir):
        """Test verification with matching checksum."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!")
        
        verifier = BackupVerifier()
        checksum = verifier.generate_checksum(test_file)
        
        assert verifier.verify(test_file, checksum) is True
    
    def test_verify_mismatched_checksum(self, temp_dir):
        """Test verification with mismatched checksum."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!")
        
        verifier = BackupVerifier()
        fake_checksum = "0" * 64  # Invalid checksum
        
        assert verifier.verify(test_file, fake_checksum) is False
    
    def test_verify_nonexistent_file(self, temp_dir):
        """Test verification with nonexistent file."""
        verifier = BackupVerifier()
        nonexistent = temp_dir / "nonexistent.txt"
        
        assert verifier.verify(nonexistent, "0" * 64) is False
    
    def test_verify_size_match(self, temp_dir):
        """Test size verification."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!")
        
        verifier = BackupVerifier()
        file_size = test_file.stat().st_size
        
        assert verifier.verify_size_match(test_file, file_size) is True
        assert verifier.verify_size_match(test_file, file_size + 1) is False


class TestTieredVerifier:
    """Tests for TieredVerifier class."""
    
    def test_tiered_verification(self, temp_dir):
        """Test tiered verification process."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!")
        
        verifier = TieredVerifier()
        checksum = verifier.hash_verifier.generate_checksum(test_file)
        file_size = test_file.stat().st_size
        
        result, tier = verifier.verify_tiered(
            test_file,
            expected_size=file_size,
            expected_checksum=checksum
        )
        
        assert result is True
        assert tier in ["tier2_mtime", "tier3_checksum"]


# ============ BackupManager Tests ============

class TestBackupManager:
    """Tests for BackupManager class."""
    
    def test_create_backup(self, backup_manager):
        """Test backup creation."""
        job = backup_manager.create_backup(user_id="test-user")
        
        assert job.status == BackupStatus.COMPLETED
        assert job.file_path is not None
        assert job.checksum is not None
        assert len(job.checksum) == 64
        assert job.record_count > 0
        assert Path(job.file_path).exists()
    
    def test_get_backup(self, backup_manager):
        """Test retrieving a backup by ID."""
        created_job = backup_manager.create_backup()
        retrieved_job = backup_manager.get_backup(created_job.id)
        
        assert retrieved_job is not None
        assert retrieved_job.id == created_job.id
        assert retrieved_job.checksum == created_job.checksum
    
    def test_list_backups(self, backup_manager):
        """Test listing backups."""
        # Create multiple backups
        backup_manager.create_backup()
        backup_manager.create_backup()
        backup_manager.create_backup()
        
        backups = backup_manager.list_backups()
        
        assert len(backups) >= 3
    
    def test_delete_backup(self, backup_manager):
        """Test backup deletion."""
        job = backup_manager.create_backup()
        backup_path = Path(job.file_path)
        
        assert backup_path.exists()
        
        result = backup_manager.delete_backup(job.id)
        
        assert result is True
        assert not backup_path.exists()
    
    def test_verify_backup(self, backup_manager):
        """Test backup verification."""
        job = backup_manager.create_backup()
        
        result = backup_manager.verify_backup(job.id)
        
        assert result is True
    
    def test_get_statistics(self, backup_manager):
        """Test getting backup statistics."""
        backup_manager.create_backup()
        backup_manager.create_backup()
        
        stats = backup_manager.get_statistics()
        
        assert stats.total_backups >= 2
        assert stats.successful_backups >= 2
        assert stats.total_size_bytes > 0


# ============ Deduplication Tests ============

class TestDedupDatabase:
    """Tests for DedupDatabase class."""
    
    def test_record_file(self, temp_dir):
        """Test recording a file in dedup database."""
        db_path = temp_dir / "dedup.db"
        db = DedupDatabase(str(db_path))
        
        db.record_file(
            file_hash="abc123",
            original_path="/backups/test.db",
            original_size=1024
        )
        
        record = db.find_by_hash("abc123")
        
        assert record is not None
        assert record.file_hash == "abc123"
        assert record.original_path == "/backups/test.db"
        assert record.original_size == 1024
    
    def test_find_by_size(self, temp_dir):
        """Test finding files by size."""
        db_path = temp_dir / "dedup.db"
        db = DedupDatabase(str(db_path))
        
        db.record_file("hash1", "/path1", 1024)
        db.record_file("hash2", "/path2", 1024)
        db.record_file("hash3", "/path3", 2048)
        
        records = db.find_by_size(1024)
        
        assert len(records) == 2
    
    def test_increment_link_count(self, temp_dir):
        """Test incrementing link count."""
        db_path = temp_dir / "dedup.db"
        db = DedupDatabase(str(db_path))
        
        db.record_file("hash1", "/path1", 1024)
        
        new_count = db.increment_link_count("hash1")
        
        assert new_count == 2
    
    def test_get_statistics(self, temp_dir):
        """Test getting dedup statistics."""
        db_path = temp_dir / "dedup.db"
        db = DedupDatabase(str(db_path))
        
        db.record_file("hash1", "/path1", 1024)
        db.increment_link_count("hash1")
        db.increment_link_count("hash1")
        
        stats = db.get_statistics()
        
        assert stats["total_files"] == 1
        assert stats["total_links"] == 3


class TestDeduplicationEngine:
    """Tests for DeduplicationEngine class."""
    
    def test_process_file_creates_copy(self, temp_dir):
        """Test that processing creates a copy for new files."""
        source = temp_dir / "source.txt"
        source.write_text("Test content")
        
        dest = temp_dir / "dest.txt"
        
        engine = DeduplicationEngine(
            db_path=str(temp_dir / "dedup.db"),
            backup_dir=str(temp_dir)
        )
        
        result = engine.process_file(source, dest)
        
        assert result.is_link is False
        assert dest.exists()
        assert dest.read_text() == "Test content"
    
    def test_noop_engine(self, temp_dir):
        """Test NoOpDedupEngine always copies."""
        source = temp_dir / "source.txt"
        source.write_text("Test content")
        
        dest = temp_dir / "dest.txt"
        
        engine = NoOpDedupEngine()
        result = engine.process_file(source, dest)
        
        assert result.is_link is False
        assert dest.exists()


# ============ Retention Tests ============

class TestRetentionPolicy:
    """Tests for RetentionPolicy class."""
    
    def test_evaluate_empty_list(self):
        """Test evaluation with no backups."""
        policy = RetentionPolicy()
        to_delete = policy.evaluate([])
        
        assert to_delete == []
    
    def test_evaluate_keeps_recent_backups(self):
        """Test that recent backups are kept."""
        policy = RetentionPolicy(daily=7, weekly=4, monthly=12)
        
        # Create recent backups
        now = datetime.now()
        backups = []
        
        for i in range(3):
            job = BackupJob(
                status=BackupStatus.COMPLETED,
                completed_at=now - timedelta(days=i)
            )
            backups.append(job)
        
        to_delete = policy.evaluate(backups)
        
        # All recent backups should be kept
        assert len(to_delete) == 0
    
    def test_get_summary(self):
        """Test getting retention summary."""
        policy = RetentionPolicy()
        
        backups = [
            BackupJob(status=BackupStatus.COMPLETED, completed_at=datetime.now())
        ]
        
        summary = policy.get_summary(backups)
        
        assert "total_backups" in summary
        assert "retention_policy" in summary


# ============ Restore Tests ============

class TestRestoreEngine:
    """Tests for RestoreEngine class."""
    
    def test_restore_success(self, temp_dir, temp_db, backup_manager):
        """Test successful restore."""
        # Create a backup
        job = backup_manager.create_backup()
        backup_path = Path(job.file_path)
        
        # Create a restore target
        restore_path = temp_dir / "restored.db"
        
        # Restore
        engine = RestoreEngine(verify_checksum=True, create_safety_backup=False)
        result = engine.restore(
            backup_path=backup_path,
            target_path=restore_path,
            expected_checksum=job.checksum
        )
        
        assert result.success is True
        assert result.records_restored > 0
        assert restore_path.exists()
    
    def test_restore_with_safety_backup(self, temp_dir, temp_db, backup_manager):
        """Test restore creates safety backup."""
        # Create a backup
        job = backup_manager.create_backup()
        backup_path = Path(job.file_path)
        
        # Create a target that already exists
        restore_path = temp_dir / "restored.db"
        restore_path.write_text("existing data")
        
        # Restore with safety backup
        engine = RestoreEngine(verify_checksum=True, create_safety_backup=True)
        result = engine.restore(
            backup_path=backup_path,
            target_path=restore_path,
            expected_checksum=job.checksum
        )
        
        assert result.success is True
    
    def test_restore_missing_file(self, temp_dir):
        """Test restore with missing backup file."""
        engine = RestoreEngine()
        result = engine.restore(
            backup_path=temp_dir / "nonexistent.db",
            target_path=temp_dir / "target.db"
        )
        
        assert result.success is False
        assert "not found" in result.error_message.lower()


class TestRestorePlanner:
    """Tests for RestorePlanner class."""
    
    def test_create_plan_full_backup(self, backup_manager):
        """Test restore plan for full backup."""
        job = backup_manager.create_backup(backup_type=BackupType.FULL)
        
        planner = RestorePlanner()
        plan = planner.create_restore_plan(job, backup_manager)
        
        assert len(plan) == 1
        assert not plan.requires_incremental_restore


# ============ Validator Tests ============

class TestBackupValidator:
    """Tests for BackupValidator class."""
    
    def test_validate_valid_backup(self, temp_dir, temp_db, backup_manager):
        """Test validation of a valid backup."""
        job = backup_manager.create_backup()
        backup_path = Path(job.file_path)
        
        validator = BackupValidator(verify_checksum=True)
        result = validator.validate(backup_path, job.checksum)
        
        assert result.is_valid is True
        assert result.structure_valid is True
        assert result.integrity_valid is True
        assert result.checksum_valid is True
    
    def test_validate_missing_file(self, temp_dir):
        """Test validation of missing file."""
        validator = BackupValidator()
        result = validator.validate(temp_dir / "missing.db")
        
        assert result.is_valid is False
        assert "not found" in result.errors[0].lower()
    
    def test_validate_corrupt_checksum(self, temp_dir, temp_db, backup_manager):
        """Test validation with corrupt checksum."""
        job = backup_manager.create_backup()
        backup_path = Path(job.file_path)
        
        validator = BackupValidator(verify_checksum=True)
        result = validator.validate(backup_path, "0" * 64)  # Fake checksum
        
        assert result.is_valid is False
        assert result.checksum_valid is False


class TestBackupHealthChecker:
    """Tests for BackupHealthChecker class."""
    
    def test_check_health_empty(self, backup_manager):
        """Test health check with no backups."""
        checker = BackupHealthChecker(backup_manager)
        result = checker.check_health()
        
        assert result.total_backups == 0
    
    def test_check_health_with_backups(self, backup_manager):
        """Test health check with backups."""
        backup_manager.create_backup()
        backup_manager.create_backup()
        
        checker = BackupHealthChecker(backup_manager)
        result = checker.check_health()
        
        assert result.total_backups >= 2


# ============ Model Tests ============

class TestBackupJob:
    """Tests for BackupJob dataclass."""
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        job = BackupJob(
            id="test-id",
            user_id="test-user",
            backup_type=BackupType.FULL,
            status=BackupStatus.COMPLETED,
        )
        
        data = job.to_dict()
        
        assert data["id"] == "test-id"
        assert data["user_id"] == "test-user"
        assert data["backup_type"] == "full"
        assert data["status"] == "completed"
    
    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "id": "test-id",
            "user_id": "test-user",
            "backup_type": "full",
            "status": "completed",
            "file_path": "/path/to/backup.db",
            "file_size_bytes": 1024,
            "checksum": "abc123",
            "record_count": 10,
            "previous_backup_id": None,
            "started_at": "2024-01-01T00:00:00",
            "completed_at": "2024-01-01T00:01:00",
            "verified_at": None,
            "expires_at": None,
            "error_message": None,
            "metadata": "{}",
        }
        
        job = BackupJob.from_dict(data)
        
        assert job.id == "test-id"
        assert job.backup_type == BackupType.FULL
        assert job.status == BackupStatus.COMPLETED


class TestBackupManifest:
    """Tests for BackupManifest dataclass."""
    
    def test_to_json(self):
        """Test JSON serialization."""
        manifest = BackupManifest(
            backup_id="test-id",
            database_checksum="abc123",
            file_size_bytes=1024,
            record_count=100,
        )
        
        json_str = manifest.to_json()
        data = json.loads(json_str)
        
        assert data["backup_id"] == "test-id"
        assert data["database_checksum"] == "abc123"
    
    def test_from_json(self):
        """Test JSON deserialization."""
        json_str = json.dumps({
            "backup_id": "test-id",
            "created_at": "2024-01-01T00:00:00",
            "backup_type": "full",
            "database_checksum": "abc123",
            "file_size_bytes": 1024,
            "record_count": 100,
            "tables": {"habits": 10},
            "previous_backup_id": None,
            "checksum_algorithm": "sha256",
            "version": "1.0",
        })
        
        manifest = BackupManifest.from_json(json_str)
        
        assert manifest.backup_id == "test-id"
        assert manifest.database_checksum == "abc123"


class TestScheduleBuilder:
    """Tests for ScheduleBuilder class."""
    
    def test_build_daily_schedule(self):
        """Test building a daily schedule."""
        schedule = (ScheduleBuilder()
            .for_user("test-user")
            .daily()
            .at_time("02:00")
            .full_backup()
            .retention(daily=7, weekly=4, monthly=12)
            .build())
        
        assert schedule.user_id == "test-user"
        assert schedule.frequency == BackupFrequency.DAILY
        assert schedule.time_of_day == "02:00"
        assert schedule.backup_type == BackupType.FULL
        assert schedule.retention_daily == 7
    
    def test_build_weekly_schedule(self):
        """Test building a weekly schedule."""
        schedule = (ScheduleBuilder()
            .weekly(day_of_week=6)  # Sunday
            .at_time("03:00")
            .incremental_backup()
            .build())
        
        assert schedule.frequency == BackupFrequency.WEEKLY
        assert schedule.day_of_week == 6
        assert schedule.backup_type == BackupType.INCREMENTAL


# ============ Manifest Tests ============

class TestManifestManager:
    """Tests for ManifestManager class."""
    
    def test_save_and_load(self, temp_dir):
        """Test saving and loading manifests."""
        manifest_path = temp_dir / "backup.manifest.json"
        
        manifest = BackupManifest(
            backup_id="test-id",
            database_checksum="abc123",
            file_size_bytes=1024,
            record_count=100,
        )
        
        manager = ManifestManager()
        manager.save(manifest, manifest_path)
        
        assert manifest_path.exists()
        
        loaded = manager.load(manifest_path)
        
        assert loaded is not None
        assert loaded.backup_id == "test-id"
        assert loaded.database_checksum == "abc123"
    
    def test_get_manifest_path(self):
        """Test manifest path generation."""
        manager = ManifestManager()
        
        backup_path = Path("/backups/backup.db")
        manifest_path = manager.get_manifest_path(backup_path)
        
        assert manifest_path.name == "backup.manifest.json"


# ============ Integration Tests ============

class TestBackupIntegration:
    """Integration tests for backup system."""
    
    def test_full_backup_cycle(self, backup_manager, temp_dir):
        """Test complete backup cycle: create, verify, restore."""
        # 1. Create backup
        job = backup_manager.create_backup()
        assert job.status == BackupStatus.COMPLETED
        
        # 2. Verify backup
        verified = backup_manager.verify_backup(job.id)
        assert verified is True
        
        # 3. Restore backup
        restore_path = temp_dir / "restored.db"
        engine = RestoreEngine()
        result = engine.restore(
            backup_path=Path(job.file_path),
            target_path=restore_path,
            expected_checksum=job.checksum
        )
        
        assert result.success is True
        
        # 4. Verify restored database
        conn = sqlite3.connect(str(restore_path))
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        check_result = cursor.fetchone()
        conn.close()
        
        assert check_result[0] == "ok"
    
    def test_backup_with_retention(self, backup_manager):
        """Test backup with retention policy enforcement."""
        # Create multiple backups
        for _ in range(5):
            backup_manager.create_backup()
        
        # Get retention manager
        policy = RetentionPolicy(daily=3, weekly=2, monthly=1)
        retention_manager = RetentionManager(backup_manager, policy)
        
        # Preview retention
        preview = retention_manager.preview_retention()
        
        assert "summary" in preview
        assert "to_delete" in preview


# ============ Utility Function Tests ============

def test_quick_validate(temp_dir, temp_db, backup_manager):
    """Test quick validation utility."""
    from brain.backup.validator import quick_validate
    
    job = backup_manager.create_backup()
    backup_path = Path(job.file_path)
    
    is_valid, message = quick_validate(backup_path)
    
    assert is_valid is True
    assert "valid" in message.lower()


def test_preview_restore(temp_dir, temp_db, backup_manager):
    """Test restore preview utility."""
    from brain.backup.restore import preview_restore
    
    job = backup_manager.create_backup()
    backup_path = Path(job.file_path)
    target_path = temp_dir / "preview.db"
    
    preview = preview_restore(backup_path, target_path)
    
    assert preview["can_restore"] is True
    assert preview["backup_exists"] is True
    assert preview["total_records"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])