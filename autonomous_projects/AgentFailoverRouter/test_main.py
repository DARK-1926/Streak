import unittest
import tempfile
import subprocess
import sys
import os
import json
from typing import List, Dict, Any

from core.models import CallRecord, FailoverPolicy, RouterState, RoutingDecision
from core.router import update_state, evaluate_route
from core.recovery import snapshot_context, restore_context, compute_context_diff
from adapters.executor import execute_with_failover


class TestRouter(unittest.TestCase):
    def test_evaluate_route_stays_on_target(self) -> None:
        policy = FailoverPolicy(
            max_retries=3,
            fallback_target="fallback",
            error_rate_threshold=0.5,
            latency_threshold_ms=100.0,
            window_size=5
        )
        history: List[CallRecord] = [
            CallRecord(target="target", success=True, latency_ms=20.0, error_code=None, timestamp=0.0),
            CallRecord(target="target", success=True, latency_ms=30.0, error_code=None, timestamp=1.0),
            CallRecord(target="target", success=True, latency_ms=25.0, error_code=None, timestamp=2.0),
        ]
        decision = evaluate_route(history, policy, "target")
        self.assertFalse(decision.should_failover)
        self.assertEqual(decision.route_to, "target")

    def test_evaluate_route_triggers_failover_on_error_rate(self) -> None:
        policy = FailoverPolicy(
            max_retries=3,
            fallback_target="fallback",
            error_rate_threshold=0.5,
            latency_threshold_ms=100.0,
            window_size=5
        )
        history: List[CallRecord] = [
            CallRecord(target="target", success=False, latency_ms=20.0, error_code="error", timestamp=0.0),
            CallRecord(target="target", success=False, latency_ms=30.0, error_code="error", timestamp=1.0),
            CallRecord(target="target", success=False, latency_ms=25.0, error_code="error", timestamp=2.0),
            CallRecord(target="target", success=False, latency_ms=40.0, error_code="error", timestamp=3.0),
            CallRecord(target="target", success=True, latency_ms=35.0, error_code=None, timestamp=4.0),  # 80% failure
        ]
        decision = evaluate_route(history, policy, "target")
        self.assertTrue(decision.should_failover)
        self.assertEqual(decision.route_to, "fallback")

    def test_evaluate_route_triggers_failover_on_latency(self) -> None:
        policy = FailoverPolicy(
            max_retries=3,
            fallback_target="fallback",
            error_rate_threshold=0.5,
            latency_threshold_ms=100.0,
            window_size=5
        )
        history: List[CallRecord] = [
            CallRecord(target="target", success=True, latency_ms=150.0, error_code=None, timestamp=0.0),
            CallRecord(target="target", success=True, latency_ms=160.0, error_code=None, timestamp=1.0),
            CallRecord(target="target", success=True, latency_ms=170.0, error_code=None, timestamp=2.0),
        ]
        decision = evaluate_route(history, policy, "target")
        self.assertTrue(decision.should_failover)
        self.assertEqual(decision.route_to, "fallback")

    def test_update_state_accumulates_correctly(self) -> None:
        state = RouterState(total_calls=0, total_failures=0, rolling_latencies=[], current_target="target")
        record1 = CallRecord(target="target", success=True, latency_ms=50.0, error_code=None, timestamp=0.0)
        state = update_state(state, record1)
        self.assertEqual(state.total_calls, 1)
        self.assertEqual(state.total_failures, 0)
        self.assertEqual(len(state.rolling_latencies), 1)
        self.assertEqual(state.rolling_latencies[0], 50.0)

        record2 = CallRecord(target="target", success=False, latency_ms=200.0, error_code="error", timestamp=1.0)
        state = update_state(state, record2)
        self.assertEqual(state.total_calls, 2)
        self.assertEqual(state.total_failures, 1)
        self.assertEqual(len(state.rolling_latencies), 2)
        self.assertEqual(state.rolling_latencies[1], 200.0)

        # Test rolling window cap
        policy = FailoverPolicy(max_retries=3, fallback_target="fallback", error_rate_threshold=0.5, latency_threshold_ms=100.0, window_size=3)
        long_history = [CallRecord(target="target", success=True, latency_ms=10.0, error_code=None, timestamp=float(i)) for i in range(5)]
        state = RouterState(total_calls=0, total_failures=0, rolling_latencies=[], current_target="target")
        for rec in long_history:
            state = update_state(state, rec, policy.window_size)
        self.assertEqual(len(state.rolling_latencies), 3)


class TestRecovery(unittest.TestCase):
    def test_snapshot_and_restore_context_roundtrip(self) -> None:
        original_context = {"user_id": "123", "session_token": "abc", "counter": 42}
        snapshot = snapshot_context(original_context)
        restored = restore_context(snapshot)
        self.assertEqual(original_context, restored)

    def test_compute_context_diff_detects_changes(self) -> None:
        ctx1 = {"a": 1, "b": 2, "c": 3}
        ctx2 = {"a": 1, "b": 99, "d": 4}
        diff = compute_context_diff(ctx1, ctx2)
        expected = {"b": 99, "d": 4}
        self.assertEqual(diff, expected)


class TestExecutor(unittest.TestCase):
    def test_execute_with_failover_routes_correctly(self) -> None:
        def target_func(context: Dict[str, Any]) -> Dict[str, Any]:
            raise Exception("Target failed")

        def fallback_func(context: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": "from_fallback", "context_used": context}

        context = {"key": "value"}
        policy = FailoverPolicy(
            max_retries=1,
            fallback_target="fallback",
            error_rate_threshold=0.1,
            latency_threshold_ms=50.0,
            window_size=3
        )

        result_dict, call_record = execute_with_failover(
            target_runner=target_func,
            fallback_runner=fallback_func,
            context=context,
            policy=policy
        )

        self.assertIn("result", result_dict)
        self.assertEqual(result_dict["result"], "from_fallback")
        self.assertEqual(result_dict["context_used"], context)
        self.assertFalse(call_record.success)


class TestCLI(unittest.TestCase):
    def test_cli_integration_runs_without_error(self) -> None:
        # Create temporary config file
        config_data = {
            "max_retries": 2,
            "error_rate_threshold": 0.3,
            "latency_threshold_ms": 80.0,
            "fallback_target": "fallback",
            "window_size": 10
        }
        context_data = {"input_value": 42, "mode": "test"}

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as cfg_file:
            json.dump(config_data, cfg_file)
            cfg_path = cfg_file.name

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as ctx_file:
            json.dump(context_data, ctx_file)
            ctx_path = ctx_file.name

        try:
            result = subprocess.run(
                [sys.executable, 'cli.py', '--config', cfg_path, '--input', ctx_path, '--simulate-failure'],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            self.assertEqual(result.returncode, 0)
            # Validate output is valid JSON
            output = json.loads(result.stdout)
            self.assertIsInstance(output, dict)
            self.assertIn("result", output)
        finally:
            os.unlink(cfg_path)
            os.unlink(ctx_path)


if __name__ == '__main__':
    unittest.main()