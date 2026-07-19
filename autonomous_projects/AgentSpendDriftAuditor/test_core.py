import json
import pathlib
from decimal import Decimal
from typing import List

import pytest

from core import calculate_exact_cost, detect_agent_spikes, run_audit


def test_calculate_exact_cost() -> None:
    """
    Test exact decimal accumulation without float drift.
    
    Passes an in-memory list of JSON strings with costs like '0.1' and '0.2'.
    Asserts result is exactly Decimal('0.3').
    """
    lines: List[str] = [
        '{"cost": "0.1"}',
        '{"cost": "0.2"}',
        '{"cost": "0.0"}',
        'invalid json line',
        '{"no_cost_key": true}'
    ]
    result = calculate_exact_cost(lines)
    assert result == Decimal('0.3')


def test_detect_agent_spikes() -> None:
    """
    Test sliding window spike detection.
    
    Passes in-memory JSON strings with 150 events for 'agent-1' within 10 seconds.
    Asserts a spike is detected.
    """
    lines: List[str] = []
    for i in range(150):
        lines.append(json.dumps({
            'agent_id': 'agent-1',
            'timestamp': 1000 + (i * 0.05)
        }))
        
    for i in range(5):
        lines.append(json.dumps({
            'agent_id': 'agent-2',
            'timestamp': 1000 + i
        }))
        
    spikes = detect_agent_spikes(lines, window_sec=10, threshold=100)
    
    assert len(spikes) >= 1
    assert spikes[0]['agent_id'] == 'agent-1'
    assert spikes[0]['event_count'] >= 100


def test_run_audit_empty_file(tmp_path: pathlib.Path) -> None:
    """
    Test that run_audit handles 0-byte files safely.
    
    Creates a 0-byte file and asserts run_audit returns safely 
    without ValueError, testing the win32 guard.
    """
    empty_file = tmp_path / "empty.jsonl"
    empty_file.touch()
    
    result = run_audit(str(empty_file), window_sec=60, threshold=100)
    
    assert result['exact_cost'] == '0.0'
    assert result['spikes'] == []


def test_run_audit_file_not_found() -> None:
    """
    Test that run_audit raises FileNotFoundError for missing files.
    
    Asserts run_audit raises FileNotFoundError when given a non-existent path.
    """
    with pytest.raises(FileNotFoundError):
        run_audit("non_existent_file.jsonl", window_sec=60, threshold=100)


def test_run_audit_integration(tmp_path: pathlib.Path) -> None:
    """
    Test end-to-end audit with a populated JSONL file.
    
    Writes 200 valid JSONL lines to a file in tmp_path. Calls run_audit.
    Asserts the returned dictionary contains the correct Decimal string 
    and a populated spikes list.
    """
    log_file = tmp_path / "audit.jsonl"
    lines: List[str] = []
    
    for i in range(200):
        lines.append(json.dumps({
            'agent_id': 'agent-X',
            'timestamp': 5000 + (i * 0.01),
            'cost': '0.1'
        }))
        
    log_file.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    
    result = run_audit(str(log_file), window_sec=10, threshold=100)
    
    assert result['exact_cost'] == '20.0'
    assert len(result['spikes']) >= 1
    assert result['spikes'][0]['agent_id'] == 'agent-X'