import unittest
import json
import os
import subprocess
import sys
import tempfile
from typing import List, Dict, Any, Tuple

import contracts
import parser
import simulator
from contracts import ToolContract


class TestContractsModule(unittest.TestCase):
    """Unit tests for contracts.py pure functions."""

    def test_check_type_drift(self) -> None:
        """Verify strict type rules and alias normalization."""
        self.assertFalse(contracts.check_type_drift("str", "string"))
        self.assertFalse(contracts.check_type_drift("int", "integer"))
        self.assertFalse(contracts.check_type_drift("float", "double"))
        self.assertFalse(contracts.check_type_drift("bool", "boolean"))
        self.assertFalse(contracts.check_type_drift("list", "array"))
        self.assertFalse(contracts.check_type_drift("dict", "object"))
        self.assertFalse(contracts.check_type_drift("none", "null"))
        self.assertFalse(contracts.check_type_drift("str", "str"))
        self.assertFalse(contracts.check_type_drift("int", "int"))
        self.assertTrue(contracts.check_type_drift("str", "int"))
        self.assertTrue(contracts.check_type_drift("float", "bool"))
        self.assertTrue(contracts.check_type_drift("list", "dict"))
        self.assertFalse(contracts.check_type_drift("STRING", "Str"))
        self.assertTrue(contracts.check_type_drift("INT", "Float"))

    def test_validate_io_compatibility(self) -> None:
        """Assert exact mismatch lists for matching, missing keys, and type drift cases."""
        src_out = {"id": "int", "name": "str"}
        tgt_in = {"id": "int", "name": "str"}
        self.assertEqual(contracts.validate_io_compatibility(src_out, tgt_in), [])

        src_out = {"id": "int"}
        tgt_in = {"id": "int", "name": "str"}
        errors = contracts.validate_io_compatibility(src_out, tgt_in)
        self.assertEqual(len(errors), 1)
        self.assertIn("Missing key: 'name'", errors[0])

        src_out = {"id": "str", "name": "str"}
        tgt_in = {"id": "int", "name": "str"}
        errors = contracts.validate_io_compatibility(src_out, tgt_in)
        self.assertEqual(len(errors), 1)
        self.assertIn("Type drift on key 'id'", errors[0])
        self.assertIn("expected 'int', got 'str'", errors[0])

        src_out = {"id": "str"}
        tgt_in = {"id": "int", "name": "str"}
        errors = contracts.validate_io_compatibility(src_out, tgt_in)
        self.assertEqual(len(errors), 2)

        src_out = {"id": "int", "name": "str", "extra": "float"}
        tgt_in = {"id": "int"}
        self.assertEqual(contracts.validate_io_compatibility(src_out, tgt_in), [])


class TestParserModule(unittest.TestCase):
    """Unit tests for parser.py pure functions."""

    def test_parse_contracts(self) -> None:
        """Feed a list of raw JSON strings and assert correct filtering."""
        lines = [
            '{"name": "ToolA", "input_schema": {"x": "int"}, "output_schema": {"y": "str"}}',
            '{"name": "ToolB", "input_schema": {"y": "str"}, "output_schema": {"z": "bool"}}',
            'invalid json line',
            '{"name": "ToolC", "input_schema": {"a": "int"}}',
            '',
            '   ',
            '{"name": "ToolD", "input_schema": {}, "output_schema": {}}'
        ]
        result = parser.parse_contracts(lines)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["name"], "ToolA")
        self.assertEqual(result[1]["name"], "ToolB")
        self.assertEqual(result[2]["name"], "ToolD")

    def test_parse_chain_links(self) -> None:
        """Verify tuple extraction for both '->' and JSON formats."""
        lines = [
            'ToolA->ToolB',
            '{"from": "ToolB", "to": "ToolC"}',
            'invalid->',
            '->invalid',
            'no arrow here',
            '{"from": "ToolC"}',
            '  ToolD -> ToolE  ',
            ''
        ]
        result = parser.parse_chain_links(lines)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("ToolA", "ToolB"))
        self.assertEqual(result[1], ("ToolB", "ToolC"))
        self.assertEqual(result[2], ("ToolD", "ToolE"))


class TestSimulatorModule(unittest.TestCase):
    """Unit tests for simulator.py pure functions."""

    def _make_registry(self) -> Dict[str, ToolContract]:
        """Helper to create a standard registry for testing."""
        return {
            "ToolA": ToolContract("ToolA", {"x": "int"}, {"y": "str"}),
            "ToolB": ToolContract("ToolB", {"y": "str"}, {"z": "bool"}),
            "ToolC": ToolContract("ToolC", {"z": "bool"}, {"w": "int"}),
            "ToolD": ToolContract("ToolD", {"y": "int"}, {"v": "str"})
        }

    def test_audit_toolchain(self) -> None:
        """Pass a mock registry and link sequence, asserting exact counts and flags."""
        registry = self._make_registry()
        
        valid_links = [("ToolA", "ToolB"), ("ToolB", "ToolC")]
        report = simulator.audit_toolchain(registry, valid_links)
        self.assertTrue(report.valid)
        self.assertEqual(len(report.mismatches), 0)
        self.assertEqual(len(report.circular_deps), 0)
        self.assertEqual(len(report.missing_tools), 0)

        missing_links = [("ToolA", "ToolX"), ("ToolY", "ToolB")]
        report = simulator.audit_toolchain(registry, missing_links)
        self.assertFalse(report.valid)
        self.assertEqual(len(report.missing_tools), 2)
        self.assertIn("ToolX", report.missing_tools)
        self.assertIn("ToolY", report.missing_tools)

        mismatch_links = [("ToolA", "ToolD")]
        report = simulator.audit_toolchain(registry, mismatch_links)
        self.assertFalse(report.valid)
        self.assertEqual(len(report.mismatches), 1)
        self.assertEqual(report.mismatches[0]["source"], "ToolA")
        self.assertEqual(report.mismatches[0]["target"], "ToolD")
        self.assertIn("Type drift", report.mismatches[0]["error"])

        circular_links = [("ToolA", "ToolB"), ("ToolB", "ToolC"), ("ToolC", "ToolA")]
        report = simulator.audit_toolchain(registry, circular_links)
        self.assertFalse(report.valid)
        self.assertEqual(len(report.circular_deps), 1)
        self.assertEqual(report.circular_deps[0], ("ToolC", "ToolA"))


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for cli.py using subprocess."""

    def _create_temp_file(self, content: str) -> str:
        """Create a temporary file with given content and return its path."""
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_cli_integration(self) -> None:
        """Use subprocess.run to execute cli.py, verifying exit codes and JSON output."""
        contracts_content = (
            '{"name": "T1", "input_schema": {"a": "int"}, "output_schema": {"b": "str"}}\n'
            '{"name": "T2", "input_schema": {"b": "str"}, "output_schema": {"c": "bool"}}\n'
        )
        chain_content = "T1->T2\n"
        
        c_path = self._create_temp_file(contracts_content)
        ch_path = self._create_temp_file(chain_content)
        
        try:
            result = subprocess.run(
                [sys.executable, "cli.py", "--contracts", c_path, "--chain", ch_path],
                capture_output=True, text=True, timeout=10
            )
            self.assertEqual(result.returncode, 0)
            output = json.loads(result.stdout)
            self.assertTrue(output["valid"])
            self.assertEqual(len(output["mismatches"]), 0)
            self.assertEqual(len(output["missing_tools"]), 0)
            self.assertEqual(len(output["circular_deps"]), 0)
        finally:
            os.unlink(c_path)
            os.unlink(ch_path)

        fail_result = subprocess.run(
            [sys.executable, "cli.py", "--contracts", "nonexistent.json", "--chain", "nonexistent.txt"],
            capture_output=True, text=True, timeout=10
        )
        self.assertEqual(fail_result.returncode, 1)
        self.assertIn("Audit failed", fail_result.stderr)

        mismatch_contracts = (
            '{"name": "T1", "input_schema": {"a": "int"}, "output_schema": {"b": "str"}}\n'
            '{"name": "T2", "input_schema": {"b": "int"}, "output_schema": {"c": "bool"}}\n'
        )
        c_path2 = self._create_temp_file(mismatch_contracts)
        ch_path2 = self._create_temp_file(chain_content)
        
        try:
            result2 = subprocess.run(
                [sys.executable, "cli.py", "--contracts", c_path2, "--chain", ch_path2],
                capture_output=True, text=True, timeout=10
            )
            self.assertEqual(result2.returncode, 0)
            output2 = json.loads(result2.stdout)
            self.assertFalse(output2["valid"])
            self.assertEqual(len(output2["mismatches"]), 1)
        finally:
            os.unlink(c_path2)
            os.unlink(ch_path2)


if __name__ == "__main__":
    unittest.main()