import json
from dataclasses import dataclass
from typing import Dict, Iterable


@dataclass
class ChurnMetrics:
    """
    Data class representing disk write churn metrics for a specific process.
    
    Attributes:
        total_bytes: The total number of bytes written by the process.
        write_count: The total number of write operations performed.
        micro_writes: The number of write operations under 512 bytes.
    """
    total_bytes: int = 0
    write_count: int = 0
    micro_writes: int = 0


def analyze_write_churn(log_lines: Iterable[str]) -> Dict[str, ChurnMetrics]:
    """
    Analyzes write churn from an iterable of JSONL log lines.
    
    Performs a single-pass O(N) aggregation of write metrics per process ID.
    Malformed lines or lines missing required keys are gracefully ignored.
    
    Args:
        log_lines: An iterable of strings, where each string is a JSON object.
        
    Returns:
        A dictionary mapping process IDs (as strings) to their ChurnMetrics.
    """
    metrics: Dict[str, ChurnMetrics] = {}
    
    for line in log_lines:
        try:
            data = json.loads(line)
            pid = str(data['pid'])
            bytes_written = int(data['bytes'])
            
            if pid not in metrics:
                metrics[pid] = ChurnMetrics()
                
            metrics[pid].total_bytes += bytes_written
            metrics[pid].write_count += 1
            
            if bytes_written < 512:
                metrics[pid].micro_writes += 1
                
        except (json.JSONDecodeError, ValueError, TypeError, KeyError):
            continue
            
    return metrics