#!/usr/bin/env python3
"""
Wrapper script for running CodeGuard tests.
Checks for dependency files, runs pytest on test_codeguard.py,
and provides a fallback if the test file is missing.
"""

import os
import sys
import subprocess
import time
from typing import NoReturn

def check_dependency_files() -> None:
    """
    Verify that at least one of the required dependency files exists.
    If neither requirements.txt nor package.json is present, exit with code 9009.
    """
    if not (os.path.exists('requirements.txt') or os.path.exists('package.json')):
        sys.exit(9009)

def fallback_start_codeguard() -> None:
    """
    Optional fallback: if test_codeguard.py does not exist, start codeguard.py
    for 5 seconds and then terminate it.
    """
    try:
        # Start codeguard.py as a subprocess
        proc = subprocess.Popen([sys.executable, 'codeguard.py'])
        # Wait for the specified timeout
        time.sleep(5)
        # Terminate the process gracefully
        proc.terminate()
        # Wait for the process to finish (with a short timeout)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # If it doesn't terminate, force kill
            proc.kill()
            proc.wait()
    except Exception as e:
        # If anything goes wrong, we simply continue; the script will exit with 0
        # as per the optional fallback semantics.
        sys.stderr.write(f'Warning: fallback failed: {e}\\n')

def run_pytest() -> int:
    """
    Execute pytest on the test_codeguard.py file and return the exit code.
    """
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'test_codeguard.py', '-v']
    )
    return result.returncode

def exit_with_code(code: int) -> NoReturn:
    """
    Helper to exit the script with the given code.
    """
    sys.exit(code)

def main() -> None:
    # Step 2: Ensure dependency files exist
    check_dependency_files()

    # Step 5: Optional fallback if test file is missing
    if not os.path.exists('test_codeguard.py'):
        fallback_start_codeguard()
        # After the fallback, we consider the script's job done.
        exit_with_code(0)

    # Step 3: Run pytest on the test file
    pytest_exit_code = run_pytest()

    # Step 4: Handle pytest result
    if pytest_exit_code != 0:
        # According to the specification, exit with code 1 (or 9009).
        # We choose 1 for test failures.
        exit_with_code(1)
    else:
        exit_with_code(0)

if __name__ == '__main__':
    main()