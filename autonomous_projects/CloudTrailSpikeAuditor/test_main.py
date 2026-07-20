"""
Test suite for CloudTrailSpikeAuditor.

Validates the I/O engine, core analysis logic, and CLI wiring
using strict TDD principles without mocking.
"""
import json
import pathlib
from typing import Any, Dict

import pytest

from io_engine import stream_log_lines
from main import main
from sentinel_core import analyze_provisioning_spikes


def test_analyze_provisioning_spikes_counts_and_flags() -> None:
    """
    Test that analyze_provisioning_spikes correctly counts events,
    ignores malformed JSON, and flags anomalies when threshold is crossed.
    """
    lines = [
        json.dumps({"eventName": "RunInstances"}),
        json.dumps({"eventName": "RunInstances"}),
        json.dumps({"eventName": "CreateVolume"}),
        "this is not valid json",
        json.dumps({"eventName": "DescribeInstances"}),
    ]
    
    result: Dict[str, Any] = analyze_provisioning_spikes(lines, spike_threshold=1)
    
    assert result["total_events"] == 4
    assert result["is_anomalous"] is True
    assert result["spikes"]["RunInstances"] == 2
    assert "CreateVolume" not in result["spikes"]
    assert "DescribeInstances" not in result["spikes"]


def test_analyze_provisioning_spikes_no_anomaly() -> None:
    """Test that analyze_provisioning_spikes correctly identifies normal traffic."""
    lines = [
        json.dumps({"eventName": "RunInstances"}),
        json.dumps({"eventName": "CreateBucket"}),
    ]
    
    result: Dict[str, Any] = analyze_provisioning_spikes(lines, spike_threshold=10)
    
    assert result["total_events"] == 2
    assert result["is_anomalous"] is False
    assert not result["spikes"]


def test_stream_log_lines_reads_file(tmp_path: pathlib.Path) -> None:
    """Test that stream_log_lines correctly streams lines from a JSONL file."""
    log_file = tmp_path / "test.jsonl"
    lines = [
        json.dumps({"eventName": "RunInstances"}),
        json.dumps({"eventName": "CreateVolume"}),
    ]
    log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    
    streamed = list(stream_log_lines(str(log_file)))
    
    assert len(streamed) == 2
    assert json.loads(streamed[0])["eventName"] == "RunInstances"
    assert json.loads(streamed[1])["eventName"] == "CreateVolume"


def test_stream_log_lines_empty_file(tmp_path: pathlib.Path) -> None:
    """Test the win32 empty-file guard by ensuring 0-byte files don't crash."""
    empty_file = tmp_path / "empty.jsonl"
    empty_file.touch()
    
    streamed = list(stream_log_lines(str(empty_file)))
    
    assert streamed == []


def test_main_success(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test main CLI entry point with a valid log file and custom threshold."""
    log_file = tmp_path / "audit.jsonl"
    lines = [json.dumps({"eventName": "RunInstances"}) for _ in range(5)]
    log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    
    exit_code = main([str(log_file), "--threshold", "2"])
    
    assert exit_code == 0
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    
    assert output["total_events"] == 5
    assert output["is_anomalous"] is True
    assert output["spikes"]["RunInstances"] == 5


def test_main_file_not_found(capsys: pytest.CaptureFixture[str]) -> None:
    """Test main CLI entry point when the specified log file does not exist."""
    exit_code = main(["nonexistent_file.jsonl"])
    
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error: Log file not found" in captured.err