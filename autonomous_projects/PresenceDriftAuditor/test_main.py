"""
Comprehensive test suite for the PresenceDriftAuditor project.
Validates parsing, state machine logic, memory-mapped I/O, and CLI execution.
"""

import json
from pathlib import Path

import pytest

from models import LogEvent, parse_log_line
from engine import audit_presence
from cli import stream_log_events, run_audit


def test_parse_log_line_valid() -> None:
    """Assert parse_log_line correctly parses a valid JSON string into a LogEvent."""
    raw = '{"timestamp": 1620000000.0, "agent_id": "a1", "session_id": "s1", "process_id": "p1", "event_type": "CONNECT"}'
    event = parse_log_line(raw)
    
    assert event is not None
    assert isinstance(event, LogEvent)
    assert event.timestamp == 1620000000.0
    assert event.agent_id == "a1"
    assert event.session_id == "s1"
    assert event.process_id == "p1"
    assert event.event_type == "CONNECT"


def test_parse_log_line_malformed_json() -> None:
    """Assert parse_log_line returns None for malformed JSON."""
    raw = '{"timestamp": 1620000000.0, "agent_id": "a1", "session_id": "s1"'
    assert parse_log_line(raw) is None


def test_parse_log_line_missing_keys() -> None:
    """Assert parse_log_line returns None for JSON missing required keys."""
    raw = '{"timestamp": 1620000000.0, "agent_id": "a1"}'
    assert parse_log_line(raw) is None


def test_parse_log_line_invalid_event_type() -> None:
    """Assert parse_log_line returns None for an invalid event_type."""
    raw = '{"timestamp": 1.0, "agent_id": "a1", "session_id": "s1", "process_id": "p1", "event_type": "UNKNOWN"}'
    assert parse_log_line(raw) is None


def test_parse_log_line_non_dict() -> None:
    """Assert parse_log_line returns None for non-dict JSON (e.g., a list)."""
    raw = '[{"timestamp": 1.0, "agent_id": "a1", "session_id": "s1", "process_id": "p1", "event_type": "CONNECT"}]'
    assert parse_log_line(raw) is None


def test_audit_presence_scenario_a() -> None:
    """Scenario A: Agent connects, stays connected. Verify stability_score is 1.0 and migrations is 0."""
    events = [
        LogEvent(timestamp=1.0, agent_id="agent_1", session_id="s1", process_id="p1", event_type="CONNECT"),
        LogEvent(timestamp=5.0, agent_id="agent_1", session_id="s1", process_id="p1", event_type="HEARTBEAT")
    ]
    
    reports = audit_presence(events)
    
    assert "agent_1" in reports
    report = reports["agent_1"]
    assert report.stability_score == 1.0
    assert report.migrations == 0
    assert report.is_flapping is False


def test_audit_presence_scenario_b() -> None:
    """Scenario B: Agent connects, disconnects, reconnects 2 seconds later. Verify flapping."""
    events = [
        LogEvent(timestamp=1.0, agent_id="agent_2", session_id="s1", process_id="p1", event_type="CONNECT"),
        LogEvent(timestamp=2.0, agent_id="agent_2", session_id="s1", process_id="p1", event_type="DISCONNECT"),
        LogEvent(timestamp=4.0, agent_id="agent_2", session_id="s1", process_id="p1", event_type="CONNECT")
    ]
    
    reports = audit_presence(events, flap_threshold_sec=5.0)
    
    assert "agent_2" in reports
    report = reports["agent_2"]
    assert report.is_flapping is True
    assert report.stability_score == 0.9


def test_audit_presence_scenario_c() -> None:
    """Scenario C: Agent sends HEARTBEAT from process_A, then process_B. Verify migrations is 1."""
    events = [
        LogEvent(timestamp=1.0, agent_id="agent_3", session_id="s1", process_id="process_A", event_type="HEARTBEAT"),
        LogEvent(timestamp=2.0, agent_id="agent_3", session_id="s1", process_id="process_B", event_type="HEARTBEAT")
    ]
    
    reports = audit_presence(events)
    
    assert "agent_3" in reports
    report = reports["agent_3"]
    assert report.migrations == 1


def test_stream_log_events(tmp_path: Path) -> None:
    """Test stream_log_events yields exactly 3 LogEvent objects from a file with 3 valid and 1 invalid line."""
    log_file = tmp_path / "test_stream.jsonl"
    lines = [
        '{"timestamp": 1.0, "agent_id": "a1", "session_id": "s1", "process_id": "p1", "event_type": "CONNECT"}\n',
        'this is not valid json\n',
        '{"timestamp": 2.0, "agent_id": "a1", "session_id": "s1", "process_id": "p1", "event_type": "HEARTBEAT"}\n',
        '{"timestamp": 3.0, "agent_id": "a1", "session_id": "s1", "process_id": "p1", "event_type": "DISCONNECT"}\n'
    ]
    log_file.write_text("".join(lines), encoding="utf-8")
    
    events = list(stream_log_events(str(log_file)))
    
    assert len(events) == 3
    assert all(isinstance(e, LogEvent) for e in events)


def test_stream_log_events_empty_file(tmp_path: Path) -> None:
    """Test empty file safety: stream_log_events yields nothing and does not crash."""
    log_file = tmp_path / "empty.jsonl"
    log_file.write_text("", encoding="utf-8")
    
    events = list(stream_log_events(str(log_file)))
    
    assert len(events) == 0


def test_run_audit(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test run_audit end-to-end: verify stdout contains valid JSON with the expected agent_id."""
    log_file = tmp_path / "audit_e2e.jsonl"
    line = '{"timestamp": 1.0, "agent_id": "agent_99", "session_id": "s1", "process_id": "p1", "event_type": "CONNECT"}\n'
    log_file.write_text(line, encoding="utf-8")
    
    run_audit(str(log_file), flap_threshold=5.0)
    
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    
    assert isinstance(output, list)
    assert len(output) == 1
    assert output[0]["agent_id"] == "agent_99"
    assert output[0]["stability_score"] == 1.0
    assert output[0]["is_flapping"] is False
    assert output[0]["migrations"] == 0