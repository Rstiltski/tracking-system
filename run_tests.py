#!/usr/bin/env python3
"""
Test Runner Script for Tracking System

Provides a convenient CLI for running tests with various options.
Follows testing best practices from PHASE_4_NOTIFICATIONS.md.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run unit tests only
    python run_tests.py --integration      # Run integration tests only
    python run_tests.py --edge             # Run edge case tests only
    python run_tests.py --coverage         # Run with coverage report
    python run_tests.py --watch            # Run in watch mode
    python run_tests.py --file=test_notification_engine.py  # Specific file
    python run_tests.py --help             # Show help
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path


# Colors for terminal output
class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def check_dependencies():
    """Check if required dependencies are installed."""
    required = ['pytest']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print_error(f"Missing dependencies: {', '.join(missing)}")
        print_info("Install with: pip install pytest pytest-cov")
        return False
    
    return True


def run_tests(args):
    """Run pytest with the specified arguments."""
    # Build pytest command
    cmd = [sys.executable, '-m', 'pytest']
    
    # Add verbosity
    if not args.quiet:
        cmd.append('-v')
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend(['--cov=brain', '--cov-report=term-missing'])
        if args.coverage_html:
            cmd.append('--cov-report=html')
    
    # Add specific test file/pattern
    if args.file:
        cmd.append(f"tests/{args.file}")
    elif args.unit:
        cmd.extend(['-m', 'not integration', 'tests/'])
    elif args.integration:
        cmd.extend(['-m', 'integration', 'tests/'])
    elif args.edge:
        cmd.extend(['-m', 'edge_case', 'tests/'])
    else:
        cmd.append('tests/')
    
    # Add specific test class or function
    if args.klass:
        cmd.append(f"::{args.klass}")
    if args.function:
        cmd.append(f"::{args.function}")
    
    # Add watch mode
    if args.watch:
        try:
            import pytest_watch
            cmd = ['ptw'] + cmd[2:]  # Replace pytest with ptw
        except ImportError:
            print_info("pytest-watch not installed. Install with: pip install pytest-watch")
    
    # Add stop-on-first-failure
    if args.stop:
        cmd.append('-x')
    
    # Add fail-fast after N failures
    if args.maxfail:
        cmd.append(f'--maxfail={args.maxfail}')
    
    # Add number of workers (parallel execution)
    if args.numworkers:
        try:
            import xdist
            cmd.append(f'-n={args.numworkers}')
        except ImportError:
            print_info("pytest-xdist not installed. Install with: pip install pytest-xdist")
    
    # Add custom markers
    if args.marker:
        cmd.extend(['-m', args.marker])
    
    # Add output file
    if args.output:
        cmd.append(f'--html={args.output}')
    
    # Add quiet mode
    if args.quiet:
        cmd.append('-q')
    
    # Run the command
    print_header("Running Tests")
    print_info(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0:
            print_success("All tests passed!")
        else:
            print_error(f"Tests failed with exit code {result.returncode}")
        
        return result.returncode
    
    except KeyboardInterrupt:
        print("\n")
        print_info("Tests interrupted by user")
        return 1
    except Exception as e:
        print_error(f"Error running tests: {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run tests for the Tracking System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                     Run all tests
  python run_tests.py --coverage          Run with coverage report
  python run_tests.py --unit              Run unit tests only
  python run_tests.py --integration       Run integration tests only
  python run_tests.py --edge              Run edge case tests only
  python run_tests.py --file=test_notification_engine.py
  python run_tests.py --marker=edge_case
  python run_tests.py --watch             Watch mode (auto-rerun on changes)
        """
    )
    
    # Test selection
    parser.add_argument('--unit', action='store_true',
                        help='Run unit tests only (exclude integration)')
    parser.add_argument('--integration', action='store_true',
                        help='Run integration tests only')
    parser.add_argument('--edge', action='store_true',
                        help='Run edge case tests only')
    parser.add_argument('--file', type=str,
                        help='Run specific test file (e.g., test_notification_engine.py)')
    parser.add_argument('--klass', type=str,
                        help='Run specific test class (e.g., TestNotificationDispatch)')
    parser.add_argument('--function', type=str,
                        help='Run specific test function (e.g., test_dispatch_basic)')
    parser.add_argument('--marker', '-m', type=str,
                        help='Run tests with specific marker')
    
    # Output options
    parser.add_argument('--coverage', action='store_true',
                        help='Generate coverage report')
    parser.add_argument('--coverage-html', action='store_true',
                        help='Generate HTML coverage report (requires --coverage)')
    parser.add_argument('--output', type=str,
                        help='Generate HTML report (requires pytest-html)')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Quiet mode (less output)')
    
    # Execution options
    parser.add_argument('--watch', action='store_true',
                        help='Watch mode (auto-rerun on file changes)')
    parser.add_argument('--stop', '-x', action='store_true',
                        help='Stop after first failure')
    parser.add_argument('--maxfail', type=int,
                        help='Stop after N failures')
    parser.add_argument('--numworkers', '-n', type=str,
                        help='Number of parallel workers (e.g., auto, 4)')
    
    # Other
    parser.add_argument('--check-deps', action='store_true',
                        help='Check dependencies only')
    
    args = parser.parse_args()
    
    # Check dependencies
    if args.check_deps:
        if check_dependencies():
            print_success("All dependencies installed")
            return 0
        else:
            return 1
    
    # Run tests
    return run_tests(args)


if __name__ == '__main__':
    sys.exit(main())
