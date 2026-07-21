"""
Test suite for ZombieComputeAuditor.

Validates anomaly detection, malformed/incomplete log resilience, 
and CLI file processing.
"""

import json
from pathlib import Path

from cli import process_file
from zombie_auditor import audit_agent_yield


def test_detects_zombie_agent() -> None:
    """Test that an agent with high cost and zero tasks is flagged as a zombie."""
    logs = [
        json.dumps({"agent_id": "agent-1", "compute_cost": 15.0, "tasks_completed": 0})
    ]
    result = audit_agent_yield(logs, cost_threshold=10.0, task_threshold=0)
    
    assert "agent-1" in result
    assert result["agent-1"]["is_zombie"] is True
    assert result["agent-1"]["total_cost"] == 15.0
    assert result["agent-1"]["total_tasks"] == 0


def test_ignores_healthy_agent() -> None:
    """Test that an agent with high cost but completed tasks is not flagged."""
    logs = [
        json.dumps({"agent_id": "agent-2", "compute_cost": 15.0, "tasks_completed": 10})
    ]
    result = audit_agent_yield(logs, cost_threshold=10.0, task_threshold=0)
    
    assert "agent-2" in result
    assert result["agent-2"]["is_zombie"] is False


def test_handles_malformed_json() -> None:
    """Test that malformed JSON strings are gracefully ignored."""
    logs = [
        "this is not valid json",
        json.dumps({"agent_id": "agent-3", "compute_cost": 5.0, "tasks_completed": 1})
    ]
    result = audit_agent_yield(logs)
    
    assert len(result) == 1
    assert "agent-3" in result


def test_handles_incomplete_json() -> None:
    """Test that JSON missing required keys is gracefully ignored."""
    logs = [
        json.dumps({"agent_id": "agent-4", "tasks_completed": 1}),
        json.dumps({"agent_id": "agent-5", "compute_cost": 5.0, "tasks_completed": 1})
    ]
    result = audit_agent_yield(logs)
    
    assert len(result) == 1
    assert "agent-5" in result
    assert "agent-4" not in result


def test_cli_process_file_integration(tmp_path: Path) -> None:
    """Test CLI file processing with a temporary JSONL file."""
    log_file = tmp_path / "test.log"
    logs = [
        {"agent_id": "agent-A", "compute_cost": 12.0, "tasks_completed": 0},
        {"agent_id": "agent-A", "compute_cost": 3.0, "tasks_completed": 0},
        {"agent_id": "agent-B", "compute_cost": 5.0, "tasks_completed": 5}
    ]
    
    with open(log_file, "w", encoding="utf-8") as f:
        for log in logs:
            f.write(json.dumps(log) + "\n")
    
    result = process_file(str(log_file), cost_threshold=10.0, task_threshold=0)
    
    assert "agent-A" in result
    assert result["agent-A"]["total_cost"] == 15.0
    assert result["agent-A"]["total_tasks"] == 0
    assert result["agent-A"]["is_zombie"] is True
    
    assert "agent-B" in result
    assert result["agent-B"]["is_zombie"] is False


def test_cli_empty_file_guard(tmp_path: Path) -> None:
    """Test that processing an empty file returns an empty dict without crashing."""
    empty_file = tmp_path / "empty.log"
    empty_file.touch()
    
    result = process_file(str(empty_file))
    
    assert result == {}