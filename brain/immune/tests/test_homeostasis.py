"""
Test Homeostasis

📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import sqlite3
from brain.immune.homeostasis import HomeostaticRegulator

def _setup_db():
    conn = sqlite3.connect(':memory:')
    conn.execute('\n        CREATE TABLE immune_metrics (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            timestamp TEXT,\n            queue_depth INTEGER,\n            memory_usage_bytes BIGINT,\n            sandbox_accuracy_pct REAL\n        )\n        ')
    conn.execute('\n        CREATE TABLE neuro_synapse (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            timestamp TEXT,\n            queue_depth INTEGER,\n            memory_usage_bytes BIGINT,\n            sandbox_accuracy_pct REAL,\n            load_ratio REAL,\n            arousal REAL,\n            valence REAL\n        )\n        ')
    conn.execute('\n        INSERT INTO immune_metrics (\n            timestamp, queue_depth, memory_usage_bytes, sandbox_accuracy_pct\n        ) VALUES (?, ?, ?, ?)\n        ', ('2026-01-12T00:00:00', 250, 1000000, 95.0))
    conn.commit()
    return conn

def test_homeostasis_records_synapse():
    conn = _setup_db()
    regulator = HomeostaticRegulator(conn, queue_threshold=500, memory_threshold_bytes=10000000)
    snapshot = regulator.run_once()
    assert snapshot is not None
    row = conn.execute('SELECT COUNT(*) FROM neuro_synapse').fetchone()
    assert (((((((((((((((row[0] if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) == 1