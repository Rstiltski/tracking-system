# Testing Guide for Tracking System

This guide provides comprehensive instructions for testing the AI-powered tracking system, following best practices from **PHASE_4_NOTIFICATIONS.md**.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Testing Philosophy](#testing-philosophy)
3. [Test Structure](#test-structure)
4. [Running Tests](#running-tests)
5. [Writing Tests](#writing-tests)
6. [Test Categories](#test-categories)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# Install testing dependencies
pip install pytest pytest-cov pytest-xdist

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=brain --cov-report=html

# Run specific test file
python -m pytest tests/test_notification_engine.py -v

# Use the test runner script
python run_tests.py --coverage
```

---

## Testing Philosophy

### Verification vs. Validation

Our testing approach follows two key principles:

| Type | Purpose | Tools |
|------|---------|-------|
| **Verification** | Ensure code runs correctly | `pytest`, `unittest` |
| **Validation** | Ensure model predicts correctly | Metrics (F1, MSE, Accuracy) |

### Key Principles

1. **Never test on training data** - Use 70/15/15 split (Train/Validation/Test)
2. **Test edge cases aggressively** - Null inputs, large datasets, unexpected types
3. **Mock external dependencies** - Database, APIs, file systems
4. **Fast feedback loop** - Unit tests should run in <100ms

---

## Test Structure

```
tracking-system/
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── test_notification_engine.py
│   ├── test_notification_preferences.py
│   ├── test_channels.py
│   └── integration_suite.py
├── brain/
│   ├── notifications/
│   │   ├── engine.py
│   │   ├── preferences.py
│   │   └── models.py
│   └── ...
├── pyproject.toml               # Pytest configuration
├── run_tests.py                 # Test runner script
└── TESTING_GUIDE.md             # This file
```

### File Naming Convention

- Test files: `test_*.py` or `*_test.py`
- Test classes: `Test*ClassName*`
- Test functions: `test_*_behavior_*`

---

## Running Tests

### Basic Commands

```bash
# Run all tests
python -m pytest

# Verbose output
python -m pytest -v

# Stop on first failure
python -m pytest -x

# Re-run failed tests only
python -m pytest --lf

# Show local variables on failure
python -m pytest -l
```

### Test Selection

```bash
# Run specific file
python -m pytest tests/test_notification_engine.py

# Run specific class
python -m pytest tests/test_notification_engine.py::TestNotificationDispatch

# Run specific function
python -m pytest tests/test_notification_engine.py::TestNotificationDispatch::test_dispatch_basic

# Run by marker
python -m pytest -m edge_case
python -m pytest -m "not slow"
```

### Coverage Reports

```bash
# Terminal report
python -m pytest --cov=brain --cov-report=term-missing

# HTML report (opens in browser)
python -m pytest --cov=brain --cov-report=html
open htmlcov/index.html

# Coverage with threshold (fails if <80%)
python -m pytest --cov=brain --cov-fail-under=80
```

### Using the Test Runner

```bash
# All tests
python run_tests.py

# Unit tests only
python run_tests.py --unit

# Integration tests only
python run_tests.py --integration

# Edge case tests
python run_tests.py --edge

# With coverage
python run_tests.py --coverage

# Watch mode (auto-rerun on changes)
python run_tests.py --watch
```

---

## Writing Tests

### Basic Test Structure

```python
"""
Unit Tests for Module Name

Run with: python -m pytest tests/test_module.py -v
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestClassName:
    """Test cases for ClassName."""

    def setup_method(self):
        """Set up test fixtures (runs before each test)."""
        self.mock_db = Mock()
        self.module = ModuleName(db=self.mock_db)

    def test_basic_behavior(self):
        """Test basic functionality."""
        # Arrange
        expected = "expected_value"
        
        # Act
        result = self.module.some_method()
        
        # Assert
        assert result == expected

    def test_edge_case_null_input(self):
        """Test handling of null inputs."""
        # Arrange
        null_input = None
        
        # Act & Assert
        with pytest.raises(ValueError):
            self.module.process(null_input)
```

### Using Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest

@pytest.fixture
def mock_db():
    """Create a mock database."""
    db = Mock()
    db.fetch_one = Mock(return_value=None)
    db.fetch_all = Mock(return_value=[])
    db.execute = Mock(return_value=Mock())
    return db

@pytest.fixture
def sample_notification():
    """Create a sample notification for testing."""
    return Notification(
        type=NotificationType.HABIT_REMINDER,
        title="Test Reminder",
        message="This is a test",
    )
```

```python
# tests/test_module.py
def test_notification_dispatch(mock_db, sample_notification):
    """Test dispatch using fixtures."""
    engine = NotificationEngine(db=mock_db)
    result = engine.dispatch(sample_notification)
    assert result.success
```

### Mocking Best Practices

```python
from unittest.mock import Mock, patch, MagicMock

# Mock a database
mock_db = Mock()
mock_db.fetch_one.return_value = {'id': 1, 'name': 'test'}
mock_db.fetch_all.return_value = [{'id': 1}, {'id': 2}]
mock_db.execute.return_value = Mock()

# Mock external API
with patch('requests.post') as mock_post:
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'success': True}
    
    result = send_notification()
    assert result.success

# Mock datetime (time-dependent tests)
with patch('datetime.datetime') as mock_datetime:
    mock_datetime.now.return_value = datetime(2026, 1, 1, 23, 0)  # 11 PM
    # Test quiet hours logic
```

---

## Test Categories

### 1. Unit Tests

Test individual functions/methods in isolation.

```python
def test_calculate_streak_basic():
    """Test basic streak calculation."""
    dates = ['2026-01-01', '2026-01-02', '2026-01-03']
    assert calculate_streak(dates) == 3

def test_calculate_streak_empty():
    """Test streak with empty input."""
    assert calculate_streak([]) == 0
```

### 2. Integration Tests

Test component interactions.

```python
@pytest.mark.integration
def test_notification_end_to_end():
    """Test full notification flow."""
    # Create notification
    notification = engine.create_notification(...)
    
    # Dispatch
    results = engine.dispatch(notification)
    
    # Verify database state
    saved = engine.get_notification(notification.id)
    assert saved.status == NotificationStatus.SENT
```

### 3. Edge Case Tests

Test boundary conditions and error handling.

```python
@pytest.mark.edge_case
def test_create_notification_null_title():
    """Test creating notification with null title."""
    notification = engine.create_notification(
        type=NotificationType.SYSTEM,
        title=None,  # Null input
        message="Test"
    )
    assert notification.title == ""  # Should handle gracefully

@pytest.mark.edge_case
def test_create_notification_very_long_message():
    """Test with extremely long message (100k chars)."""
    long_message = "A" * 100000
    notification = engine.create_notification(
        type=NotificationType.SYSTEM,
        title="Test",
        message=long_message
    )
    assert len(notification.message) == 100000
```

### 4. Performance Tests

Test with large datasets.

```python
@pytest.mark.slow
def test_bulk_notification_creation():
    """Test creating 1000 notifications."""
    import time
    
    start = time.time()
    
    for i in range(1000):
        engine.create_notification(
            type=NotificationType.SYSTEM,
            title=f"Notification {i}",
            message="Test"
        )
    
    elapsed = time.time() - start
    assert elapsed < 5.0  # Should complete in <5 seconds
```

---

## Best Practices

### 1. Test Naming

```python
# Good: Descriptive name
def test_dispatch_quiet_hours_blocks_notification():
    pass

# Bad: Vague name
def test_dispatch():
    pass
```

### 2. Arrange-Act-Assert Pattern

```python
def test_notification_creation():
    # Arrange
    expected_title = "Test Reminder"
    
    # Act
    notification = engine.create_notification(
        type=NotificationType.HABIT_REMINDER,
        title=expected_title,
        message="Test"
    )
    
    # Assert
    assert notification.title == expected_title
```

### 3. Test Independence

```python
# Good: Each test is independent
def test_one():
    engine = NotificationEngine(db=mock_db)
    result = engine.create_notification(...)

def test_two():
    engine = NotificationEngine(db=mock_db)
    result = engine.dispatch(...)

# Bad: Tests depend on each other
def test_one():
    global notification
    notification = engine.create_notification(...)

def test_two():
    # Depends on test_one running first!
    engine.dispatch(notification)
```

### 4. Edge Case Checklist

When testing any function, consider:

- [ ] Null/None inputs
- [ ] Empty strings/collections
- [ ] Very large inputs
- [ ] Special characters (emoji, HTML, quotes)
- [ ] Invalid data types
- [ ] Boundary values (0, -1, max int)
- [ ] Concurrent access
- [ ] Time zone edge cases

### 5. Effective Prompts for AI-Assisted Testing

When using AI to generate tests:

**Ineffective:**
> "Test this Python code."

**Effective:**
> "Act as a Senior QA Engineer. Write pytest unit tests for this function, including:
> - Edge cases for null inputs
> - Tests for extremely large datasets
> - Tests for unexpected data types
> - Mock database interactions
> - Coverage of all decision branches"

---

## Troubleshooting

### Common Issues

#### Import Errors

```
ModuleNotFoundError: No module named 'brain'
```

**Solution:** Add parent directory to path:
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

#### Fixture Not Found

```
fixture 'mock_db' not found
```

**Solution:** Ensure `conftest.py` is in the `tests/` directory.

#### Tests Not Discovered

```
collected 0 items
```

**Solution:** Check naming convention:
- Files must be named `test_*.py`
- Functions must be named `test_*`
- Classes must be named `Test*`

#### Coverage Too Low

```
FAIL Required coverage is 80%, but only 65% covered
```

**Solution:** Add tests for uncovered modules:
```bash
# See which lines are not covered
python -m pytest --cov=brain --cov-report=term-missing

# Focus on uncovered lines
```

### Debugging Tests

```bash
# Print statements during test
python -m pytest -s

# Show local variables on failure
python -m pytest -l

# Step-by-step debugging
python -m pytest --pdb

# Run single test with verbose output
python -m pytest tests/test_file.py::TestClass::test_method -vv
```

---

## Metrics and Quality Gates

### Coverage Targets

| Component | Target |
|-----------|--------|
| Core logic (brain/) | 80%+ |
| Models | 90%+ |
| API endpoints | 85%+ |
| UI components | 70%+ |

### Performance Targets

| Test Type | Max Duration |
|-----------|--------------|
| Unit test | <100ms |
| Integration test | <1s |
| Full test suite | <5min |

### Quality Gates

```bash
# Run with quality checks
python -m pytest \
  --cov=brain \
  --cov-fail-under=80 \
  --maxfail=5 \
  --timeout=300 \
  -v
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: python -m pytest --cov=brain --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [PHASE_4_NOTIFICATIONS.md](phases/PHASE_4_NOTIFICATIONS.md) - Testing philosophy
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
