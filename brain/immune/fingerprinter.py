"""
Semantic Fingerprinting for Crash Deduplication

Generates three levels of fingerprints for each crash:
1. EXACT: Full stack trace hash (catches identical crashes)
2. STRUCTURAL: Call chain without line numbers (catches similar crashes)
3. SEMANTIC: Error type + violated invariants (catches conceptually similar crashes)

This prevents the immune system from treating the same bug as multiple different bugs.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import hashlib
import re
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class CrashReport:
    """
    Represents a crash/error that occurred during command execution.

    This is the "pathogen" that the immune system will try to heal.
    """
    id: Optional[int] = None
    tool_name: str = ''
    error_type: str = ''
    error_message: str = ''
    traceback: str = ''
    command: str = ''
    context: Dict = field(default_factory=dict)
    violated_invariants: List = field(default_factory=list)
    fingerprint_exact: str = ''
    fingerprint_structural: str = ''
    fingerprint_semantic: str = ''

class SemanticFingerprinter:
    """
    Multi-level fingerprinting for accurate crash deduplication.

    Example:
        Crash 1: KeyError at app/pages/today.py:49
        Crash 2: KeyError at app/pages/calendar.py:120

        Both have DIFFERENT exact fingerprints (different line numbers)
        But SAME structural fingerprint (same call chain)
        And SAME semantic fingerprint (both are missing dictionary keys)

        The immune system will recognize Crash 2 as similar to Crash 1
        and apply the same patch without re-running AI synthesis.
    """

    @staticmethod
    def compute_fingerprint(crash_report: CrashReport) -> Dict[str, str]:
        """
        Generate all three fingerprint levels.

        Returns:
            Dict with keys: 'exact', 'structural', 'semantic'
        """
        return {'exact': SemanticFingerprinter._hash_exact(crash_report), 'structural': SemanticFingerprinter._hash_structural(crash_report), 'semantic': SemanticFingerprinter._hash_semantic(crash_report)}

    @staticmethod
    def _hash_exact(crash_report: CrashReport) -> str:
        """
        Level 1: Exact stack trace hash.

        This catches crashes that are EXACTLY the same:
        - Same file, same line, same error
        """
        trace_str = f'{crash_report.traceback}::{crash_report.error_message}'
        return hashlib.sha256(trace_str.encode()).hexdigest()[:16]

    @staticmethod
    def _hash_structural(crash_report: CrashReport) -> str:
        """
        Level 2: Call chain without line numbers.

        This catches crashes that are SIMILAR:
        - Same sequence of function calls
        - But maybe different line numbers (code was edited)

        Example:
            Traceback:
              File "app.py", line 100, in main
              File "brain.py", line 200, in execute
              File "tool.py", line 50, in run

            Structural fingerprint: "main->execute->run"
        """
        call_chain = []
        pattern = 'in (\\w+)'
        matches = re.findall(pattern, crash_report.traceback)
        call_chain = matches if matches else ['unknown']
        chain_str = '->'.join(call_chain)
        return hashlib.sha256(chain_str.encode()).hexdigest()[:16]

    @staticmethod
    def _hash_semantic(crash_report: CrashReport) -> str:
        """
        Level 3: Error type + violated invariants.

        This catches crashes that are CONCEPTUALLY similar:
        - Same type of error (KeyError, TypeError, etc.)
        - Same business rule violated
        - But maybe in different locations

        Example:
            Crash 1: KeyError accessing dictionary key 'soon_2h' in today.py
            Crash 2: KeyError accessing dictionary key 'user_id' in calendar.py

            Both have semantic fingerprint: "KeyError:missing_key"
        """
        signature_parts = [crash_report.error_type, crash_report.tool_name]
        if crash_report.violated_invariants:
            invariant_names = sorted([str(inv) if isinstance(inv, str) else inv.get('name', 'unknown') for inv in crash_report.violated_invariants])
            signature_parts.extend(invariant_names)
        semantic_signature = ':'.join(signature_parts)
        return hashlib.sha256(semantic_signature.encode()).hexdigest()[:16]

    @staticmethod
    def compute_and_update(crash_report: CrashReport) -> CrashReport:
        """
        Convenience method: Compute fingerprints and update the crash report.

        Usage:
            crash = CrashReport(...)
            crash = SemanticFingerprinter.compute_and_update(crash)
            # Now crash.fingerprint_exact, etc. are populated
        """
        fingerprints = SemanticFingerprinter.compute_fingerprint(crash_report)
        crash_report.fingerprint_exact = fingerprints.get('exact', 0)
        crash_report.fingerprint_structural = fingerprints.get('structural', 0)
        crash_report.fingerprint_semantic = fingerprints.get('semantic', 0)
        return crash_report
if __name__ == '__main__':
    crash = CrashReport(tool_name='compute_reminders', error_type='KeyError', error_message="'soon_2h'", traceback='\nTraceback (most recent call last):\n  File "app/pages/today.py", line 49, in render_today\n    if rem["soon_2h"]:\nKeyError: \'soon_2h\'\n        ', command='show_today_page', violated_invariants=['missing_dictionary_key'])
    crash = SemanticFingerprinter.compute_and_update(crash)
    print(f'Exact fingerprint:      {crash.fingerprint_exact}')
    print(f'Structural fingerprint: {crash.fingerprint_structural}')
    print(f'Semantic fingerprint:   {crash.fingerprint_semantic}')