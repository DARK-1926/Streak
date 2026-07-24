"""
Test suite for DiskChurnAuditor.

Validates pure logic, I/O behavior, and CLI integration using pytest.
"""
import pytest
from pathlib import Path
from typing import List

from disk_churn.core import analyze_write_churn, ChurnMetrics
from disk_churn.io_handler import stream_log_file
from disk_churn.cli import main


def test_analyze_write_churn_pure_logic() -> None:
    """
    Test pure logic of analyze_write_churn with valid, malformed, 
    and missing key lines.
    """
    lines: List[str] = [
        '{"pid": 101, "bytes": 1024}',
        '{"pid": 101, "bytes": 256}',
        '{"pid": 102, "bytes": 512}',
        'not a json',
        '{"pid": 103}',
        '{"bytes": 100}',
        '{"pid": "101", "bytes": 100}'
    ]
    metrics = analyze_write_churn(lines)
    
    assert len(metrics) == 2
    assert metrics["101"].total_bytes == 1380
    assert metrics["101"].write_count == 3
    assert metrics["101"].micro_writes == 2
    
    assert metrics["102"].total_bytes == 512
    assert metrics["102"].write_count == 1
    assert metrics["102"].micro_writes == 0


def test_stream_log_file_valid(tmp_path: Path) -> None:
    """Test streaming a valid JSONL file."""
    log_file = tmp_path / "valid.log"
    content = '{"pid": 1, "bytes": 10}\n{"pid": 2, "bytes": 20}\n'
    log_file.write_text(content, encoding='utf-8')
    
    lines = list(stream_log_file(str(log_file)))
    
    assert len(lines) == 2
    assert lines[0] == '{"pid": 1, "bytes": 10}\n'
    assert lines[1] == '{"pid": 2, "bytes": 20}\n'


def test_stream_log_file_empty_win32_guard(tmp_path: Path) -> None:
    """Test that streaming an empty file yields nothing and does not crash."""
    log_file = tmp_path / "empty.log"
    log_file.write_text("", encoding='utf-8')
    
    lines = list(stream_log_file(str(log_file)))
    
    assert len(lines) == 0


def test_stream_log_file_missing() -> None:
    """Test that FileNotFoundError is raised for a missing file."""
    with pytest.raises(FileNotFoundError):
        list(stream_log_file("nonexistent_file.log"))


def test_cli_main_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test CLI main function with a valid log file."""
    log_file = tmp_path / "cli_valid.log"
    log_file.write_text('{"pid": 999, "bytes": 100}\n', encoding='utf-8')
    
    exit_code = main([str(log_file)])
    captured = capsys.readouterr()
    
    assert exit_code == 0
    assert "999" in captured.out
    assert "Total Bytes" in captured.out


def test_cli_main_missing_file(capsys: pytest.CaptureFixture[str]) -> None:
    """Test CLI main function with a missing log file."""
    exit_code = main(["nonexistent.log"])
    captured = capsys.readouterr()
    
    assert exit_code == 1
    assert "Error:" in captured.err
    assert "Log file not found" in captured.err