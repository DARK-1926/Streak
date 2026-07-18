import argparse
import io
import json
import sys
from typing import Any, Dict, Union

import sentinel_core
import sentinel_io


def run_analysis(source: Union[str, io.TextIOBase]) -> Dict[str, Any]:
    """
    Runs loop and frequency spike detection on the given log source.
    
    Processes the source in two passes to maintain O(1) memory usage
    and avoid itertools.tee buffering.
    
    Args:
        source: A filepath string or an io.TextIOBase stream.
        
    Returns:
        A JSON-serializable dictionary containing the combined anomaly reports.
    """
    if isinstance(source, str):
        # Pass 1: Detect sequence loops
        lines_pass1 = sentinel_io.stream_log_lines(source)
        loops = sentinel_core.detect_loops(lines_pass1)
        
        # Pass 2: Detect frequency spikes
        lines_pass2 = sentinel_io.stream_log_lines(source)
        timestamps = sentinel_io.extract_timestamps(lines_pass2)
        spikes = sentinel_core.detect_frequency_spikes(timestamps)
        
    elif isinstance(source, io.TextIOBase):
        # Pass 1: Detect sequence loops
        loops = sentinel_core.detect_loops(source)
        
        # Reset stream for Pass 2
        source.seek(0)
        
        # Pass 2: Detect frequency spikes
        timestamps = sentinel_io.extract_timestamps(source)
        spikes = sentinel_core.detect_frequency_spikes(timestamps)
    else:
        raise TypeError("source must be a filepath string or io.TextIOBase")
        
    return {
        "loops": loops,
        "spikes": spikes
    }


def main() -> None:
    """
    CLI entry point for SpikeGuardAgent.
    
    Parses command-line arguments, runs the analysis, and prints 
    the JSON report to stdout.
    """
    parser = argparse.ArgumentParser(
        description="SpikeGuardAgent: Analyze logs for AI sycophancy loops and billing spikes."
    )
    parser.add_argument(
        "filepath", 
        type=str, 
        help="Path to the log file to analyze."
    )
    
    args = parser.parse_args()
    
    try:
        report = run_analysis(args.filepath)
        print(json.dumps(report, indent=2))
    except FileNotFoundError:
        print(f"Error: File not found - {args.filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()