"""
Database schema for Brain audit tables
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/06_audit_schema.md
- LLM_AGENT_QUICKSTART.md
"""

import db


def ensure_audit_tables():
    """Ensure Brain audit tables exist"""
    with db.get_conn() as conn:
        # Primary audit log table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS brain_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_id TEXT NOT NULL UNIQUE,
                sequence_number INTEGER NOT NULL,

                -- Command details
                command_type TEXT NOT NULL,
                command_params TEXT NOT NULL,
                idempotency_key TEXT,

                -- Execution context
                user_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,
                session_id TEXT,
                client_ip TEXT,
                user_agent TEXT,

                -- Timestamps
                received_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                duration_ms INTEGER,

                -- Execution results
                status TEXT NOT NULL,
                result_data TEXT,
                error_code TEXT,
                error_message TEXT,
                stack_trace TEXT,

                -- Confirmation & risk
                risk_tier INTEGER NOT NULL,
                confirmation_required BOOLEAN NOT NULL DEFAULT 0,
                confirmation_token TEXT,
                confirmation_at TEXT,
                dry_run_result TEXT,

                -- Tool execution plan
                plan TEXT,
                tool_results TEXT,

                -- State machine transition
                entity_type TEXT,
                entity_id INTEGER,
                state_before TEXT,
                state_after TEXT,

                -- Metadata
                metadata TEXT,
                tags TEXT,

                -- Indexing
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_brain_audit_command_id ON brain_audit_log(command_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_brain_audit_command_type ON brain_audit_log(command_type);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_brain_audit_user_id ON brain_audit_log(user_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_brain_audit_company_id ON brain_audit_log(company_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_brain_audit_entity ON brain_audit_log(entity_type, entity_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_brain_audit_created_at ON brain_audit_log(created_at);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_brain_audit_status ON brain_audit_log(status);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_brain_audit_idempotency_key ON brain_audit_log(idempotency_key);")

        # Tool calls table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS brain_tool_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_id TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                tool_params TEXT NOT NULL,
                tool_result TEXT,
                success BOOLEAN NOT NULL,
                error_code TEXT,
                error_message TEXT,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                duration_ms INTEGER,

                FOREIGN KEY (command_id) REFERENCES brain_audit_log(command_id)
            )
        """)

        conn.execute("CREATE INDEX IF NOT EXISTS idx_brain_tool_calls_command_id ON brain_tool_calls(command_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_brain_tool_calls_tool_name ON brain_tool_calls(tool_name);")

        # State transitions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS brain_state_transitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_id TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                state_before TEXT NOT NULL,
                state_after TEXT NOT NULL,
                transition_valid BOOLEAN NOT NULL,
                preconditions_met BOOLEAN NOT NULL,
                side_effects TEXT,
                transitioned_at TEXT NOT NULL,

                FOREIGN KEY (command_id) REFERENCES brain_audit_log(command_id)
            )
        """)

        conn.execute("CREATE INDEX IF NOT EXISTS idx_brain_state_transitions_command_id ON brain_state_transitions(command_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_brain_state_transitions_entity ON brain_state_transitions(entity_type, entity_id);")

        conn.commit()


# Run on import to ensure tables exist
if __name__ == "__main__":
    ensure_audit_tables()
    print("✅ Brain audit tables created successfully")
