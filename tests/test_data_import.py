"""
Unit Tests for Data Import Module

Python pytest tests for the data import functionality.
Tests parsers, validator, conflict resolver, and importer.

All implementation is in Python 3.10+ using pytest

Run with:
    python -m pytest tests/test_data_import.py -v
"""

import pytest
import json
import csv
import tempfile
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ==========================================
# Fixtures
# ==========================================

@pytest.fixture
def mock_db():
    """Create a mock database connection."""
    db = Mock()
    db.execute = Mock(return_value=Mock())
    db.fetchone = Mock(return_value=None)
    db.fetchall = Mock(return_value=[])
    db.commit = Mock()
    db.rollback = Mock()
    db.row_factory = sqlite3.Row
    return db


@pytest.fixture
def sample_json_export(tmp_path):
    """Create a sample JSON export file."""
    export_data = {
        "metadata": {
            "exported_at": datetime.now().isoformat(),
            "version": "1.0"
        },
        "habits": [
            {
                "id": "habit-1",
                "name": "Exercise",
                "streak": 5,
                "frequency": "daily"
            },
            {
                "id": "habit-2",
                "name": "Reading",
                "streak": 10,
                "frequency": "daily"
            }
        ],
        "tasks": [
            {
                "id": "task-1",
                "title": "Complete project",
                "priority": "high",
                "completed": False
            }
        ]
    }
    
    file_path = tmp_path / "export.json"
    with open(file_path, 'w') as f:
        json.dump(export_data, f)
    
    return str(file_path)


@pytest.fixture
def sample_csv_export(tmp_path):
    """Create a sample CSV export file."""
    file_path = tmp_path / "habits.csv"
    
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'streak', 'frequency'])
        writer.writerow(['habit-1', 'Exercise', '5', 'daily'])
        writer.writerow(['habit-2', 'Reading', '10', 'daily'])
    
    return str(file_path)


# ==========================================
# Parser Tests
# ==========================================

class TestJSONParser:
    """Tests for JSON parser."""
    
    def test_parse_valid_json(self, sample_json_export):
        """Test parsing valid JSON export."""
        from brain.data_import.parsers import JSONParser
        
        parser = JSONParser(sample_json_export)
        result = parser.parse()
        
        assert 'habits' in result.modules
        assert 'tasks' in result.modules
        assert len(result.modules['habits']) == 2
        assert len(result.modules['tasks']) == 1
    
    def test_parse_missing_file(self):
        """Test parsing non-existent file."""
        from brain.data_import.parsers import JSONParser
        
        parser = JSONParser("/nonexistent/file.json")
        
        with pytest.raises(FileNotFoundError):
            parser.parse()
    
    def test_parse_invalid_json(self, tmp_path):
        """Test parsing invalid JSON."""
        file_path = tmp_path / "invalid.json"
        with open(file_path, 'w') as f:
            f.write("{ invalid json }")
        
        from brain.data_import.parsers import JSONParser
        
        parser = JSONParser(str(file_path))
        
        with pytest.raises(json.JSONDecodeError):
            parser.parse()
    
    def test_validate_structure(self, sample_json_export):
        """Test JSON structure validation."""
        from brain.data_import.parsers import JSONParser
        
        parser = JSONParser(sample_json_export)
        parser.parse()  # Must parse first
        
        assert parser.validate_structure() is True


class TestCSVParser:
    """Tests for CSV parser."""
    
    def test_parse_single_csv(self, sample_csv_export):
        """Test parsing single CSV file."""
        from brain.data_import.parsers import CSVParser
        
        parser = CSVParser(sample_csv_export, module_name='habits')
        result = parser.parse()
        
        assert 'habits' in result.modules
        assert len(result.modules['habits']) == 2
    
    def test_parse_csv_with_empty_values(self, tmp_path):
        """Test parsing CSV with empty values."""
        file_path = tmp_path / "tasks.csv"
        
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'title', 'description'])
            writer.writerow(['task-1', 'Test', ''])  # Empty description
            writer.writerow(['task-2', '', 'No title'])
        
        from brain.data_import.parsers import CSVParser
        
        parser = CSVParser(str(file_path), module_name='tasks')
        result = parser.parse()
        
        # Empty strings should be converted to None
        assert result.modules['tasks'][0]['description'] is None


# ==========================================
# Validator Tests
# ==========================================

class TestImportValidator:
    """Tests for import validator."""
    
    def test_validate_valid_data(self, mock_db):
        """Test validating valid data."""
        from brain.data_import.validator import ImportValidator
        
        validator = ImportValidator(mock_db)
        
        modules = {
            'habits': [
                {'id': 'habit-1', 'name': 'Exercise'}
            ]
        }
        
        is_valid, errors = validator.validate_all(modules)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_missing_required_field(self, mock_db):
        """Test validation with missing required field."""
        from brain.data_import.validator import ImportValidator
        
        validator = ImportValidator(mock_db)
        
        modules = {
            'habits': [
                {'id': 'habit-1'}  # Missing 'name'
            ]
        }
        
        is_valid, errors = validator.validate_all(modules)
        
        assert is_valid is False
        assert len(errors) == 1
        assert errors[0].field == 'name'
    
    def test_validate_negative_streak(self, mock_db):
        """Test validation with negative streak."""
        from brain.data_import.validator import ImportValidator
        
        validator = ImportValidator(mock_db)
        
        modules = {
            'habits': [
                {'id': 'habit-1', 'name': 'Exercise', 'streak': -5}
            ]
        }
        
        is_valid, errors = validator.validate_all(modules)
        
        assert is_valid is False
        assert errors[0].error_type == 'business_rule'
    
    def test_validate_invalid_priority(self, mock_db):
        """Test validation with invalid task priority."""
        from brain.data_import.validator import ImportValidator
        
        validator = ImportValidator(mock_db)
        
        modules = {
            'tasks': [
                {'id': 'task-1', 'title': 'Test', 'priority': 'invalid'}
            ]
        }
        
        is_valid, errors = validator.validate_all(modules)
        
        assert is_valid is False
        assert errors[0].error_type == 'business_rule'


# ==========================================
# Conflict Resolver Tests
# ==========================================

class TestConflictResolver:
    """Tests for conflict resolver."""
    
    def test_detect_conflict_by_id(self, mock_db):
        """Test detecting conflict by ID."""
        from brain.data_import.conflict_resolver import ConflictResolver
        
        # Mock existing record
        mock_db.execute.return_value.fetchone.return_value = {
            'id': 'habit-1',
            'name': 'Existing Habit'
        }
        
        resolver = ConflictResolver(mock_db)
        
        modules = {
            'habits': [
                {'id': 'habit-1', 'name': 'New Habit'}
            ]
        }
        
        conflicts = resolver.detect_conflicts(modules)
        
        assert len(conflicts) == 1
        assert conflicts[0].module == 'habits'
    
    def test_resolve_skip(self, mock_db):
        """Test skip resolution strategy."""
        from brain.data_import.conflict_resolver import (
            ConflictResolver, ConflictStrategy
        )
        
        resolver = ConflictResolver(mock_db)
        
        conflict = resolver._check_by_id(
            'habits', 'habit-1',
            {'id': 'habit-1', 'name': 'New Habit'}
        )
        
        resolution = resolver.resolve(conflict, ConflictStrategy.SKIP)
        
        assert resolution.value == 'skipped'
    
    def test_resolve_overwrite(self, mock_db):
        """Test overwrite resolution strategy."""
        from brain.data_import.conflict_resolver import (
            ConflictResolver, ConflictStrategy
        )
        
        resolver = ConflictResolver(mock_db)
        
        conflict = resolver._check_by_id(
            'habits', 'habit-1',
            {'id': 'habit-1', 'name': 'New Habit'}
        )
        
        resolution = resolver.resolve(conflict, ConflictStrategy.OVERWRITE)
        
        assert resolution.value == 'overwritten'


# ==========================================
# Importer Tests
# ==========================================

class TestDataImporter:
    """Tests for main DataImporter class."""
    
    def test_preview_import(self, mock_db, sample_json_export):
        """Test previewing import."""
        from brain.data_import import DataImporter
        
        importer = DataImporter(db_connection=mock_db)
        preview = importer.preview(sample_json_export)
        
        assert preview.total_records == 3  # 2 habits + 1 task
        assert 'habits' in preview.records_by_module
        assert 'tasks' in preview.records_by_module
    
    def test_dry_run_import(self, mock_db, sample_json_export):
        """Test dry run import (no commit)."""
        from brain.data_import import DataImporter
        from brain.data_import.models import ConflictStrategy
        
        importer = DataImporter(db_connection=mock_db)
        
        result = importer.import_file(
            sample_json_export,
            user_id='test-user',
            strategy=ConflictStrategy.SKIP,
            dry_run=True
        )
        
        assert result.success is True
        assert result.details.get('dry_run') is True
    
    def test_import_invalid_file(self, mock_db):
        """Test importing non-existent file."""
        from brain.data_import import DataImporter
        
        importer = DataImporter(db_connection=mock_db)
        
        result = importer.import_file('/nonexistent/file.json')
        
        assert result.success is False
        assert 'No such file' in result.error_message or 'not found' in result.error_message.lower()


# ==========================================
# Integration Tests
# ==========================================

@pytest.mark.integration
class TestImportWorkflow:
    """Integration tests for full import workflow."""
    
    def test_full_import_cycle(self, tmp_path):
        """Test complete import workflow."""
        import sqlite3
        from brain.data_import import DataImporter
        from brain.data_import.models import ConflictStrategy
        
        # Create test database
        db_path = tmp_path / "test.db"
        db = sqlite3.connect(str(db_path))
        
        # Create tables
        db.execute("""
            CREATE TABLE habits (
                id TEXT PRIMARY KEY,
                name TEXT,
                streak INTEGER,
                frequency TEXT
            )
        """)
        db.commit()
        
        # Create export file
        export_data = {
            "habits": [
                {"id": "habit-1", "name": "Exercise", "streak": 5, "frequency": "daily"}
            ]
        }
        
        export_path = tmp_path / "export.json"
        with open(export_path, 'w') as f:
            json.dump(export_data, f)
        
        # Import
        importer = DataImporter(db_connection=db)
        result = importer.import_file(
            str(export_path),
            strategy=ConflictStrategy.SKIP,
            dry_run=False
        )
        
        assert result.success is True
        assert result.records_imported == 1
        
        # Verify data was imported
        cursor = db.execute("SELECT COUNT(*) FROM habits")
        count = cursor.fetchone()[0]
        assert count == 1
        
        db.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
