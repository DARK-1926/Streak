import json
import io
import pathlib
import pytest
from typing import Any, Dict

from context_drift import (
    parse_manifest_entry,
    parse_knowledge_entry,
    calculate_slop_score,
    audit_context_drift
)
import cli


def test_parse_manifest_entry_valid() -> None:
    """
    Test parsing of manifest entries with valid, invalid, and missing data.
    """
    valid_line = json.dumps({"type": "code", "symbol": "MyClass"})
    assert parse_manifest_entry(valid_line) == "MyClass"

    invalid_json = "not a json string"
    assert parse_manifest_entry(invalid_json) is None

    missing_type = json.dumps({"symbol": "MyClass"})
    assert parse_manifest_entry(missing_type) is None

    missing_symbol = json.dumps({"type": "code"})
    assert parse_manifest_entry(missing_symbol) is None


def test_parse_knowledge_entry_valid() -> None:
    """
    Test parsing of knowledge entries with valid, invalid, and missing data.
    """
    valid_line = json.dumps({"id": "1", "text": "Hello", "author": "Alice"})
    result = parse_knowledge_entry(valid_line)
    assert result is not None
    assert result["id"] == "1"

    invalid_json = "{bad json"
    assert parse_knowledge_entry(invalid_json) is None

    missing_id = json.dumps({"text": "Hello", "author": "Alice"})
    assert parse_knowledge_entry(missing_id) is None


def test_calculate_slop_score_high() -> None:
    """
    Test slop score calculation for high density and normal text.
    """
    slop_text = "delve into the tapestry of delve and tapestry"
    score = calculate_slop_score(slop_text)
    assert score > 0.0

    normal_text = "This is a standard technical documentation string."
    assert calculate_slop_score(normal_text) == 0.0


def test_audit_context_drift_detects_orphans() -> None:
    """
    Test drift detection identifies orphaned symbols correctly.
    """
    manifest_data = json.dumps({"type": "code", "symbol": "Auth"})
    manifest_stream = io.StringIO(manifest_data + "\n")

    knowledge_data = json.dumps({"id": "1", "text": "Use Auth and DBManager", "author": "Bob"})
    knowledge_stream = io.StringIO(knowledge_data + "\n")

    report = audit_context_drift(manifest_stream, knowledge_stream)

    assert "DBManager" in report["orphaned_symbols"]
    assert report["drifted_docs"] == 1
    assert report["total_docs"] == 1
    assert report["high_slop_docs"] == 0


def test_cli_empty_file_guard(tmp_path: pathlib.Path) -> None:
    """
    Test that safe_mmap_generator handles empty files without crashing.
    """
    empty_file = tmp_path / "empty.jsonl"
    empty_file.write_text("")

    result = list(cli.safe_mmap_generator(str(empty_file)))
    assert result == []


def test_cli_main_success(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test successful CLI execution with valid JSONL files.
    """
    manifest_file = tmp_path / "manifest.jsonl"
    manifest_file.write_text(json.dumps({"type": "code", "symbol": "App"}) + "\n")

    knowledge_file = tmp_path / "knowledge.jsonl"
    knowledge_file.write_text(json.dumps({"id": "1", "text": "App is good", "author": "Dev"}) + "\n")

    exit_code = cli.main(["cli.py", str(manifest_file), str(knowledge_file)])
    assert exit_code == 0

    captured = capsys.readouterr()
    output_data = json.loads(captured.out)
    
    assert "total_docs" in output_data
    assert "drifted_docs" in output_data
    assert "high_slop_docs" in output_data
    assert "orphaned_symbols" in output_data