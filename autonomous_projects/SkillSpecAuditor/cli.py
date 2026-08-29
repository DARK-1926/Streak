"""
cli.py

CLI entry point for SkillSpecAuditor.
Isolates all file I/O, stdin ingestion, and argument parsing.
Orchestrates parsing, validation, routing, and execution via dependency injection.
Outputs structured JSON reports and adheres to strict exit code conventions.
"""

import argparse
import json
import os
import sys
from typing import Callable, List, Optional

from skill_spec import SkillDef, parse_manifest, validate_contract
from executor import ExecutionResult, execute_skill, subprocess_runner
from router import resolve_chain, verify_chain_compatibility


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(description="SkillSpecAuditor CLI")
    parser.add_argument("--manifest", required=True, help="Path to JSON manifest file")
    parser.add_argument("--entrypoint", required=True, help="Name of the entrypoint skill")
    parser.add_argument("--dry-run", action="store_true", help="Print chain plan and exit")
    return parser.parse_args(argv)


def _load_manifest(path: str) -> str:
    """Safely read manifest file contents with existence and size guards."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Manifest file not found: {path}")
    if os.path.getsize(path) == 0:
        raise ValueError(f"Manifest file is empty: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def _validate_skills(skills: List[SkillDef]) -> None:
    """Run contract validation against each parsed skill definition."""
    for skill in skills:
        errors = validate_contract(skill)
        if errors:
            raise ValueError(f"Contract validation failed for skill '{skill.name}': {errors}")


def _format_dry_run(chain: List[SkillDef]) -> None:
    """Build and print a JSON-serializable dry-run plan from the resolved chain."""
    plan = [
        {
            "name": s.name,
            "command": s.command,
            "stdin_type": s.stdin_type,
            "stdout_type": s.stdout_type,
        }
        for s in chain
    ]
    print(json.dumps({"status": "dry_run", "chain": plan}, indent=2))


def _execute_chain(chain: List[SkillDef], initial_payload: str, runner: Callable) -> List[ExecutionResult]:
    """Execute resolved skills sequentially, piping stdout to next stdin."""
    results: List[ExecutionResult] = []
    payload = initial_payload
    for skill in chain:
        result = execute_skill(skill, payload, runner)
        results.append(result)
        if not result.success:
            raise RuntimeError(f"Skill '{skill.name}' failed: {result.error_msg}")
        payload = result.stdout
    return results


def _print_report(report: dict) -> None:
    """Print a structured JSON report to standard output."""
    print(json.dumps(report, indent=2))


def main(argv: Optional[List[str]] = None) -> int:
    """
    CLI entry point orchestrating parsing, validation, routing, and execution.

    Args:
        argv: Optional list of command-line arguments for testing/injection.

    Returns:
        Exit code: 0 for success, 1 for validation error, 2 for execution error.
    """
    try:
        args = _parse_args(argv)
        raw_manifest = _load_manifest(args.manifest)
        skills = parse_manifest(raw_manifest)
        _validate_skills(skills)

        chain = resolve_chain(skills, args.entrypoint)
        verify_chain_compatibility(chain)

        if args.dry_run:
            _print_report(_format_dry_run(chain))
            return 0

        initial_payload = sys.stdin.read()
        execution_results = _execute_chain(chain, initial_payload, subprocess_runner)

        report = {
            "status": "success",
            "chain": [s.name for s in chain],
            "results": execution_results,
        }
        _print_report(report)
        return 0

    except (ValueError, FileNotFoundError, KeyError, TypeError) as exc:
        _print_report({"status": "validation_error", "error": str(exc)})
        return 1
    except Exception as exc:
        _print_report({"status": "execution_error", "error": str(exc)})
        return 2


if __name__ == "__main__":
    sys.exit(main())