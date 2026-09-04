import os
import sys
import json
import tempfile
import subprocess
import unittest
from typing import List, Dict
from models import LogEntry, CircuitState, RoutingDecision
from parser import parse_log_stream
from breaker import evaluate_circuit_states
from router import simulate_fallback_routing


def _create_temp_file(content: str) -> str:
    """Create a temporary file with given content and return its path."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


class TestParser(unittest.TestCase):
    """Test suite for the log parser module."""

    def test_parser_valid_and_malformed(self) -> None:
        """Verify parser yields correct LogEntries and skips malformed lines."""
        valid_line_1 = json.dumps({
            "timestamp": 1000.0, "provider": "openai",
            "status_code": 200, "latency_ms": 120.5
        })
        valid_line_2 = json.dumps({
            "timestamp": 1001.0, "provider": "anthropic",
            "status_code": 500, "latency_ms": 300.0
        })
        lines = [valid_line_1, "GARBAGE_DATA", valid_line_2, "{bad json", ""]
        entries: List[LogEntry] = list(parse_log_stream(lines))
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].provider, "openai")
        self.assertEqual(entries[0].status_code, 200)
        self.assertAlmostEqual(entries[0].latency_ms, 120.5)
        self.assertEqual(entries[1].provider, "anthropic")
        self.assertEqual(entries[1].status_code, 500)


class TestBreaker(unittest.TestCase):
    """Test suite for the circuit breaker state machine."""

    def _build_entries(self, count: int, status: int, start_ts: float) -> List[LogEntry]:
        """Generate a list of LogEntry objects for testing."""
        return [
            LogEntry(timestamp=start_ts + i, provider="test_prov",
                     status_code=status, latency_ms=100.0)
            for i in range(count)
        ]

    def test_breaker_state_transitions(self) -> None:
        """Assert error_rate calculation and CLOSED->OPEN->HALF-OPEN transitions."""
        window, threshold, cooldown = 5, 0.6, 10.0
        phase1 = self._build_entries(5, 200, 1.0)
        states1 = evaluate_circuit_states(phase1, window, threshold, cooldown)
        self.assertEqual(states1["test_prov"].state, "CLOSED")
        self.assertAlmostEqual(states1["test_prov"].error_rate, 0.0)

        phase2 = phase1 + self._build_entries(5, 500, 6.0)
        states2 = evaluate_circuit_states(phase2, window, threshold, cooldown)
        self.assertEqual(states2["test_prov"].state, "OPEN")
        self.assertAlmostEqual(states2["test_prov"].error_rate, 1.0)

        phase3 = phase2 + self._build_entries(5, 200, 25.0)
        states3 = evaluate_circuit_states(phase3, window, threshold, cooldown)
        self.assertEqual(states3["test_prov"].state, "HALF-OPEN")
        self.assertAlmostEqual(states3["test_prov"].error_rate, 0.0)


class TestRouter(unittest.TestCase):
    """Test suite for the fallback routing simulator."""

    def test_router_fallback_logic(self) -> None:
        """Verify correct primary/fallback selection based on circuit states."""
        circuit_states: Dict[str, CircuitState] = {
            "primary_ai": CircuitState(
                provider="primary_ai", state="OPEN", error_rate=0.8
            ),
            "backup_ai": CircuitState(
                provider="backup_ai", state="CLOSED", error_rate=0.1
            )
        }
        policy: List[str] = ["primary_ai", "backup_ai"]
        decision: RoutingDecision = simulate_fallback_routing(circuit_states, policy)
        self.assertEqual(decision.provider, "backup_ai")
        self.assertTrue(decision.is_fallback)
        self.assertIn("primary_ai", decision.reason)
        self.assertIn("OPEN", decision.reason)


class TestCLI(unittest.TestCase):
    """Integration test suite for the command-line interface."""

    def test_cli_integration(self) -> None:
        """Execute cli.py via subprocess and validate exit code and JSON output."""
        log_content = "\n".join([
            json.dumps({"timestamp": 1.0, "provider": "p1", "status_code": 200, "latency_ms": 50.0}),
            json.dumps({"timestamp": 2.0, "provider": "p2", "status_code": 200, "latency_ms": 60.0})
        ])
        policy_content = json.dumps(["p1", "p2"])
        log_path = _create_temp_file(log_content)
        policy_path = _create_temp_file(policy_content)
        try:
            cli_script = os.path.join(os.path.dirname(__file__), "cli.py")
            result = subprocess.run(
                [sys.executable, cli_script, "--log", log_path, "--policy", policy_path],
                capture_output=True, text=True, timeout=10
            )
            self.assertEqual(result.returncode, 0)
            output_data = json.loads(result.stdout)
            self.assertIn("routing_decision", output_data)
            self.assertIn("circuit_states", output_data)
        finally:
            os.unlink(log_path)
            os.unlink(policy_path)


if __name__ == "__main__":
    unittest.main()