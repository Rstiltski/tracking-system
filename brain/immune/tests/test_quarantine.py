"""
Test Quarantine

📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import sqlite3
from datetime import datetime, timedelta

from brain.immune.quarantine import ImmuneQuarantineManager


def _setup_db():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE immune_quarantine (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fingerprint VARCHAR(64) UNIQUE NOT NULL,
            tool_name VARCHAR(255) NOT NULL,
            failure_count INTEGER DEFAULT 0,
            backoff_until TIMESTAMP NULL,
            status VARCHAR(20) DEFAULT 'ACTIVE',
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_failure TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            escalation_reason TEXT NULL,
            updated_at TIMESTAMP NULL
        )
        """
    )
    return conn


def test_quarantine_records_backoff():
    conn = _setup_db()
    manager = ImmuneQuarantineManager(conn)

    status = manager.record_failure("fingerprint-1", "ToolA", base_backoff_sec=1)
    assert status.failure_count == 1
    assert status.backoff_until is not None

    status = manager.record_failure("fingerprint-1", "ToolA", base_backoff_sec=1)
    assert status.failure_count == 2
    assert status.backoff_until > datetime.utcnow()


def test_quarantine_check_respects_status():
    conn = _setup_db()
    manager = ImmuneQuarantineManager(conn)

    manager.record_failure("fingerprint-2", "ToolB", base_backoff_sec=1)
    assert manager.is_quarantined("fingerprint-2")

    manager.resolve("fingerprint-2")
    assert not manager.is_quarantined("fingerprint-2")


def test_quarantine_backoff_expires():
    conn = _setup_db()
    manager = ImmuneQuarantineManager(conn)

    manager.record_failure("fingerprint-3", "ToolC", base_backoff_sec=1)
    conn.execute(
        "UPDATE immune_quarantine SET backoff_until = ? WHERE fingerprint = ?",
        ((datetime.utcnow() - timedelta(seconds=5)).isoformat(), "fingerprint-3"),
    )
    conn.commit()

    assert not manager.is_quarantined("fingerprint-3")
