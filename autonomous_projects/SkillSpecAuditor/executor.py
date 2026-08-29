"""
executor.py

Dependency Injection-based execution engine for SkillSpecAuditor.
Provides a pure core logic function for running skills with an injected runner,
isolating side-effects to the runner implementation. Includes a default
subprocess-based runner for production use.
"""

import subprocess
from dataclasses import dataclass
from typing import Callable, List, Tuple

from skill_spec import SkillDef


@dataclass(frozen=True)
class ExecutionResult:
    """
    Immutable data model representing the outcome of a skill execution.

    Attributes:
        exit_code: The POSIX exit code returned by the process.
        stdout: The standard output captured from the process.
        stderr: The standard error captured from the process.
        success: Boolean flag indicating if the execution was successful.
        error_msg: Descriptive message for failures or exceptions, empty on success.
    """
    exit_code: int
    stdout: str
    stderr: str
    success: bool
    error_msg: str = ""


def execute_skill(
    skill: SkillDef,
    payload: str,
    runner: Callable[[List[str], str], Tuple[int, str, str]]
) -> ExecutionResult:
    """
    Execute a skill using the provided dependency-injected runner.

    This function contains pure orchestration logic. It delegates the actual
    process execution to the injected `runner`, handles exceptions gracefully,
    and validates the exit code against the skill's allowed exit codes.

    Args:
        skill: The SkillDef instance containing command and validation rules.
        payload: The string payload to be passed to the skill's stdin.
        runner: A callable that executes the command with the payload and
                returns a tuple of (exit_code, stdout, stderr).

    Returns:
        An ExecutionResult instance detailing the outcome of the execution.
    """
    try:
        exit_code, stdout, stderr = runner(skill.command, payload)
    except Exception as exc:
        return ExecutionResult(
            exit_code=-1,
            stdout="",
            stderr="",
            success=False,
            error_msg=f"Runner execution failed: {exc}"
        )

    is_success = exit_code in skill.allowed_exit_codes
    error_msg = "" if is_success else (
        f"Exit code {exit_code} not in allowed codes: {skill.allowed_exit_codes}"
    )

    return ExecutionResult(
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        success=is_success,
        error_msg=error_msg
    )


def subprocess_runner(cmd: List[str], payload: str) -> Tuple[int, str, str]:
    """
    Default runner implementation using Python's subprocess module.

    Executes the command list safely without shell invocation, capturing
    stdout and stderr. Designed for cross-platform compatibility, including
    Windows, by avoiding shell=True and passing commands as lists.

    Args:
        cmd: A list of strings representing the executable and its arguments.
        payload: The string data to be written to the subprocess stdin.

    Returns:
        A tuple containing (exit_code, stdout, stderr).

    Raises:
        subprocess.TimeoutExpired: If the process exceeds the 30-second timeout.
        RuntimeError: For any other subprocess-related failures.
    """
    try:
        process = subprocess.run(
            cmd,
            input=payload,
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )
        return process.returncode, process.stdout, process.stderr
    except subprocess.TimeoutExpired as exc:
        raise subprocess.TimeoutExpired(cmd, 30) from exc
    except Exception as exc:
        raise RuntimeError(f"Subprocess execution failed for cmd {cmd}: {exc}") from exc