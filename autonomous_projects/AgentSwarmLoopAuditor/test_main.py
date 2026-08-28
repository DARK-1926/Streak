import os
import json
import tempfile
import pytest
from typing import List
import importlib.util

_spec = importlib.util.spec_from_file_location("local_io", os.path.join(os.path.dirname(__file__), "io.py"))
_local_io = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_local_io)
stream_jsonl = _local_io.stream_jsonl

from models import AgentAction, LoopReport
from core import parse_action, audit_sessions


def test_stream_jsonl_valid_and_invalid() -> None:
    """Test streaming JSONL with valid and invalid lines."""
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write('{"session_id": "s1", "tool_name": "read", "args_hash": "h1", "tokens_used": 10}\n')
            f.write('this is not valid json\n')
            f.write('{"session_id": "s1", "tool_name": "write", "args_hash": "h2", "tokens_used": 20}\n')
        
        lines: List[str] = list(stream_jsonl(path))
        assert len(lines) == 3
        assert "this is not valid json" in lines[1]
    finally:
        os.unlink(path)


def test_stream_jsonl_empty() -> None:
    """Test streaming an empty JSONL file."""
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    
    try:
        lines: List[str] = list(stream_jsonl(path))
        assert lines == []
    finally:
        os.unlink(path)


def test_parse_action_valid() -> None:
    """Test parsing a valid action string."""
    raw = '{"session_id": "s1", "tool_name": "read", "args_hash": "h1", "tokens_used": 10}'
    action = parse_action(raw)
    assert isinstance(action, AgentAction)
    assert action.session_id == "s1"
    assert action.tool_name == "read"


def test_parse_action_invalid() -> None:
    """Test parsing an invalid action string."""
    raw = "not a json string"
    try:
        action = parse_action(raw)
        assert action is None
    except (ValueError, json.JSONDecodeError, TypeError):
        pass  # Raising an exception is also acceptable for invalid input


def test_audit_sessions_exact_loop() -> None:
    """Test audit_sessions detects an exact loop."""
    actions = [
        AgentAction(session_id="s1", tool_name="read_file", args_hash="hash1", tokens_used=100)
        for _ in range(5)
    ]
    
    report = audit_sessions(actions)
    assert isinstance(report, LoopReport)
    assert report.exact_loops >= 1
    assert report.wasted_tokens >= 400  # 4 wasted calls * 100 tokens


def test_audit_sessions_alternating_loop() -> None:
    """Test audit_sessions detects an A-B thrashing loop."""
    actions = [
        AgentAction(session_id="s2", tool_name="edit_file", args_hash="hashA", tokens_used=50),
        AgentAction(session_id="s2", tool_name="read_file", args_hash="hashB", tokens_used=50),
        AgentAction(session_id="s2", tool_name="edit_file", args_hash="hashA", tokens_used=50),
        AgentAction(session_id="s2", tool_name="read_file", args_hash="hashB", tokens_used=50),
        AgentAction(session_id="s2", tool_name="edit_file", args_hash="hashA", tokens_used=50),
        AgentAction(session_id="s2", tool_name="read_file", args_hash="hashB", tokens_used=50),
    ]
    
    report = audit_sessions(actions)
    assert isinstance(report, LoopReport)
    assert report.alternating_loops >= 1
    assert report.wasted_tokens >= 200  # At least some wasted tokens


def test_audit_sessions_combined() -> None:
    """Test audit_sessions with both exact and alternating loops."""
    exact_actions = [
        AgentAction(session_id="s1", tool_name="read_file", args_hash="hash1", tokens_used=100)
        for _ in range(5)
    ]
    
    thrash_actions = [
        AgentAction(session_id="s2", tool_name="edit_file", args_hash="hashA", tokens_used=50),
        AgentAction(session_id="s2", tool_name="read_file", args_hash="hashB", tokens_used=50),
        AgentAction(session_id="s2", tool_name="edit_file", args_hash="hashA", tokens_used=50),
        AgentAction(session_id="s2", tool_name="read_file", args_hash="hashB", tokens_used=50),
        AgentAction(session_id="s2", tool_name="edit_file", args_hash="hashA", tokens_used=50),
        AgentAction(session_id="s2", tool_name="read_file", args_hash="hashB", tokens_used=50),
    ]
    
    all_actions = exact_actions + thrash_actions
    report = audit_sessions(all_actions)
    
    assert isinstance(report, LoopReport)
    assert report.exact_loops >= 1
    assert report.alternating_loops >= 1
    assert report.wasted_tokens >= 600