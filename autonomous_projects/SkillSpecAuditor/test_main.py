import unittest
import json
import io
import sys
from typing import List, Tuple, Callable

import skill_spec
import executor
import router
import cli

from skill_spec import SkillDef, parse_manifest, validate_contract
from executor import ExecutionResult, execute_skill, subprocess_runner
from router import resolve_chain, verify_chain_compatibility
from cli import _format_dry_run, _execute_chain, _print_report, main


def fake_runner(cmd: str, payload: str) -> Tuple[int, str, str]:
    """Pure Python fake runner for deterministic testing."""
    return (0, f'processed:{payload}', '')


def failing_runner(cmd: str, payload: str) -> Tuple[int, str, str]:
    """Runner that simulates a command failure."""
    return (1, '', 'simulated error')


class TestSkillSpecParsing(unittest.TestCase):
    """Tests for manifest parsing and contract validation."""

    def test_parse_manifest_valid(self) -> None:
        """Verify parsing of a well-formed JSON manifest string."""
        raw_json = json.dumps([{
            "name": "extract",
            "command": "run_extract",
            "stdin_type": "raw_text",
            "stdout_type": "structured_json",
            "description": "Extracts data"
        }])
        skills = parse_manifest(raw_json)
        self.assertEqual(len(skills), 1)
        self.assertIsInstance(skills[0], SkillDef)
        self.assertEqual(skills[0].name, "extract")
        self.assertEqual(skills[0].stdin_type, "raw_text")

    def test_parse_manifest_invalid(self) -> None:
        """Verify exception raising on malformed JSON or missing fields."""
        malformed_json = '{invalid_json_structure'
        with self.assertRaises((ValueError, json.JSONDecodeError, TypeError)):
            parse_manifest(malformed_json)

    def test_validate_contract(self) -> None:
        """Verify error detection for invalid skill definitions."""
        invalid_skill = SkillDef(
            name="",
            command="run",
            stdin_type="",
            stdout_type="out",
            description="Invalid"
        )
        errors = validate_contract(invalid_skill)
        self.assertIsInstance(errors, list)
        self.assertGreater(len(errors), 0)


class TestExecutor(unittest.TestCase):
    """Tests for skill execution with injected runners."""

    def test_execute_skill_success(self) -> None:
        """Verify successful execution returns correct ExecutionResult."""
        skill = SkillDef(
            name="transform",
            command="run_transform",
            stdin_type="json",
            stdout_type="csv",
            description="Transforms data"
        )
        result = execute_skill(skill, '{"key": "val"}', fake_runner)
        self.assertIsInstance(result, ExecutionResult)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, 'processed:{"key": "val"}')
        self.assertEqual(result.stderr, '')

    def test_execute_skill_failure(self) -> None:
        """Verify failure handling when runner returns non-zero exit code."""
        skill = SkillDef(
            name="fail_skill",
            command="run_fail",
            stdin_type="text",
            stdout_type="text",
            description="Fails intentionally"
        )
        result = execute_skill(skill, "input_data", failing_runner)
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.stderr, 'simulated error')


class TestRouter(unittest.TestCase):
    """Tests for chain resolution and compatibility verification."""

    def _make_skills(self) -> List[SkillDef]:
        """Helper to create a standard set of skills for routing tests."""
        return [
            SkillDef("A", "cmd_a", "text", "json", "Step A"),
            SkillDef("B", "cmd_b", "json", "xml", "Step B"),
            SkillDef("C", "cmd_c", "xml", "csv", "Step C"),
            SkillDef("D", "cmd_d", "binary", "image", "Step D")
        ]

    def test_resolve_chain_linear(self) -> None:
        """Verify linear chain resolution matches I/O types correctly."""
        skills = self._make_skills()
        chain = resolve_chain(skills, "text", "csv")
        self.assertEqual(len(chain), 3)
        self.assertEqual([s.name for s in chain], ["A", "B", "C"])

    def test_resolve_chain_none_handling(self) -> None:
        """Verify empty list returned when no valid chain exists."""
        skills = self._make_skills()
        chain = resolve_chain(skills, "text", "image")
        self.assertEqual(chain, [])

    def test_resolve_chain_cycle_detection(self) -> None:
        """Verify graceful handling of cyclic skill dependencies."""
        cyclic_skills = [
            SkillDef("X", "cmd_x", "alpha", "beta", "X"),
            SkillDef("Y", "cmd_y", "beta", "alpha", "Y")
        ]
        chain = resolve_chain(cyclic_skills, "alpha", "alpha")
        self.assertIsInstance(chain, list)

    def test_verify_chain_compatibility(self) -> None:
        """Verify detection of I/O type mismatches in a proposed chain."""
        mismatched_chain = [
            SkillDef("P", "cmd_p", "text", "json", "P"),
            SkillDef("Q", "cmd_q", "xml", "csv", "Q")
        ]
        errors = verify_chain_compatibility(mismatched_chain)
        self.assertIsInstance(errors, list)
        self.assertGreater(len(errors), 0)


class TestCLI(unittest.TestCase):
    """Tests for CLI wiring and reporting."""

    def test_cli_dry_run(self) -> None:
        """Verify dry-run output is valid JSON with expected structure."""
        chain = [
            SkillDef("dry_a", "cmd_a", "in", "mid", "Dry A"),
            SkillDef("dry_b", "cmd_b", "mid", "out", "Dry B")
        ]
        captured = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured
            _format_dry_run(chain)
        finally:
            sys.stdout = old_stdout

        output_str = captured.getvalue().strip()
        report_data = json.loads(output_str)
        self.assertIn("chain", report_data)
        self.assertIn("status", report_data)
        self.assertEqual(report_data["status"], "dry_run")

    def test_full_chain_execution(self) -> None:
        """Verify payload piping across multiple skills deterministically."""
        chain = [
            SkillDef("pipe_1", "cmd_1", "raw", "step1", "Pipe 1"),
            SkillDef("pipe_2", "cmd_2", "step1", "step2", "Pipe 2")
        ]
        results = _execute_chain(chain, "initial_payload", fake_runner)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].exit_code, 0)
        self.assertEqual(results[0].stdout, "processed:initial_payload")
        self.assertEqual(results[1].stdout, "processed:processed:initial_payload")


if __name__ == '__main__':
    unittest.main()