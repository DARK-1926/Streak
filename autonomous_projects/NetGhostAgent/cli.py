"""
NetGhostAgent CLI

This module provides the command-line interface for the NetGhostAgent system.
It uses memory-mapped file I/O for efficient processing of large log files,
streaming parsed events into the state-machine engine to detect anomalies.
"""

import argparse
import json
import mmap
import os
import sys
from dataclasses import asdict
from typing import Iterable, List, Optional

from engine import detect_anomalies
from models import Anomaly
from parser import parse_line


def _generate_lines(m: mmap.mmap) -> Iterable[str]:
    """
    Yields decoded lines from a memory-mapped file.

    Args:
        m: The memory-mapped file object.

    Yields:
        Decoded UTF-8 strings representing log lines.
    """
    while True:
        line_bytes = m.readline()
        if not line_bytes:
            break
        yield line_bytes.decode('utf-8', errors='ignore')


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for the NetGhostAgent CLI.

    Parses command-line arguments, reads the specified log file using
    memory mapping, and outputs detected anomalies as formatted JSON.

    Args:
        argv: Command-line arguments. Defaults to sys.argv[1:].

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = argparse.ArgumentParser(
        description="NetGhostAgent: Detect network anomalies from syslog files."
    )
    parser.add_argument(
        "--logfile",
        required=True,
        help="Path to the syslog file to analyze."
    )
    
    args = parser.parse_args(argv)
    logfile = args.logfile

    if not os.path.isfile(logfile):
        print(f"Error: File not found: {logfile}", file=sys.stderr)
        return 1

    try:
        file_size = os.path.getsize(logfile)
    except OSError as e:
        print(f"Error accessing file metadata: {e}", file=sys.stderr)
        return 1

    if file_size == 0:
        print(json.dumps([]))
        return 0

    try:
        with open(logfile, "rb") as f:
            # Length 0 maps the entire file; ACCESS_READ is cross-platform safe
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
                lines = _generate_lines(m)
                
                # Stream parsed events, filtering out None values
                events = (
                    event for line in lines 
                    if (event := parse_line(line)) is not None
                )
                
                anomalies: List[Anomaly] = detect_anomalies(events)
                
                # Serialize frozen dataclasses to dictionaries for JSON output
                anomaly_dicts = [asdict(a) for a in anomalies]
                print(json.dumps(anomaly_dicts, indent=2))
                
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 130
    except (OSError, ValueError, mmap.error) as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())