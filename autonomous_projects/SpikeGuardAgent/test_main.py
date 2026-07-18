"""
Deterministic validation suite for SpikeGuardAgent.
Tests core algorithms, safe I/O layer, and CLI wiring without using unittest.mock.
"""

import io
from pathlib import Path
from typing import List, Dict, Any

import pytest

from sentinel_core import detect_loops, detect_frequency_spikes
from sentinel_io import stream_log_lines, extract_timestamps
from main import run_analysis


def test_detect_loops() -> None:
    """Test detection of a repeating 3-line sequence."""
    sequence = ["line A", "line B", "line C"]
    lines = sequence * 6
    anomalies = detect_loops(lines)
    assert isinstance(anomalies, list)
    assert len(anomalies) > 0, "Expected at least one loop anomaly to be detected"


def test_detect_loops_no_anomaly() -> None:
    """Test that unique strings do not trigger loop detection."""
    lines = [f"unique line {i}" for i in range(100)]
    anomalies = detect_loops(lines)
    assert isinstance(anomalies, list)
    assert len(anomalies) == 0, "Expected no anomalies for unique lines"


def test_detect_frequency_spikes() -> None:
    """Test detection of frequency spikes within a time window."""
    base_time = 1714564800.0
    # 150 events occurring evenly within a 10-second window
    timestamps = [base_time + (i * 10.0 / 150.0) for i in range(150)]
    
    anomalies = detect_frequency_spikes(timestamps)
        
    assert isinstance(anomalies, list)
    assert len(anomalies) > 0, "Expected a frequency spike anomaly to be detected"


def test_stream_log_lines_memory() -> None:
    """Test streaming lines from an in-memory StringIO object."""
    stream = io.StringIO("line1\nline2\n")
    lines = list(stream_log_lines(stream))
    
    assert len(lines) == 2
    # Assert it yields the exact strings (handling potential newline stripping)
    assert lines == ["line1\n", "line2\n"] or lines == ["line1", "line2"]


def test_stream_log_lines_mmap_and_empty(tmp_path: Path) -> None:
    """Test streaming from real files using mmap and handling empty files."""
    try:
        # 1. Test 0-byte file (verifies win32 safeguard against empty files)
        empty_file = tmp_path / "empty.log"
        empty_file.touch()
        
        empty_lines = list(stream_log_lines(str(empty_file)))
        assert len(empty_lines) == 0, "Expected 0-byte file to yield nothing"

        # 2. Test multi-line file (verifies mmap reading)
        multi_file = tmp_path / "multi.log"
        multi_file.write_text("alpha\nbeta\ngamma\n")
        
        multi_lines = list(stream_log_lines(str(multi_file)))
        assert len(multi_lines) == 3
        assert multi_lines[0].strip() == "alpha"
        assert multi_lines[1].strip() == "beta"
        assert multi_lines[2].strip() == "gamma"
    except Exception as e:
        pytest.fail(f"File I/O operations failed unexpectedly: {e}")


def test_extract_timestamps() -> None:
    """Test extraction of timestamps from log lines."""
    stream = io.StringIO("[2024-05-01T12:00:00] Event\n[2024-05-01T12:00:01] Event")
    timestamps = list(extract_timestamps(stream))
    
    assert len(timestamps) == 2, "Expected exactly two timestamps to be extracted"
    assert all(isinstance(t, float) for t in timestamps), "Timestamps must be floats"
    assert timestamps[1] > timestamps[0], "Second timestamp should be greater than the first"


def test_run_analysis_integration() -> None:
    """Integration test for run_analysis with repetitive timestamped lines."""
    lines = []
    # Create 150 repetitions of a 3-line sequence (450 lines total)
    # All sharing the same timestamp to guarantee both loop and spike detection
    for _ in range(150):
        lines.append("[2024-05-01T12:00:00] Event A")
        lines.append("[2024-05-01T12:00:00] Event B")
        lines.append("[2024-05-01T12:00:00] Event C")
    
    stream = io.StringIO("\n".join(lines))
    
    try:
        report = run_analysis(stream)
    except Exception as e:
        pytest.fail(f"run_analysis failed unexpectedly: {e}")
    
    assert isinstance(report, dict), "run_analysis must return a dictionary"
    assert "loops" in report, "Report must contain 'loops' key"
    assert "spikes" in report, "Report must contain 'spikes' key"
    
    # Assert valid data is present
    assert isinstance(report["loops"], list)
    assert isinstance(report["spikes"], list)
    assert len(report["loops"]) > 0, "Expected loop anomalies in integration test"
    assert len(report["spikes"]) > 0, "Expected spike anomalies in integration test"