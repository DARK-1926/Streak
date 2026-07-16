"""
Strict unit test suite for the SlopFilterAgent project.
Validates core logic using io.StringIO and integration tests with mmap.
"""

import io
from pathlib import Path

import pytest

from heuristics import calculate_shannon_entropy, calculate_repetition_ratio
from csv_processor import parse_csv_content, format_csv_content
from agent import filter_high_signal_comments
from main import process_file


def test_calculate_shannon_entropy() -> None:
    """Test entropy calculation for repetitive vs random strings."""
    repetitive = "aaaaaaaaaa"
    random_str = "abcdefghij"
    
    entropy_rep = calculate_shannon_entropy(repetitive)
    entropy_rand = calculate_shannon_entropy(random_str)
    
    assert entropy_rep == 0.0
    assert entropy_rand > entropy_rep


def test_calculate_repetition_ratio() -> None:
    """Test repetition ratio for bot-like vs human-like strings."""
    bot_str = "bot bot bot"
    human_str = "hello world this is a test"
    
    ratio_bot = calculate_repetition_ratio(bot_str)
    ratio_human = calculate_repetition_ratio(human_str)
    
    assert ratio_bot > ratio_human
    assert ratio_bot > 0.5


def test_parse_csv_content() -> None:
    """Test CSV parsing using an in-memory string stream."""
    csv_data = "id,text\n1,hello\n2,bot bot bot"
    stream = io.StringIO(csv_data)
    
    result = parse_csv_content(stream)
    
    assert len(result) == 2
    assert result[0] == {"id": "1", "text": "hello"}
    assert result[1] == {"id": "2", "text": "bot bot bot"}


def test_filter_high_signal_comments() -> None:
    """Test filtering logic removes slop and keeps high-signal comments."""
    comments = [
        {"id": "1", "text": "hello world this is a test"},
        {"id": "2", "text": "bot bot bot bot bot bot bot bot bot bot"}
    ]
    
    filtered = filter_high_signal_comments(comments)
    
    assert len(filtered) == 1
    assert filtered[0]["id"] == "1"
    assert filtered[0]["text"] == "hello world this is a test"


def test_format_csv_content() -> None:
    """Test CSV formatting writes correct structure to an output stream."""
    data = [{"id": "1", "text": "hello"}]
    out_stream = io.StringIO()
    
    format_csv_content(data, out_stream)
    
    output = out_stream.getvalue()
    assert "id,text" in output
    assert "1,hello" in output


def test_process_file_integration(tmp_path: Path) -> None:
    """Integration test for process_file using real files and mmap."""
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"
    
    csv_content = (
        "id,text\n"
        "1,This is a genuine human comment with varied vocabulary.\n"
        "2,bot bot bot bot bot bot bot bot bot bot bot bot bot bot\n"
        "3,Another thoughtful response that should pass the filter.\n"
    )
    input_file.write_text(csv_content, encoding="utf-8")
    
    process_file(str(input_file), str(output_file), "text")
    
    assert output_file.exists()
    output_content = output_file.read_text(encoding="utf-8")
    
    assert "bot bot bot" not in output_content
    assert "genuine human comment" in output_content
    assert "thoughtful response" in output_content