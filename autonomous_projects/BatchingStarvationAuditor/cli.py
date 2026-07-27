"""
CLI entry point and memory-mapped I/O wrapper for BatchingStarvationAuditor.
"""

import os
import mmap
import argparse
import sys
import json
from typing import Any, Dict

from batching_auditor import calculate_starvation_metrics, parse_event


def process_log_file(filepath: str, threshold_ms: int) -> Dict[str, Any]:
    """
    Process a JSONL log file using memory-mapped I/O and calculate starvation metrics.

    Args:
        filepath: Path to the JSONL log file.
        threshold_ms: The wait time threshold in milliseconds.

    Returns:
        A dictionary containing the calculated starvation metrics.
    """
    if os.path.getsize(filepath) == 0:
        return {
            "total_requests": 0,
            "starved_requests": 0,
            "total_wait_ms": 0,
            "max_wait_ms": 0,
            "average_wait_ms": 0.0,
            "batch_starvation_counts": {}
        }

    with open(filepath, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            def event_generator():
                for line in iter(mm.readline, b""):
                    event = parse_event(line.decode('utf-8'))
                    if event is not None:
                        yield event
            
            return calculate_starvation_metrics(event_generator(), threshold_ms)


def main() -> None:
    """
    CLI entry point for BatchingStarvationAuditor.
    Parses arguments, processes the log file, and prints metrics as JSON.
    """
    parser = argparse.ArgumentParser(
        description="Audit ML inference logs for batching starvation."
    )
    parser.add_argument(
        "filepath", 
        type=str, 
        help="Path to the JSONL inference log file."
    )
    parser.add_argument(
        "--threshold", 
        type=int, 
        default=100, 
        help="Wait time threshold in ms above which a request is starved (default: 100)."
    )
    
    args = parser.parse_args()
    
    try:
        metrics = process_log_file(args.filepath, args.threshold)
        print(json.dumps(metrics, indent=2))
    except FileNotFoundError:
        print(f"Error: File not found: {args.filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()