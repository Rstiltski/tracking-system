"""
MetaBrain - The Orchestrator

This is the master controller that coordinates all meta-brains
to perform self-repair and self-check operations.

The MetaBrain facilitates the collaboration between LLM and brain system:
LLM WORK → SCAN → DIAGNOSE → REPAIR → TEST → VALIDATE → REPEAT (by LLM)

Where:
- LLM does the actual work (scanning, diagnosing, repairing)
- Brain system supervises, validates, and ensures quality of LLM's work

Usage:
    from brain.brains.meta_brain import MetaBrain

    meta = MetaBrain()
    meta.self_repair()  # Run until all tests pass
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from brain.nervous_system import NervousSystem, get_nervous_system
from brain.brains.scanner_brain import ScannerBrain, ScanResult
from brain.brains.diagnosis_brain import DiagnosisBrain, Diagnosis, FixPlan
from brain.brains.repair_brain import RepairBrain, RepairResult
from brain.brains.test_brain import TestBrain, TestResult, Comparison
from brain.brains.validator_brain import ValidatorBrain, ValidationResult
from brain.brains.docs_brain import DocsBrain, DocsSyncReport


@dataclass
class RepairCycleResult:
    """Result of one repair cycle"""
    cycle_number: int
    before_rate: int
    after_rate: int
    error_fixed: Optional[str]
    action_taken: str
    success: bool
    continue_loop: bool


@dataclass
class SelfRepairReport:
    """Final report after self-repair completes"""
    total_cycles: int
    starting_rate: int
    final_rate: int
    errors_fixed: int
    complete: bool
    cycle_history: List[RepairCycleResult]


class MetaBrain:
    """
    Master Orchestrator - Controls all meta-brains

    Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                       META BRAIN                             │
    │                    (The Orchestrator)                        │
    ├─────────────────────────────────────────────────────────────┤
    │                                                              │
    │  LLM → ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐    │
    │        │ Scanner │ → │Diagnosis│ → │ Repair  │ → │  Test   │    │
    │        │  Brain  │   │  Brain  │   │  Brain  │   │  Brain  │    │
    │        └─────────┘   └─────────┘   └─────────┘   └─────────┘    │
    │             ↑                                          ↓          │
    │             │         ┌─────────┐   ┌─────────┐       │          │
    │             └─────────│Validator│ ← │  Docs   │←──────┘          │
    │                       │  Brain  │   │  Brain  │                   │
    │                       └─────────┘   └─────────┘                   │
    │                                                                  │
    │  LLM does actual work; Brain system supervises and validates     │
    └─────────────────────────────────────────────────────────────────┘

    The Loop:
    1. LLM uses ScannerBrain to find errors
    2. LLM uses DiagnosisBrain to analyze first error
    3. LLM uses RepairBrain to fix ONE error
    4. TestBrain runs tests
    5. ValidatorBrain checks for regression and validates LLM's work
    6. If not 100%, LLM repeats the loop from step 1
    """

    def __init__(self, nervous_system: Optional[NervousSystem] = None,
                 max_cycles: int = 50):
        self.nervous_system = nervous_system or get_nervous_system()
        self.max_cycles = max_cycles

        # Initialize all meta-brains
        self.scanner = ScannerBrain(self.nervous_system)
        self.diagnosis = DiagnosisBrain(self.nervous_system)
        self.repair = RepairBrain(self.nervous_system)
        self.test = TestBrain(self.nervous_system)
        self.validator = ValidatorBrain(self.nervous_system)
        self.docs = DocsBrain(self.nervous_system)

        self.cycle_history: List[RepairCycleResult] = []

    def self_repair(self, verbose: bool = True) -> SelfRepairReport:
        """
        Run the self-repair loop until all tests pass.

        Args:
            verbose: Print progress to console

        Returns:
            SelfRepairReport with complete history
        """
        if verbose:
            print("=" * 60)
            print("SELF-REPAIR INITIATED")
            print("=" * 60)

        # Initial scan
        scan_result = self.scanner.scan()
        starting_rate = scan_result.pass_rate

        if verbose:
            print(f"\nStarting pass rate: {starting_rate}%")
            print(f"Failed tests: {scan_result.failed}")

        if scan_result.pass_rate == 100:
            if verbose:
                print("\nAll tests already passing!")
            return SelfRepairReport(
                total_cycles=0,
                starting_rate=starting_rate,
                final_rate=100,
                errors_fixed=0,
                complete=True,
                cycle_history=[]
            )

        # Run repair cycles
        cycle = 0
        current_rate = starting_rate
        errors_fixed = 0

        while cycle < self.max_cycles and current_rate < 100:
            cycle += 1

            if verbose:
                print(f"\n{'=' * 40}")
                print(f"CYCLE {cycle}")
                print(f"{'=' * 40}")

            cycle_result = self._run_one_cycle(cycle, current_rate, verbose)
            self.cycle_history.append(cycle_result)

            if cycle_result.success:
                errors_fixed += 1

            current_rate = cycle_result.after_rate

            if not cycle_result.continue_loop:
                break

        # Final report
        final_result = self.test.run_tests()

        if verbose:
            print("\n" + "=" * 60)
            print("SELF-REPAIR COMPLETE")
            print("=" * 60)
            print(f"Cycles run: {cycle}")
            print(f"Starting rate: {starting_rate}%")
            print(f"Final rate: {final_result.pass_rate}%")
            print(f"Errors fixed: {errors_fixed}")

            if final_result.all_passed:
                print("\nALL TESTS PASSING!")
            else:
                print(f"\nRemaining failures: {final_result.failed}")

        return SelfRepairReport(
            total_cycles=cycle,
            starting_rate=starting_rate,
            final_rate=final_result.pass_rate,
            errors_fixed=errors_fixed,
            complete=final_result.all_passed,
            cycle_history=self.cycle_history
        )

    def _run_one_cycle(self, cycle_num: int, before_rate: int,
                       verbose: bool) -> RepairCycleResult:
        """Run one repair cycle"""
        # Step 1: Scan for errors
        scan_result = self.scanner.scan()

        if scan_result.pass_rate == 100:
            return RepairCycleResult(
                cycle_number=cycle_num,
                before_rate=before_rate,
                after_rate=100,
                error_fixed=None,
                action_taken="All tests passing",
                success=True,
                continue_loop=False
            )

        if not scan_result.first_error:
            return RepairCycleResult(
                cycle_number=cycle_num,
                before_rate=before_rate,
                after_rate=scan_result.pass_rate,
                error_fixed=None,
                action_taken="No errors found but tests still failing",
                success=False,
                continue_loop=False
            )

        # Step 2: Diagnose first error
        fix_plan = self.diagnosis.diagnose(scan_result.errors)
        first_diagnosis = self.diagnosis.get_first_fix(fix_plan)

        if verbose:
            print(f"\nError: {first_diagnosis.error_type}")
            print(f"Root cause: {first_diagnosis.root_cause}")
            print(f"Fix strategy: {first_diagnosis.fix_strategy}")

        # Step 3: Attempt repair
        repair_result = self.repair.repair(first_diagnosis)

        if verbose:
            print(f"\nAction: {repair_result.action_taken[:100]}")

        # Step 4: Test
        test_result = self.test.run_tests()

        # Step 5: Validate
        comparison = self.test.compare(
            TestResult(17, int(17 * before_rate / 100), 17 - int(17 * before_rate / 100),
                      before_rate, False, [], ""),
            test_result
        )

        validation = self.validator.validate(comparison)

        if verbose:
            print(f"\nResult: {validation.reason}")
            print(f"Pass rate: {before_rate}% → {test_result.pass_rate}%")

        return RepairCycleResult(
            cycle_number=cycle_num,
            before_rate=before_rate,
            after_rate=test_result.pass_rate,
            error_fixed=first_diagnosis.error_type if repair_result.success else None,
            action_taken=repair_result.action_taken[:200],
            success=repair_result.success and validation.approved,
            continue_loop=not test_result.all_passed and validation.approved
        )

    def run_one_fix(self, verbose: bool = True) -> RepairCycleResult:
        """
        Run just ONE fix cycle (not the full loop).

        Useful for step-by-step repair.
        """
        scan_result = self.scanner.scan()
        before_rate = scan_result.pass_rate

        return self._run_one_cycle(1, before_rate, verbose)

    def get_status(self) -> str:
        """Get current system status"""
        test_result = self.test.run_tests()
        docs_status = self.docs.check_sync_status()

        status = f"""
## System Status

### Tests
- Pass Rate: {test_result.pass_rate}%
- Passed: {test_result.passed}/{test_result.total_tests}
- Status: {"COMPLETE" if test_result.all_passed else "NEEDS REPAIR"}

### Documentation
- Total MD files: {docs_status.total_docs}
- Root docs: {docs_status.root_docs}
- Out of sync: {len(docs_status.out_of_sync)}

### Brains
- Domain brains: 3 (Ops, Finance, Relation)
- Meta brains: 6 (Scanner, Diagnosis, Repair, Test, Validator, Docs)
- Total: 9 brains
"""
        return status

    def check_docs(self) -> DocsSyncReport:
        """Check documentation sync status"""
        return self.docs.check_sync_status()


# Convenience functions
def self_repair(verbose: bool = True) -> SelfRepairReport:
    """Run self-repair loop"""
    meta = MetaBrain()
    return meta.self_repair(verbose)


def fix_one_error(verbose: bool = True) -> RepairCycleResult:
    """Fix just one error"""
    meta = MetaBrain()
    return meta.run_one_fix(verbose)


def get_system_status() -> str:
    """Get system status"""
    meta = MetaBrain()
    return meta.get_status()
