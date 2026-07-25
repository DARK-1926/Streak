"""
Strict TDD suite for the LicenseInfectionAuditor project.
Validates core scanning, I/O handling, and CLI integration without mocks.
"""
import io
import json
import pathlib
from typing import List

import pytest

import core
import io_handler
import cli


def test_scan_stream_clean() -> None:
    """
    Test scanning a stream with clean generated code.
    
    Creates an io.StringIO with 2 valid JSON lines containing 
    'generated_code' without GPL text. Asserts core.scan_stream 
    returns 0 infected.
    """
    lines: List[str] = [
        json.dumps({"generated_code": "print('hello world')"}),
        json.dumps({"generated_code": "def foo(): return 42"})
    ]
    stream = io.StringIO("\n".join(lines))
    result = core.scan_stream(stream)
    
    assert result['total_lines_processed'] == 2
    assert result['valid_generations'] == 2
    assert result['infected_generations'] == 0
    assert result['signature_counts'] == {}


def test_scan_stream_infected() -> None:
    """
    Test scanning a stream with GPL infected generated code.
    
    Creates an io.StringIO with 1 clean JSON line and 1 JSON line 
    where 'generated_code' contains 'GNU GENERAL PUBLIC LICENSE'. 
    Asserts infected_generations is 1 and signature_counts tracks it.
    """
    lines: List[str] = [
        json.dumps({"generated_code": "clean code here"}),
        json.dumps({"generated_code": "// GNU GENERAL PUBLIC LICENSE\nprint('infected')"})
    ]
    stream = io.StringIO("\n".join(lines))
    result = core.scan_stream(stream)
    
    assert result['total_lines_processed'] == 2
    assert result['valid_generations'] == 2
    assert result['infected_generations'] == 1
    assert result['signature_counts'].get('GNU GENERAL PUBLIC LICENSE') == 1


def test_scan_stream_malformed_json() -> None:
    """
    Test scanning a stream with malformed JSON and missing keys.
    
    Passes an io.StringIO with invalid JSON and missing keys. 
    Asserts it processes without crashing and returns 0 valid generations.
    """
    lines: List[str] = [
        "this is not json",
        json.dumps({"other_key": "value"}),
        "{broken json: "
    ]
    stream = io.StringIO("\n".join(lines))
    result = core.scan_stream(stream)
    
    assert result['total_lines_processed'] == 3
    assert result['valid_generations'] == 0
    assert result['infected_generations'] == 0
    assert result['signature_counts'] == {}


def test_yield_log_lines_empty_file(tmp_path: pathlib.Path) -> None:
    """
    Test yielding lines from an empty file.
    
    Creates an empty file using tmp_path. Passes it to 
    io_handler.yield_log_lines. Asserts it returns an empty 
    list/generator without crashing (validates win32 guard).
    """
    filepath = tmp_path / "empty.jsonl"
    filepath.touch()
    
    lines = list(io_handler.yield_log_lines(str(filepath)))
    assert lines == []


def test_yield_log_lines_valid_file(tmp_path: pathlib.Path) -> None:
    """
    Test yielding lines from a valid log file.
    
    Writes 3 lines to a file in tmp_path. Asserts yield_log_lines 
    yields exactly those 3 decoded strings.
    """
    filepath = tmp_path / "valid.jsonl"
    content = "line1\nline2\nline3\n"
    filepath.write_text(content, encoding='utf-8')
    
    lines = list(io_handler.yield_log_lines(str(filepath)))
    assert lines == ["line1", "line2", "line3"]


def test_cli_integration(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture) -> None:
    """
    Test CLI integration with a valid JSONL file.
    
    Writes valid JSONL to a file in tmp_path. Calls cli.main([str(filepath)]). 
    Asserts return code is 0 and capsys.readouterr().out contains valid 
    JSON with the correct counts.
    """
    filepath = tmp_path / "integration.jsonl"
    lines: List[str] = [
        json.dumps({"generated_code": "clean code"}),
        json.dumps({"generated_code": "GPLV3 infected code"})
    ]
    filepath.write_text("\n".join(lines), encoding='utf-8')
    
    exit_code = cli.main([str(filepath)])
    assert exit_code == 0
    
    captured = capsys.readouterr()
    output_data = json.loads(captured.out)
    
    assert output_data['total_lines_processed'] == 2
    assert output_data['valid_generations'] == 2
    assert output_data['infected_generations'] == 1
    assert output_data['signature_counts'].get('GPLV3') == 1