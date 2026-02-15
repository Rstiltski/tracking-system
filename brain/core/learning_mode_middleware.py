"""
Learning Mode Middleware - Confidence Gate for AI Command Execution

Part of Sentient System Phase 2: The Safety (Logic)

This middleware implements the "Confidence Gate" logic that decides whether
to execute a command silently or ask for user confirmation based on:
1. User's ai_learning_mode setting (Student vs Expert)
2. Command confidence score
3. Command risk level

The logic follows this decision tree:
- If Risk = CRITICAL → Always require Nuclear Codes Modal
- If Learning Mode = ON (Student) → Always ask for confirmation
- If Confidence < threshold → Ask for Socratic confirmation
- Else → Execute silently
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- BRAIN_TOOLS_REFERENCE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import db
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from brain.core.enums import RiskTier

@dataclass
class ConfidenceDecision:
    """Result of the confidence gate decision"""
    should_execute: bool
    requires_nuclear_codes: bool
    requires_socratic: bool
    reason: str
    confidence_score: float
    learning_mode: bool

class LearningModeMiddleware:
    """
    Middleware that checks Learning Mode and Confidence before executing commands.
    
    This is the core safety system that prevents the AI from acting without
    user permission when it's uncertain or when the user wants to be consulted.
    """
    DEFAULT_CONFIDENCE_THRESHOLD = 0.9

    def __init__(self, db_connection=None):
        """
        Initialize the middleware.
        
        Args:
            db_connection: Optional database connection (uses db.get_conn() if None)
        """
        self.db_connection = db_connection

    def check_execution_gate(self, user_id: int, command_type: str, risk_tier: RiskTier, confidence_score: float=1.0) -> ConfidenceDecision:
        """
        Check whether a command should execute silently or require confirmation.
        
        This is the main "Confidence Gate" logic from the Sentient System Master Plan.
        
        Args:
            user_id: ID of the user executing the command
            command_type: The command being executed (e.g., "CustomerDelete")
            risk_tier: The risk tier of the command (TRIVIAL, LOW, MEDIUM, HIGH, CRITICAL)
            confidence_score: AI confidence in understanding the command (0.0 to 1.0)
            
        Returns:
            ConfidenceDecision with instructions on how to proceed
        """
        # Skip learning mode checks in development environment
        import os
        if os.getenv('ENVIRONMENT') == 'development':
            return ConfidenceDecision(should_execute=True, requires_nuclear_codes=False, requires_socratic=False, reason='Development mode - bypassing learning mode checks', confidence_score=confidence_score, learning_mode=False)
        
        user_settings = self._get_user_settings(user_id)
        learning_mode = user_settings.get('ai_learning_mode', False)
        confidence_threshold = user_settings.get('ai_confidence_threshold', self.DEFAULT_CONFIDENCE_THRESHOLD)
        if risk_tier == RiskTier.CRITICAL:
            return ConfidenceDecision(should_execute=False, requires_nuclear_codes=True, requires_socratic=False, reason='CRITICAL risk operations always require Nuclear Codes confirmation', confidence_score=confidence_score, learning_mode=learning_mode)
        if learning_mode:
            return ConfidenceDecision(should_execute=False, requires_nuclear_codes=False, requires_socratic=True, reason='Learning Mode is ON - system acts as Student and always asks for confirmation', confidence_score=confidence_score, learning_mode=learning_mode)
        if confidence_score < confidence_threshold:
            return ConfidenceDecision(should_execute=False, requires_nuclear_codes=False, requires_socratic=True, reason=f'Confidence ({confidence_score:.2f}) below threshold ({confidence_threshold:.2f}) - asking for confirmation', confidence_score=confidence_score, learning_mode=learning_mode)
        if risk_tier == RiskTier.HIGH:
            return ConfidenceDecision(should_execute=False, requires_nuclear_codes=False, requires_socratic=True, reason='HIGH risk operations require confirmation even in Expert mode', confidence_score=confidence_score, learning_mode=learning_mode)
        return ConfidenceDecision(should_execute=True, requires_nuclear_codes=False, requires_socratic=False, reason='All gates passed - sufficient confidence and user is in Expert mode', confidence_score=confidence_score, learning_mode=learning_mode)

    def _get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """
        Get user's Learning Mode settings from database.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with settings:
            - ai_learning_mode: bool (True = Student, False = Expert)
            - ai_confidence_threshold: float (0.0 to 1.0)
            - enable_socratic_prompts: bool
            - enable_rage_detection: bool
        """
        with db.get_conn() as conn:
            result = conn.execute("\n                SELECT name FROM sqlite_master \n                WHERE type='table' AND name='user_settings'\n            ").fetchone()
            if not result:
                return {'ai_learning_mode': True, 'ai_confidence_threshold': self.DEFAULT_CONFIDENCE_THRESHOLD, 'enable_socratic_prompts': True, 'enable_rage_detection': True}
            settings = conn.execute('\n                SELECT \n                    ai_learning_mode,\n                    ai_confidence_threshold,\n                    enable_socratic_prompts,\n                    enable_rage_detection\n                FROM user_settings\n                WHERE user_id = ?\n            ', (user_id,)).fetchone()
            if not settings:
                conn.execute('\n                    INSERT INTO user_settings (\n                        user_id,\n                        ai_learning_mode,\n                        ai_confidence_threshold,\n                        enable_socratic_prompts,\n                        enable_rage_detection\n                    ) VALUES (?, ?, ?, ?, ?)\n                ', (user_id, True, self.DEFAULT_CONFIDENCE_THRESHOLD, True, True))
                return {'ai_learning_mode': True, 'ai_confidence_threshold': self.DEFAULT_CONFIDENCE_THRESHOLD, 'enable_socratic_prompts': True, 'enable_rage_detection': True}
            settings = dict(settings)  # Convert sqlite3.Row to dict
            return {'ai_learning_mode': bool(settings.get('ai_learning_mode', 0)), 'ai_confidence_threshold': float(settings.get('ai_confidence_threshold', 0) if settings.get('ai_confidence_threshold', 0) else self.DEFAULT_CONFIDENCE_THRESHOLD), 'enable_socratic_prompts': bool(settings.get('enable_socratic_prompts', 0) if settings.get('enable_socratic_prompts', 0) is not None else True), 'enable_rage_detection': bool(settings.get('enable_rage_detection', 0) if settings.get('enable_rage_detection', 0) is not None else True)}

    def update_user_learning_mode(self, user_id: int, learning_mode: bool) -> bool:
        """
        Update user's Learning Mode setting.
        
        Args:
            user_id: ID of the user
            learning_mode: True = Student mode (always ask), False = Expert mode (act when confident)
            
        Returns:
            True if updated successfully
        """
        with db.get_conn() as conn:
            existing = conn.execute('SELECT user_id FROM user_settings WHERE user_id = ?', (user_id,)).fetchone()
            if existing:
                conn.execute("\n                    UPDATE user_settings \n                    SET ai_learning_mode = ?,\n                        updated_at = datetime('now')\n                    WHERE user_id = ?\n                ", (learning_mode, user_id))
            else:
                conn.execute('\n                    INSERT INTO user_settings (\n                        user_id,\n                        ai_learning_mode,\n                        ai_confidence_threshold,\n                        enable_socratic_prompts,\n                        enable_rage_detection\n                    ) VALUES (?, ?, ?, ?, ?)\n                ', (user_id, learning_mode, self.DEFAULT_CONFIDENCE_THRESHOLD, True, True))
            return True

    def log_confidence_decision(self, user_id: int, command_type: str, decision: ConfidenceDecision, user_response: Optional[bool]=None):
        """
        Log confidence gate decisions for learning and debugging.
        
        This creates a record of every time the system asked for confirmation
        or executed silently, which can be used to:
        1. Train the AI to be more accurate
        2. Debug issues where AI misunderstood
        3. Analyze user behavior patterns
        
        Args:
            user_id: ID of the user
            command_type: The command being executed
            decision: The ConfidenceDecision result
            user_response: Optional - whether user confirmed (True/False/None)
        """
        with db.get_conn() as conn:
            result = conn.execute("\n                SELECT name FROM sqlite_master \n                WHERE type='table' AND name='confidence_gate_log'\n            ").fetchone()
            if not result:
                conn.execute('\n                CREATE TABLE confidence_gate_log (\n                    id INTEGER PRIMARY KEY AUTOINCREMENT,\n                    user_id INTEGER NOT NULL,\n                    command_type VARCHAR(100) NOT NULL,\n                    confidence_score DECIMAL(3,2),\n                    learning_mode BOOLEAN,\n                    requires_nuclear_codes BOOLEAN,\n                    requires_socratic BOOLEAN,\n                    should_execute BOOLEAN,\n                    decision_reason TEXT,\n                    user_response BOOLEAN,  -- NULL if not asked, TRUE if confirmed, FALSE if rejected\n                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                    \n                    FOREIGN KEY (user_id) REFERENCES users(id)\n                )\n            ')
                conn.execute('\n                CREATE INDEX idx_confidence_log_user \n                ON confidence_gate_log(user_id, timestamp DESC)\n            ')
            conn.execute('\n            INSERT INTO confidence_gate_log (\n                user_id,\n                command_type,\n                confidence_score,\n                learning_mode,\n                requires_nuclear_codes,\n                requires_socratic,\n                should_execute,\n                decision_reason,\n                user_response\n            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)\n        ', (user_id, command_type, decision.confidence_score, decision.learning_mode, decision.requires_nuclear_codes, decision.requires_socratic, decision.should_execute, decision.reason, user_response))
_middleware_instance = None

def get_learning_mode_middleware(db_connection=None) -> LearningModeMiddleware:
    """Get or create the singleton LearningModeMiddleware instance"""
    global _middleware_instance
    if _middleware_instance is None:
        _middleware_instance = LearningModeMiddleware(db_connection)
    return _middleware_instance
