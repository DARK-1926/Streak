import json
import mmap
import os
from collections import defaultdict, deque
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Iterable, List


def calculate_exact_cost(lines: Iterable[str]) -> Decimal:
    """
    Calculate the exact total cost from an iterable of JSON lines.
    
    Args:
        lines: An iterable of JSON-formatted strings.
        
    Returns:
        A Decimal representing the total accumulated cost.
    """
    total_cost = Decimal('0.0')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            cost_str = str(data.get('cost', '0.0'))
            total_cost += Decimal(cost_str)
        except (json.JSONDecodeError, InvalidOperation, TypeError, ValueError):
            continue
    return total_cost


def detect_agent_spikes(lines: Iterable[str], window_sec: int, threshold: int) -> List[Dict[str, Any]]:
    """
    Detect billing spikes using a sliding window approach.
    
    Args:
        lines: An iterable of JSON-formatted strings.
        window_sec: The time window in seconds for spike detection.
        threshold: The number of events required to trigger a spike.
        
    Returns:
        A list of dictionaries containing spike event details.
    """
    agent_timestamps: Dict[str, deque] = defaultdict(deque)
    spikes: List[Dict[str, Any]] = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            agent_id = data.get('agent_id')
            timestamp = data.get('timestamp')
            
            if agent_id is None or timestamp is None:
                continue
                
            dq = agent_timestamps[agent_id]
            dq.append(timestamp)
            
            while dq and (timestamp - dq[0] > window_sec):
                dq.popleft()
                
            if len(dq) >= threshold:
                spikes.append({
                    'agent_id': agent_id,
                    'spike_timestamp': timestamp,
                    'event_count': len(dq)
                })
                dq.clear()
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
            
    return spikes


def run_audit(file_path: str, window_sec: int, threshold: int) -> Dict[str, Any]:
    """
    Orchestrate the audit process using memory-mapped file I/O.
    
    Args:
        file_path: Path to the JSONL log file.
        window_sec: The time window in seconds for spike detection.
        threshold: The number of events required to trigger a spike.
        
    Returns:
        A dictionary containing the exact cost and detected spikes.
    """
    if os.path.getsize(file_path) == 0:
        return {
            'exact_cost': str(Decimal('0.0')),
            'spikes': []
        }
        
    with open(file_path, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
            def line_generator_pass1() -> Iterable[str]:
                for line in iter(m.readline, b""):
                    yield line.decode('utf-8')
                    
            exact_cost = calculate_exact_cost(line_generator_pass1())
            
            m.seek(0)
            
            def line_generator_pass2() -> Iterable[str]:
                for line in iter(m.readline, b""):
                    yield line.decode('utf-8')
                    
            spikes = detect_agent_spikes(line_generator_pass2(), window_sec, threshold)
            
    return {
        'exact_cost': str(exact_cost),
        'spikes': spikes
    }