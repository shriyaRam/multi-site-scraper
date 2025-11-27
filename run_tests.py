# run_tests.py
"""
Simple test runner for the entire test suite.
Runs pytest programmatically and prints a clean summary.
"""

import pytest
import sys

def main():
    print("Running test suite...\n")

    # Run pytest for the entire tests/ directory
    result = pytest.main([
        "tests",        # directory to run
        "-q",           # quiet: fewer logs
        "--disable-warnings",
        "--maxfail=1"   # stop early if on error
    ])

    print("\nTest execution completed.")
    
    # pytest exit codes
    if result == 0:
        print("RESULT: All tests passed successfully.")
    elif result == 1:
        print("RESULT: Tests failed.")
    elif result == 2:
        print("RESULT: Pytest execution interrupted.")
    elif result == 3:
        print("RESULT: Internal pytest error.")
    elif result == 4:
        print("RESULT: pytest command line usage error.")
    else:
        print(f"RESULT: Unknown exit code: {result}")

    sys.exit(result)


if __name__ == "__main__":
    main()