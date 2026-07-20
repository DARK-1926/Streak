from __future__ import annotations

import argparse
import json
import sys

from io_engine import stream_log_lines
from sentinel_core import analyze_provisioning_spikes


def main(argv: list[str] | None = None) -> int:
    """
    CLI entry point for CloudTrailSpikeAuditor.

    Parses command-line arguments, streams the specified CloudTrail JSONL log file,
    and analyzes it for provisioning spikes.

    Args:
        argv: Optional list of command-line arguments. Defaults to sys.argv[1:].

    Returns:
        int: 0 on success, 1 on file access errors.
    """
    parser = argparse.ArgumentParser(
        description="Detect AWS billing anomalies caused by runaway infrastructure provisioning."
    )
    parser.add_argument(
        "logfile",
        type=str,
        help="Path to the CloudTrail JSONL log file."
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=100,
        help="Maximum allowed count before an event is flagged as a spike (default: 100)."
    )

    args = parser.parse_args(argv)

    try:
        lines = stream_log_lines(args.logfile)
        result = analyze_provisioning_spikes(lines, spike_threshold=args.threshold)
        print(json.dumps(result, indent=4))
        return 0
    except FileNotFoundError:
        print(f"Error: Log file not found: '{args.logfile}'", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Error: Unable to access log file: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())