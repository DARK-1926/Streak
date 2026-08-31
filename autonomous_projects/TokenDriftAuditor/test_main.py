import unittest
import json
from typing import List, Dict, Any

import core
import models


class TestTokenDriftAuditor(unittest.TestCase):
    """Strict unit tests for TokenDriftAuditor core logic and models."""

    def test_parse_valid_line(self) -> None:
        """Pass valid JSON string, assert dict keys."""
        raw = '{"session_id": "s1", "prompt_tokens": 10, "completion_tokens": 5, "prompt_text": "hello", "status": "ok"}'
        result = core.parse_log_line(raw)
        self.assertIsNotNone(result)
        self.assertEqual(result["session_id"], "s1")
        self.assertEqual(result["prompt_tokens"], 10)
        self.assertEqual(result["completion_tokens"], 5)
        self.assertEqual(result["prompt_text"], "hello")
        self.assertEqual(result["status"], "ok")

    def test_parse_malformed(self) -> None:
        """Pass broken JSON, missing keys, empty string; assert None returned."""
        self.assertIsNone(core.parse_log_line('{"broken": json}'))
        self.assertIsNone(core.parse_log_line('{"session_id": "s1"}'))
        self.assertIsNone(core.parse_log_line(''))
        self.assertIsNone(core.parse_log_line('   '))

    def test_single_pass_audit_empty(self) -> None:
        """Pass empty list, assert report has 0 tokens, 0 cost, empty inefficiencies, 0.0 drift."""
        report = core.run_audit_stream([])
        self.assertEqual(report.total_sessions, 0)
        self.assertEqual(report.total_tokens, 0)
        self.assertEqual(report.estimated_cost, 0.0)
        self.assertEqual(report.inefficiencies, [])
        self.assertEqual(report.drift_score, 0.0)

    def test_detect_prompt_duplication(self) -> None:
        """Pass list of 5 dicts with identical prompt_text and same session_id, assert pattern."""
        events: List[Dict[str, Any]] = [
            {
                "session_id": "sess_dup",
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "prompt_text": "repeat this prompt",
                "status": "ok",
            }
            for _ in range(5)
        ]
        report = core.run_audit_stream(events)
        dup_patterns = [p for p in report.inefficiencies if p.pattern_type == "prompt_duplication"]
        self.assertEqual(len(dup_patterns), 1)
        self.assertGreaterEqual(dup_patterns[0].count, 3)

    def test_detect_context_bloat(self) -> None:
        """Pass dicts with high prompt_tokens accumulating > 8000 in one session, assert pattern."""
        events: List[Dict[str, Any]] = [
            {
                "session_id": "sess_bloat",
                "prompt_tokens": 4000,
                "completion_tokens": 4001,
                "prompt_text": "large context",
                "status": "ok",
            }
        ]
        report = core.run_audit_stream(events)
        bloat_patterns = [p for p in report.inefficiencies if p.pattern_type == "context_bloat"]
        self.assertEqual(len(bloat_patterns), 1)
        self.assertEqual(bloat_patterns[0].session_id, "sess_bloat")

    def test_cost_drift_calculation(self) -> None:
        """Pass known token counts, assert estimated_cost matches formula exactly."""
        events: List[Dict[str, Any]] = [
            {
                "session_id": "sess_cost",
                "prompt_tokens": 1000,
                "completion_tokens": 1000,
                "prompt_text": "cost test",
                "status": "ok",
            }
        ]
        cost_rate = 0.01
        report = core.run_audit_stream(events, cost_per_1k=cost_rate)
        expected_cost = (report.total_tokens / 1000.0) * cost_rate
        self.assertEqual(report.estimated_cost, expected_cost)
        self.assertEqual(report.total_tokens, 2000)

    def test_retry_storm(self) -> None:
        """Pass consecutive error statuses with same prompt, assert retry_storm."""
        events: List[Dict[str, Any]] = [
            {
                "session_id": "sess_retry",
                "prompt_tokens": 10,
                "completion_tokens": 0,
                "prompt_text": "failing prompt",
                "status": "error",
            }
            for _ in range(4)
        ]
        report = core.run_audit_stream(events)
        retry_patterns = [p for p in report.inefficiencies if p.pattern_type == "retry_storm"]
        self.assertEqual(len(retry_patterns), 1)
        self.assertGreaterEqual(retry_patterns[0].count, 3)

    def test_report_serialization(self) -> None:
        """Create dummy AuditReport, call to_dict(), assert output is plain dict and JSON-serializable."""
        dummy_pattern = models.InefficiencyPattern(
            pattern_type="test_pattern",
            session_id="sess_ser",
            count=1,
            details="test details"
        )
        report = models.AuditReport(
            total_sessions=1,
            total_tokens=100,
            estimated_cost=0.5,
            inefficiencies=[dummy_pattern],
            drift_score=0.1
        )
        result = report.to_dict()
        self.assertIsInstance(result, dict)
        expected_keys = {"total_sessions", "total_tokens", "estimated_cost", "inefficiencies", "drift_score"}
        self.assertEqual(set(result.keys()), expected_keys)
        self.assertIsInstance(result["inefficiencies"], list)
        self.assertEqual(result["inefficiencies"][0]["pattern_type"], "test_pattern")
        json_str = json.dumps(result)
        self.assertIsInstance(json_str, str)


if __name__ == "__main__":
    unittest.main()