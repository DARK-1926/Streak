import json
import os
import subprocess
import sys
import tempfile
import unittest
from typing import Any, Dict, List

from core import LeakReport, LeakSignature, detect_leaks
from patterns import scan_redundancy
from simulator import SimulationResult, run_budget_simulation
from parser import parse_log_stream


class TestContextLeakAuditor(unittest.TestCase):
    """Comprehensive test suite for ContextLeakAuditor core modules."""

    def test_parser_stream(self) -> None:
        """Test parsing of valid, invalid, and empty JSONL lines."""
        lines: List[str] = [
            '{"step": 1, "context_size": 100}',
            'not valid json',
            '',
            '   ',
            '{"step": 2, "tokens": 50}'
        ]
        result: List[Dict[str, Any]] = list(parse_log_stream(lines))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["step"], 1)
        self.assertEqual(result[0]["context_size"], 100)
        self.assertEqual(result[1]["step"], 2)
        self.assertEqual(result[1]["tokens"], 50)

    def test_pattern_scanner(self) -> None:
        """Test redundancy detection with duplicate system prompts."""
        payload: str = "duplicate system prompt text for testing redundancy"
        events: List[Dict[str, Any]] = [
            {"step": i, "system": payload} for i in range(1, 7)
        ]
        sigs: List[LeakSignature] = scan_redundancy(events)
        self.assertEqual(len(sigs), 5)
        self.assertTrue(all(s.type == "redundant_injection" for s in sigs))
        self.assertEqual(sigs[0].severity, "low")
        self.assertEqual(sigs[1].severity, "medium")
        self.assertEqual(sigs[2].severity, "medium")
        self.assertEqual(sigs[3].severity, "high")
        self.assertEqual(sigs[4].severity, "high")
        self.assertTrue(all(s.tokens_wasted > 0 for s in sigs))

    def test_leak_detector_single_pass(self) -> None:
        """Test single-pass leak detection with monotonic growth and overflow."""
        events: List[Dict[str, Any]] = [
            {"step": i, "context_size": 20 + i * 15} for i in range(1, 8)
        ]
        report: LeakReport = detect_leaks(events, budget_limit=100)
        self.assertEqual(report.total_events, 7)
        self.assertGreater(report.total_leaks, 0)
        leak_types: List[str] = [s.type for s in report.signatures]
        self.assertIn("monotonic_growth", leak_types)
        self.assertIn("budget_overflow", leak_types)
        expected_rec: str = (
            "Critical budget overflow detected. Implement aggressive sliding "
            "window truncation and tool output summarization."
        )
        self.assertEqual(report.recommendation, expected_rec)
        first_leak: LeakSignature = report.signatures[0]
        self.assertEqual(first_leak.type, "monotonic_growth")
        self.assertEqual(first_leak.step, 3)
        self.assertEqual(first_leak.severity, "medium")

    def test_budget_simulator(self) -> None:
        """Test budget simulation with cap exceedance and truncation savings."""
        events: List[Dict[str, Any]] = [
            {"context_size": 60},
            {"context_size": 60},
            {"context_size": 60}
        ]
        result: SimulationResult = run_budget_simulation(events, cap=100)
        self.assertEqual(result.steps, 3)
        self.assertTrue(result.would_overflow)
        self.assertGreater(result.projected_savings, 0)
        self.assertGreater(result.peak_tokens, 100)
        self.assertIsInstance(result.peak_tokens, int)
        self.assertIsInstance(result.projected_savings, int)

    def test_cli_integration(self) -> None:
        """Test CLI execution via subprocess with a temporary JSONL file."""
        fd, tmp_path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write('{"step": 1, "context_size": 50}\n')
                f.write('{"step": 2, "context_size": 60}\n')
            cli_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cli.py")
            proc = subprocess.run(
                [sys.executable, cli_path, "--input", tmp_path, "--budget", "100"],
                capture_output=True, text=True, timeout=10
            )
            self.assertEqual(proc.returncode, 0)
            output: Dict[str, Any] = json.loads(proc.stdout)
            self.assertIn("total_events", output)
            self.assertIn("total_leaks", output)
            self.assertIn("signatures", output)
            self.assertIn("redundancy_leaks", output)
            self.assertIn("simulation", output)
            self.assertIn("recommendation", output)
            self.assertEqual(output["total_events"], 2)
            self.assertIsInstance(output["simulation"]["would_overflow"], bool)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_edge_cases(self) -> None:
        """Test handling of empty iterables and zero budget limits."""
        empty_report: LeakReport = detect_leaks([], budget_limit=100)
        self.assertEqual(empty_report.total_events, 0)
        self.assertEqual(empty_report.total_leaks, 0)
        self.assertEqual(
            empty_report.recommendation,
            "Context usage is healthy. No compression needed."
        )
        empty_sigs: List[LeakSignature] = scan_redundancy([])
        self.assertEqual(len(empty_sigs), 0)
        empty_sim: SimulationResult = run_budget_simulation([], cap=100)
        self.assertEqual(empty_sim.steps, 0)
        self.assertFalse(empty_sim.would_overflow)
        zero_budget_report: LeakReport = detect_leaks(
            [{"context_size": 10}], budget_limit=0
        )
        self.assertEqual(zero_budget_report.total_leaks, 1)
        self.assertEqual(zero_budget_report.signatures[0].severity, "high")
        zero_cap_sim: SimulationResult = run_budget_simulation(
            [{"context_size": 10}], cap=0
        )
        self.assertEqual(zero_cap_sim.steps, 1)
        self.assertTrue(zero_cap_sim.would_overflow)


if __name__ == "__main__":
    unittest.main()