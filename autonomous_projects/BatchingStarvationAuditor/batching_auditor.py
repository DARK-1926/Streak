"""
Pure functional core for BatchingStarvationAuditor.
Contains single-pass metric aggregation logic decoupled from file I/O.
"""

import json
from typing import Any, Dict, Iterable, Optional


def parse_event(line: str) -> Optional[Dict[str, Any]]:
    """
    Safely parse a JSON string representing an inference event.

    Validates that the required keys ('request_id', 'queue_wait_ms', and 'batch_id') exist.

    Args:
        line: A JSON formatted string.

    Returns:
        A dictionary of the parsed event, or None if the string is invalid 
        or missing required keys.
    """
    try:
        event = json.loads(line)
        # Validate required keys exist and event is a mapping
        _ = event['request_id']
        _ = event['queue_wait_ms']
        _ = event['batch_id']
        return event
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def calculate_starvation_metrics(events: Iterable[Dict[str, Any]], threshold_ms: int) -> Dict[str, Any]:
    """
    Perform a strict single-pass accumulation of starvation metrics.

    Args:
        events: An iterable of parsed event dictionaries.
        threshold_ms: The wait time threshold in milliseconds above which 
                      a request is considered starved.

    Returns:
        A summary dictionary containing total_requests, starved_requests, 
        total_wait_ms, max_wait_ms, average_wait_ms, and batch_starvation_counts.
    """
    total_requests = 0
    starved_requests = 0
    total_wait_ms = 0
    max_wait_ms = 0
    batch_starvation_counts: Dict[Any, int] = {}

    for event in events:
        total_requests += 1
        
        wait_ms = event['queue_wait_ms']
        total_wait_ms += wait_ms
        
        if wait_ms > max_wait_ms:
            max_wait_ms = wait_ms
            
        if wait_ms > threshold_ms:
            starved_requests += 1
            batch_id = event['batch_id']
            batch_starvation_counts[batch_id] = batch_starvation_counts.get(batch_id, 0) + 1

    average_wait_ms = (total_wait_ms / total_requests) if total_requests > 0 else 0.0

    return {
        'total_requests': total_requests,
        'starved_requests': starved_requests,
        'total_wait_ms': total_wait_ms,
        'max_wait_ms': max_wait_ms,
        'average_wait_ms': average_wait_ms,
        'batch_starvation_counts': batch_starvation_counts
    }