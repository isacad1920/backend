#!/usr/bin/env python3
"""
Test runner script for SOFinance backend tests.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_tests(
    test_type: str = "all", 
    coverage: bool = False, 
    verbose: bool = False,
    pattern: str = None,
    marker: str = None
):
    """Run tests with specified parameters."""
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test directory based on type
    if test_type == "api":
        cmd.append("tests/api/")
    elif test_type == "unit":
        cmd.append("tests/unit/")
    elif test_type == "integration":
        cmd.append("tests/integration/")
    elif test_type == "all":
        cmd.append("tests/")
    else:
        print(f"Unknown test type: {test_type}")
        sys.exit(1)
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term-missing"])
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add pattern filter if provided
    if pattern:
        cmd.extend(["-k", pattern])
    
    # Add marker filter if provided  
    if marker:
        cmd.extend(["-m", marker])
    
    # Add other useful options
    cmd.extend([
        "--tb=short",  # Shorter traceback format
        "--strict-markers",  # Strict marker usage
        "-ra"  # Show all except passed
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 80)
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 130
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run SOFinance backend tests")
    
    parser.add_argument(
        "--type", 
        choices=["all", "api", "unit", "integration"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run with coverage reporting"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true", 
        help="Verbose output"
    )
    
    parser.add_argument(
        "--pattern", "-k",
        help="Run tests matching the given pattern"
    )
    
    parser.add_argument(
        "--marker", "-m", 
        help="Run tests with the given marker"
    )
    
    args = parser.parse_args()
    
    # Install test dependencies if needed without triggering unused import lint
    try:
        import importlib.util
        missing = []
        for mod in ("httpx", "pytest"):
            if importlib.util.find_spec(mod) is None:
                missing.append(mod)
        if missing:
            print(f"Installing test dependencies ({', '.join(missing)})...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"
            ], check=True)
    except Exception as e:  # pragma: no cover - defensive
        print(f"Warning: dependency check failed ({e}); attempting install anyway")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"
        ], check=True)
    
    return run_tests(
        test_type=args.type,
        coverage=args.coverage, 
        verbose=args.verbose,
        pattern=args.pattern,
        marker=args.marker
    )


if __name__ == "__main__":
    sys.exit(main())
