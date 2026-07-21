"""
CLI and I/O module for ZombieComputeAuditor.

This module handles file system operations, utilizing memory-mapped I/O
for efficient processing of large JSONL log files, and injects the data
into the pure core logic.
"""

import argparse
import json
import mmap
import os
import sys
from typing import Any, Dict

from zombie_auditor import audit_agent_yield


def process_file(
    filepath: str, 
    cost_threshold: float = 10.0, 
    task_threshold: int = 0
) -> Dict[str, Dict[str, Any]]:
    """
    Process a JSONL log file using memory-mapped I/O and audit agent yields.
    
    Includes an explicit guard for empty files to prevent exceptions on Windows.
    
    Args:
        filepath: Path to the JSONL log file.
        cost_threshold: Minimum compute cost to flag an agent as a zombie.
        task_threshold: Maximum tasks completed to flag an agent as a zombie.
        
    Returns:
        A dictionary containing aggregated stats and zombie flags per agent.
    """
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return {}
        
    with open(filepath, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            lines = (line.decode('utf-8') for line in iter(mm.readline, b''))
            return audit_agent_yield(lines, cost_threshold, task_threshold)


def main() -> None:
    """
    Main entry point for the ZombieComputeAuditor CLI.
    
    Parses command-line arguments, processes the specified log file,
    and prints the audit results as JSON to stdout.
    """
    parser = argparse.ArgumentParser(
        description="Audit agent telemetry logs to identify zombie compute instances."
    )
    parser.add_argument(
        "filepath", 
        type=str, 
        help="Path to the JSONL log file to process."
    )
    parser.add_argument(
        "--cost-threshold", 
        type=float, 
        default=10.0, 
        help="Minimum total compute cost to consider an agent a zombie (default: 10.0)."
    )
    parser.add_argument(
        "--task-threshold", 
        type=int, 
        default=0, 
        help="Maximum total tasks completed to consider an agent a zombie (default: 0)."
    )
    
    args = parser.parse_args()
    
    try:
        results = process_file(
            filepath=args.filepath,
            cost_threshold=args.cost_threshold,
            task_threshold=args.task_threshold
        )
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()