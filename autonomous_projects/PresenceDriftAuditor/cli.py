"""
Command-line interface and memory-mapped I/O handler for the PresenceDriftAuditor.
"""

import argparse
import json
import mmap
import os
import sys
from dataclasses import asdict
from typing import Iterable

from engine import audit_presence
from models import LogEvent, parse_log_line


def stream_log_events(filepath: str) -> Iterable[LogEvent]:
    """
    Streams and parses log events from a file using memory-mapped I/O.
    
    Guards against win32 empty-file crashes by checking file size first.
    
    Args:
        filepath: Path to the JSONL log file.
        
    Yields:
        Valid LogEvent objects parsed from the file.
    """
    if os.path.getsize(filepath) == 0:
        return
        
    with open(filepath, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for line in iter(mm.readline, b""):
                decoded_line = line.decode('utf-8', errors='ignore')
                event = parse_log_line(decoded_line)
                if event is not None:
                    yield event


def run_audit(filepath: str, flap_threshold: float) -> None:
    """
    Executes the presence audit and prints the results as a JSON array.
    
    Args:
        filepath: Path to the JSONL log file.
        flap_threshold: Maximum time in seconds between disconnect and 
                        reconnect to be considered a flap.
    """
    events = stream_log_events(filepath)
    reports = audit_presence(events, flap_threshold_sec=flap_threshold)
    
    # Convert dict of dataclasses to a list of dicts for JSON serialization
    serializable_reports = [asdict(report) for report in reports.values()]
    
    print(json.dumps(serializable_reports, indent=2))


def main() -> None:
    """
    CLI entrypoint for the PresenceDriftAuditor.
    
    Parses command-line arguments and initiates the audit process.
    """
    parser = argparse.ArgumentParser(
        description="Audit agent presence and stability from JSONL logs."
    )
    parser.add_argument(
        "filepath", 
        type=str, 
        help="Path to the JSONL log file to audit."
    )
    parser.add_argument(
        "--flap-threshold", 
        type=float, 
        default=5.0,
        help="Maximum seconds between disconnect/reconnect to count as a flap (default: 5.0)."
    )
    
    args = parser.parse_args()
    
    try:
        run_audit(args.filepath, args.flap_threshold)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()