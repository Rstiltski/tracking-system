"""
Brain Architecture - Domain Brains + Meta Brains

DOMAIN BRAINS (handle business logic):
- OpsBrain: Jobs, scheduling, crew, materials
- FinanceBrain: Invoices, payments, quotes
- RelationBrain: Customers, communications, portal

META BRAINS (handle self-repair and self-check):
- ScannerBrain: Finds errors in code
- DiagnosisBrain: Analyzes errors, determines root cause
- RepairBrain: Fixes one error at a time
- TestBrain: Runs tests, interprets results
- ValidatorBrain: Confirms fixes, guards against regression
- DocsBrain: Keeps documentation in sync
- MetaBrain: Orchestrates all meta-brains for self-repair

Usage:
    # Domain brains (for business operations)
    from brain.brains import OpsBrain, FinanceBrain, RelationBrain

    # Meta brains (for self-repair)
    from brain.brains import MetaBrain
    meta = MetaBrain()
    meta.self_repair()  # Fix all errors

    # Or fix one error at a time
    from brain.brains import fix_one_error
    result = fix_one_error()
"""

# Domain Brains
from brain.brains.ops_brain import OpsBrain
from brain.brains.finance_brain import FinanceBrain
from brain.brains.relation_brain import RelationBrain

# Meta Brains
from brain.brains.scanner_brain import ScannerBrain, scan_for_errors
from brain.brains.diagnosis_brain import DiagnosisBrain, diagnose_errors
from brain.brains.repair_brain import RepairBrain, repair_error, install_missing_package
from brain.brains.test_brain import TestBrain, run_all_tests, verify_fix_worked
from brain.brains.validator_brain import ValidatorBrain, validate_fix
from brain.brains.docs_brain import DocsBrain, check_docs, list_all_brains
from brain.brains.meta_brain import MetaBrain, self_repair, fix_one_error, get_system_status

__all__ = [
    # Domain Brains
    "OpsBrain",
    "FinanceBrain",
    "RelationBrain",

    # Meta Brains
    "ScannerBrain",
    "DiagnosisBrain",
    "RepairBrain",
    "TestBrain",
    "ValidatorBrain",
    "DocsBrain",
    "MetaBrain",

    # Convenience functions
    "scan_for_errors",
    "diagnose_errors",
    "repair_error",
    "install_missing_package",
    "run_all_tests",
    "verify_fix_worked",
    "validate_fix",
    "check_docs",
    "list_all_brains",
    "self_repair",
    "fix_one_error",
    "get_system_status",
]
