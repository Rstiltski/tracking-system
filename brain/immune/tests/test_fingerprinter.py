"""
Test Fingerprinter

📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import pytest

from brain.immune.fingerprinter import SemanticFingerprinter, CrashReport


def test_exact_fingerprint_uniqueness():
    """Different crashes should have different exact fingerprints."""
    crash1 = CrashReport(
        traceback="File 'a.py', line 10",
        error_message="Error 1"
    )
    crash2 = CrashReport(
        traceback="File 'a.py', line 20",  # Different line
        error_message="Error 1"
    )

    fp1 = SemanticFingerprinter._hash_exact(crash1)
    fp2 = SemanticFingerprinter._hash_exact(crash2)

    assert fp1 != fp2, "Different crashes should have different exact fingerprints"


def test_structural_fingerprint_similarity():
    """Same call chain should have same structural fingerprint."""
    crash1 = CrashReport(
        traceback='''
        File "app.py", line 100, in main
        File "brain.py", line 200, in execute
        '''
    )
    crash2 = CrashReport(
        traceback='''
        File "app.py", line 105, in main
        File "brain.py", line 210, in execute
        '''  # Same functions, different lines
    )

    fp1 = SemanticFingerprinter._hash_structural(crash1)
    fp2 = SemanticFingerprinter._hash_structural(crash2)

    assert fp1 == fp2, "Same call chain should have same structural fingerprint"


def test_semantic_fingerprint_conceptual_similarity():
    """Same error type + invariant should have same semantic fingerprint."""
    crash1 = CrashReport(
        error_type="KeyError",
        tool_name="compute_reminders",
        violated_invariants=["missing_key"]
    )
    crash2 = CrashReport(
        error_type="KeyError",
        tool_name="compute_reminders",
        violated_invariants=["missing_key"]
    )

    fp1 = SemanticFingerprinter._hash_semantic(crash1)
    fp2 = SemanticFingerprinter._hash_semantic(crash2)

    assert fp1 == fp2, "Conceptually similar crashes should have same semantic fingerprint"


def test_compute_and_update():
    """compute_and_update should populate all three fingerprints."""
    crash = CrashReport(
        tool_name="test_tool",
        error_type="TestError",
        traceback="File 'test.py', line 1, in test"
    )

    crash = SemanticFingerprinter.compute_and_update(crash)

    assert len(crash.fingerprint_exact) == 16
    assert len(crash.fingerprint_structural) == 16
    assert len(crash.fingerprint_semantic) == 16
