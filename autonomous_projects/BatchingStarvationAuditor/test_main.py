"""
Strict TDD suite for BatchingStarvationAuditor.
Validates pure logic and memory-mapped file I/O without mocks.
"""

import json
import pytest
from typing import Any

from batching_auditor import parse_event, calculate_starvation_metrics
from cli import process_log_file


def test_parse_event_valid() -> None:
    """Assert correct parsing of a valid JSON string."""
    line = '{"request_id": "req-1", "queue_wait_ms": 42, "batch_id": "batch-A"}'
    result = parse_event(line)
    
    assert result is not None
    assert result["request_id"] == "req-1"
    assert result["queue_wait_ms"] == 42
    assert result["batch_id"] == "batch-A"


def test_parse_event_invalid() -> None:
    """Assert None is returned for malformed JSON and missing keys."""
    assert parse_event("not a json string") is None
    assert parse_event('{"request_id": "1"}') is None
    assert parse_event('{"request_id": "1", "queue_wait_ms": 10}') is None
    assert parse_event('{"queue_wait_ms": 10, "batch_id": "A"}') is None


def test_calculate_starvation_metrics() -> None:
    """Assert exact counts of total, starved, max wait, average wait, and batch counts."""
    events = [
        {"request_id": "1", "queue_wait_ms": 10, "batch_id": "A"},
        {"request_id": "2", "queue_wait_ms": 60, "batch_id": "A"},
        {"request_id": "3", "queue_wait_ms": 100, "batch_id": "B"},
        {"request_id": "4", "queue_wait_ms": 30, "batch_id": "B"},
    ]
    metrics = calculate_starvation_metrics(events, threshold_ms=50)
    
    assert metrics["total_requests"] == 4
    assert metrics["starved_requests"] == 2
    assert metrics["total_wait_ms"] == 200
    assert metrics["max_wait_ms"] == 100
    assert metrics["average_wait_ms"] == 50.0
    assert metrics["batch_starvation_counts"] == {"A": 1, "B": 1}


def test_process_log_file_empty(tmp_path: Any) -> None:
    """Assert empty file returns default metrics without crashing (win32 guard)."""
    filepath = tmp_path / "empty.jsonl"
    filepath.touch()
    
    metrics = process_log_file(str(filepath), threshold_ms=50)
    
    assert metrics["total_requests"] == 0
    assert metrics["starved_requests"] == 0
    assert metrics["total_wait_ms"] == 0
    assert metrics["max_wait_ms"] == 0
    assert metrics["average_wait_ms"] == 0.0
    assert metrics["batch_starvation_counts"] == {}


def test_process_log_file_massive(tmp_path: Any) -> None:
    """Assert aggregated metrics exactly match expected math for 100 lines."""
    filepath = tmp_path / "massive.jsonl"
    lines = []
    
    # 50 normal events (wait 10ms)
    for i in range(50):
        lines.append(json.dumps({"request_id": f"n{i}", "queue_wait_ms": 10, "batch_id": "A"}))
        
    # 40 starved events (wait 100ms)
    for i in range(40):
        lines.append(json.dumps({"request_id": f"s{i}", "queue_wait_ms": 100, "batch_id": "B"}))
        
    # 10 invalid lines
    for i in range(10):
        lines.append("invalid json line")
        
    filepath.write_text("\n".join(lines) + "\n", encoding="utf-8")
    
    metrics = process_log_file(str(filepath), threshold_ms=50)
    
    assert metrics["total_requests"] == 90
    assert metrics["starved_requests"] == 40
    assert metrics["total_wait_ms"] == 4500  # (50 * 10) + (40 * 100)
    assert metrics["max_wait_ms"] == 100
    assert metrics["average_wait_ms"] == 50.0  # 4500 / 90
    assert metrics["batch_starvation_counts"] == {"B": 40}


def test_process_log_file_missing(tmp_path: Any) -> None:
    """Assert FileNotFoundError is raised for non-existent file."""
    filepath = tmp_path / "missing.jsonl"
    
    with pytest.raises(FileNotFoundError):
        process_log_file(str(filepath), threshold_ms=50)