import json
import os
import subprocess
import sys
import tempfile
import unittest
from typing import List, Dict, Any

from contract_auditor import audit_deployment
from log_parser import parse_log_stream


class TestContractAuditor(unittest.TestCase):
    """Tests for the audit_deployment function."""

    def test_perfect_compliance(self):
        """Test that a perfectly compliant log stream passes."""
        log_stream = [
            {"timestamp": "2023-10-27T10:00:00Z", "action": "checkout_code", "status": "success"},
            {"timestamp": "2023-10-27T10:01:00Z", "action": "run_tests", "status": "success"},
            {"timestamp": "2023-10-27T10:05:00Z", "action": "build_image", "status": "success"}
        ]
        contract = ["checkout_code", "run_tests", "build_image"]
        result = audit_deployment(log_stream, contract)
        self.assertTrue(result["is_compliant"])
        self.assertEqual(result["compliance_rate"], 1.0)
        self.assertEqual(result["unauthorized_actions"], [])
        self.assertEqual(result["amnesia_events"], [])
        self.assertEqual(result["total_actions"], 3)

    def test_skipped_steps_amnesia(self):
        """Test that skipped steps are flagged as amnesia events."""
        log_stream = [
            {"timestamp": "2023-10-27T10:00:00Z", "action": "checkout_code", "status": "success"},
            {"timestamp": "2023-10-27T10:05:00Z", "action": "build_image", "status": "success"}
        ]
        contract = ["checkout_code", "run_tests", "build_image"]
        result = audit_deployment(log_stream, contract)
        self.assertFalse(result["is_compliant"])
        self.assertEqual(result["compliance_rate"], 2/3)
        self.assertEqual(result["unauthorized_actions"], [])
        self.assertEqual(result["amnesia_events"], ["run_tests"])
        self.assertEqual(result["total_actions"], 2)

    def test_extra_unauthorized_steps(self):
        """Test that unauthorized actions are flagged."""
        log_stream = [
            {"timestamp": "2023-10-27T10:00:00Z", "action": "checkout_code", "status": "success"},
            {"timestamp": "2023-10-27T10:01:00Z", "action": "run_tests", "status": "success"},
            {"timestamp": "2023-10-27T10:02:00Z", "action": "deploy_staging", "status": "success"},
            {"timestamp": "2023-10-27T10:05:00Z", "action": "build_image", "status": "success"}
        ]
        contract = ["checkout_code", "run_tests", "build_image"]
        result = audit_deployment(log_stream, contract)
        self.assertFalse(result["is_compliant"])
        self.assertEqual(result["compliance_rate"], 2/3)
        self.assertEqual(result["unauthorized_actions"], ["deploy_staging"])
        self.assertEqual(result["amnesia_events"], ["build_image"])
        self.assertEqual(result["total_actions"], 4)

    def test_out_of_order_steps(self):
        """Test that out-of-order steps are flagged as unauthorized."""
        log_stream = [
            {"timestamp": "2023-10-27T10:00:00Z", "action": "checkout_code", "status": "success"},
            {"timestamp": "2023-10-27T10:01:00Z", "action": "build_image", "status": "success"},
            {"timestamp": "2023-10-27T10:02:00Z", "action": "run_tests", "status": "success"}
        ]
        contract = ["checkout_code", "run_tests", "build_image"]
        result = audit_deployment(log_stream, contract)
        self.assertFalse(result["is_compliant"])
        self.assertEqual(result["compliance_rate"], 1/3)
        self.assertEqual(result["unauthorized_actions"], ["build_image", "run_tests"])
        self.assertEqual(result["amnesia_events"], ["run_tests", "build_image"])
        self.assertEqual(result["total_actions"], 3)

    def test_empty_log_stream(self):
        """Test that an empty log stream is handled correctly."""
        log_stream = []
        contract = ["checkout_code", "run_tests"]
        result = audit_deployment(log_stream, contract)
        self.assertFalse(result["is_compliant"])
        self.assertEqual(result["compliance_rate"], 0.0)
        self.assertEqual(result["unauthorized_actions"], [])
        self.assertEqual(result["amnesia_events"], ["checkout_code", "run_tests"])
        self.assertEqual(result["total_actions"], 0)

    def test_empty_contract(self):
        """Test that an empty contract is handled correctly."""
        log_stream = [
            {"timestamp": "2023-10-27T10:00:00Z", "action": "checkout_code", "status": "success"}
        ]
        contract = []
        result = audit_deployment(log_stream, contract)
        self.assertTrue(result["is_compliant"])
        self.assertEqual(result["compliance_rate"], 1.0)
        self.assertEqual(result["unauthorized_actions"], [])
        self.assertEqual(result["amnesia_events"], [])
        self.assertEqual(result["total_actions"], 1)

    def test_missing_action_key(self):
        """Test that missing 'action' keys are handled gracefully."""
        log_stream = [
            {"timestamp": "2023-10-27T10:00:00Z", "status": "success"},
            {"timestamp": "2023-10-27T10:01:00Z", "action": "run_tests", "status": "success"}
        ]
        contract = ["checkout_code", "run_tests"]
        result = audit_deployment(log_stream, contract)
        self.assertFalse(result["is_compliant"])
        self.assertEqual(result["compliance_rate"], 0.0)
        self.assertEqual(result["unauthorized_actions"], ["UNKNOWN", "run_tests"])
        self.assertEqual(result["amnesia_events"], ["checkout_code"])
        self.assertEqual(result["total_actions"], 2)


class TestLogParser(unittest.TestCase):
    """Tests for the parse_log_stream function."""

    def test_normal_parsing(self):
        """Test normal parsing of valid JSONL content."""
        content = '''{"timestamp": "2023-10-27T10:00:00Z", "action": "checkout_code", "status": "success"}
{"timestamp": "2023-10-27T10:01:00Z", "action": "run_tests", "status": "success"}'''
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            result = list(parse_log_stream(path))
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["action"], "checkout_code")
            self.assertEqual(result[1]["action"], "run_tests")
        finally:
            os.remove(path)

    def test_empty_file(self):
        """Test that empty files don't cause crashes."""
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        try:
            result = list(parse_log_stream(path))
            self.assertEqual(len(result), 0)
        finally:
            os.remove(path)

    def test_malformed_json_lines(self):
        """Test that malformed JSON lines are skipped gracefully."""
        content = '''{"timestamp": "2023-10-27T10:00:00Z", "action": "checkout_code", "status": "success"}
{"invalid": json}
{"timestamp": "2023-10-27T10:01:00Z", "action": "run_tests", "status": "success"}'''
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            result = list(parse_log_stream(path))
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["action"], "checkout_code")
            self.assertEqual(result[1]["action"], "run_tests")
        finally:
            os.remove(path)


class TestCLI(unittest.TestCase):
    """Tests for the CLI module."""

    def test_compliant_log(self):
        """Test CLI with a compliant log file."""
        log_content = '''{"timestamp": "2023-10-27T10:00:00Z", "action": "checkout_code", "status": "success"}
{"timestamp": "2023-10-27T10:01:00Z", "action": "run_tests", "status": "success"}
{"timestamp": "2023-10-27T10:05:00Z", "action": "build_image", "status": "success"}'''
        contract = "checkout_code,run_tests,build_image"

        fd, log_path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(log_content)

            result = subprocess.run([
                sys.executable, "-m", "cli",
                "--log-file", log_path,
                "--contract", contract
            ], capture_output=True, text=True)

            self.assertEqual(result.returncode, 0)
            data = json.loads(result.stdout)
            self.assertTrue(data["is_compliant"])
        finally:
            os.remove(log_path)

    def test_non_compliant_log(self):
        """Test CLI with a non-compliant log file."""
        log_content = '''{"timestamp": "2023-10-27T10:00:00Z", "action": "checkout_code", "status": "success"}
{"timestamp": "2023-10-27T10:01:00Z", "action": "build_image", "status": "success"}'''
        contract = "checkout_code,run_tests,build_image"

        fd, log_path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(log_content)

            result = subprocess.run([
                sys.executable, "-m", "cli",
                "--log-file", log_path,
                "--contract", contract
            ], capture_output=True, text=True)

            self.assertEqual(result.returncode, 2)
            data = json.loads(result.stdout)
            self.assertFalse(data["is_compliant"])
        finally:
            os.remove(log_path)

    def test_missing_log_file(self):
        """Test CLI with a missing log file."""
        result = subprocess.run([
            sys.executable, "-m", "cli",
            "--log-file", "/nonexistent/file.jsonl",
            "--contract", "checkout_code,run_tests"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 1)

    def test_invalid_contract_format(self):
        """Test CLI with invalid contract format."""
        log_content = '''{"timestamp": "2023-10-27T10:00:00Z", "action": "checkout_code", "status": "success"}'''

        fd, log_path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(log_content)

            result = subprocess.run([
                sys.executable, "-m", "cli",
                "--log-file", log_path,
                "--contract", ""
            ], capture_output=True, text=True)

            self.assertEqual(result.returncode, 0)
            data = json.loads(result.stdout)
            self.assertTrue(data["is_compliant"])
        finally:
            os.remove(log_path)


if __name__ == '__main__':
    unittest.main()