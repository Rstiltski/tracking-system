"""
AI Policy Enforcer for Brain Architecture

This module integrates AI-powered code analysis into the Brain's policy engine.
It can be used to validate code changes before they're committed or deployed.

Integration points:
1. Pre-commit hooks (git)
2. Brain command validation (before execution)
3. CI/CD pipelines
4. Development-time linting
📚 REQUIRED READING BEFORE MODIFICATION:
- SECURITY_GUIDE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

import os
import ast
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PolicyViolation:
    """Represents a policy violation detected in code."""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    rule_name: str
    file_path: str
    line_number: int
    description: str
    fix_suggestion: str


class AIPolicyEnforcer:
    """
    Enforces Brain architecture policies using AST analysis and optional AI.

    This enforcer can work in two modes:
    1. Static analysis (AST-based, no API calls)
    2. AI-enhanced (uses DeepSeek/OpenAI for deeper analysis)
    """

    # Brain architecture rules
    RULES = {
        "session_state_safety": {
            "severity": "CRITICAL",
            "description": "No module-level st.session_state access allowed",
            "pattern": "st.session_state at module level"
        },
        "brain_facade_usage": {
            "severity": "HIGH",
            "description": "Must use get_brain_facade with user_id parameter",
            "pattern": "get_brain() without user_id"
        },
        "direct_db_writes": {
            "severity": "CRITICAL",
            "description": "Database writes must go through Brain facade",
            "pattern": "Direct INSERT/UPDATE/DELETE via db.execute"
        },
        "proper_indentation": {
            "severity": "HIGH",
            "description": "Render functions must contain all page logic",
            "pattern": "Code outside function definitions"
        }
    }

    def __init__(self, use_ai: bool = False, ai_api_key: Optional[str] = None):
        """
        Initialize the policy enforcer.

        Args:
            use_ai: Whether to use AI-enhanced analysis
            ai_api_key: API key for DeepSeek (optional if use_ai=False)
        """
        self.use_ai = use_ai
        self.ai_api_key = ai_api_key or os.getenv("DEEPSEEK_API_KEY")

        if use_ai and not self.ai_api_key:
            logger.warning(
                "AI mode requested but no API key provided. "
                "Falling back to static analysis only."
            )
            self.use_ai = False

    def validate_file(self, filepath: str, content: Optional[str] = None) -> List[PolicyViolation]:
        """
        Validate a file against Brain architecture policies.

        Args:
            filepath: Path to the file to validate
            content: Optional file content (if None, reads from filepath)

        Returns:
            List of policy violations found
        """
        violations = []

        # Read file if content not provided
        if content is None:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except FileNotFoundError:
                logger.error(f"File not found: {filepath}")
                return []

        # Static analysis (always run)
        violations.extend(self._static_analysis(filepath, content))

        # AI analysis (if enabled)
        if self.use_ai:
            violations.extend(self._ai_analysis(filepath, content))

        return violations

    def _static_analysis(self, filepath: str, content: str) -> List[PolicyViolation]:
        """
        Perform static AST-based analysis.

        This catches common violations without needing AI.
        """
        violations = []

        try:
            tree = ast.parse(content, filename=filepath)

            # Check for module-level session state access
            violations.extend(self._check_session_state_safety(filepath, tree))

            # Check for incorrect brain facade usage
            violations.extend(self._check_brain_facade_imports(filepath, content))

            # Check for direct database writes
            violations.extend(self._check_direct_db_writes(filepath, tree, content))

        except SyntaxError as e:
            violations.append(PolicyViolation(
                severity="CRITICAL",
                rule_name="syntax_error",
                file_path=filepath,
                line_number=e.lineno or 0,
                description=f"Syntax error: {e.msg}",
                fix_suggestion="Fix the syntax error before proceeding"
            ))

        return violations

    def _check_session_state_safety(self, filepath: str, tree: ast.AST) -> List[PolicyViolation]:
        """Check for dangerous module-level session state access."""
        violations = []

        class SessionStateChecker(ast.NodeVisitor):
            def __init__(self):
                self.violations = []
                self.in_function = False

            def visit_FunctionDef(self, node):
                old_in_function = self.in_function
                self.in_function = True
                self.generic_visit(node)
                self.in_function = old_in_function

            def visit_Assign(self, node):
                if not self.in_function:
                    if isinstance(node.value, ast.Attribute):
                        if self._is_session_state_user(node.value):
                            self.violations.append(PolicyViolation(
                                severity="CRITICAL",
                                rule_name="session_state_safety",
                                file_path=filepath,
                                line_number=node.lineno,
                                description="st.session_state.user accessed at module level",
                                fix_suggestion="Move inside function or use st.session_state.get('user', default_value)"
                            ))
                self.generic_visit(node)

            def _is_session_state_user(self, node):
                """Check if node is st.session_state.user."""
                if isinstance(node, ast.Attribute) and node.attr == 'user':
                    if isinstance(node.value, ast.Attribute) and node.value.attr == 'session_state':
                        if isinstance(node.value.value, ast.Name) and node.value.value.id == 'st':
                            return True
                return False

        checker = SessionStateChecker()
        checker.visit(tree)
        violations.extend(checker.violations)

        return violations

    def _check_brain_facade_imports(self, filepath: str, content: str) -> List[PolicyViolation]:
        """Check for incorrect brain facade imports."""
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Check for old get_brain import
            if 'from brain_facade import get_brain' in line and 'get_brain_facade' not in line:
                violations.append(PolicyViolation(
                    severity="HIGH",
                    rule_name="brain_facade_usage",
                    file_path=filepath,
                    line_number=i,
                    description="Using deprecated get_brain import",
                    fix_suggestion="Change to: from brain_facade import get_brain_facade"
                ))

            # Check for get_brain() calls without user_id
            if 'get_brain()' in line and 'def get_brain' not in line:
                violations.append(PolicyViolation(
                    severity="HIGH",
                    rule_name="brain_facade_usage",
                    file_path=filepath,
                    line_number=i,
                    description="get_brain() called without user_id parameter",
                    fix_suggestion="Change to: get_brain_facade(user_id=user_id)"
                ))

        return violations

    def _check_direct_db_writes(self, filepath: str, tree: ast.AST, content: str) -> List[PolicyViolation]:
        """Check for direct database write operations."""
        violations = []

        # Only check in certain directories where Brain facade should be used
        if not any(filepath.startswith(p) for p in ['app/', 'views/', 'components/']):
            return violations

        dangerous_patterns = [
            ('INSERT INTO', 'database insert'),
            ('UPDATE ', 'database update'),
            ('DELETE FROM', 'database delete'),
            ('db.execute', 'direct db.execute'),
            ('cursor.execute', 'direct cursor.execute')
        ]

        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue

            for pattern, desc in dangerous_patterns:
                if pattern in line.upper():
                    # Check if it's in a string (allowed)
                    if '"""' in line or "'''" in line or '"' + pattern.lower() in line.lower():
                        continue

                    violations.append(PolicyViolation(
                        severity="HIGH",
                        rule_name="direct_db_writes",
                        file_path=filepath,
                        line_number=i,
                        description=f"Direct {desc} detected - should use Brain facade",
                        fix_suggestion="Use appropriate Brain facade method (e.g., brain.create_customer, brain.update_job)"
                    ))

        return violations

    def _ai_analysis(self, filepath: str, content: str) -> List[PolicyViolation]:
        """
        Perform AI-enhanced analysis using DeepSeek.

        This provides deeper semantic analysis that static analysis might miss.
        """
        try:
            from tools.ai_code_reviewer import DeepSeekReviewer

            reviewer = DeepSeekReviewer(api_key=self.ai_api_key)
            result = reviewer.review_code(filepath, content)

            violations = []
            for v in result.get('violations', []):
                violations.append(PolicyViolation(
                    severity=v.get('severity', 'MEDIUM'),
                    rule_name=v.get('rule', 'ai_detected'),
                    file_path=filepath,
                    line_number=v.get('line', 0),
                    description=v.get('description', ''),
                    fix_suggestion=v.get('fix', '')
                ))

            return violations

        except Exception as e:
            logger.warning(f"AI analysis failed for {filepath}: {e}")
            return []

    def enforce_on_commit(self) -> bool:
        """
        Enforce policies on git commit.

        Returns:
            True if all checks pass, False if violations found
        """
        import subprocess

        try:
            # Get staged files
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
                capture_output=True,
                text=True,
                check=True
            )

            staged_files = [f for f in result.stdout.strip().split('\n')
                          if f.endswith('.py') and os.path.exists(f)]

            if not staged_files:
                return True

            all_violations = []
            for filepath in staged_files:
                violations = self.validate_file(filepath)
                all_violations.extend(violations)

            if all_violations:
                print("\n❌ COMMIT BLOCKED - Policy violations detected:\n")
                self._print_violations(all_violations)
                return False

            return True

        except subprocess.CalledProcessError:
            logger.error("Failed to get staged files")
            return False

    def _print_violations(self, violations: List[PolicyViolation]):
        """Print violations in a formatted way."""
        # Group by severity
        critical = [v for v in violations if v.severity == "CRITICAL"]
        high = [v for v in violations if v.severity == "HIGH"]
        medium = [v for v in violations if v.severity == "MEDIUM"]
        low = [v for v in violations if v.severity == "LOW"]

        for severity_name, vlist in [("CRITICAL", critical), ("HIGH", high), ("MEDIUM", medium), ("LOW", low)]:
            if vlist:
                print(f"\n{severity_name} ({len(vlist)}):")
                for v in vlist:
                    print(f"  {v.file_path}:{v.line_number} - {v.rule_name}")
                    print(f"    {v.description}")
                    print(f"    💡 {v.fix_suggestion}\n")


# Convenience function for use in pre-commit hooks
def enforce_on_commit(use_ai: bool = False) -> bool:
    """Run policy enforcement on staged files."""
    enforcer = AIPolicyEnforcer(use_ai=use_ai)
    return enforcer.enforce_on_commit()


if __name__ == '__main__':
    import sys

    use_ai = '--ai' in sys.argv or os.getenv('USE_AI_REVIEW') == '1'
    success = enforce_on_commit(use_ai=use_ai)
    sys.exit(0 if success else 1)
