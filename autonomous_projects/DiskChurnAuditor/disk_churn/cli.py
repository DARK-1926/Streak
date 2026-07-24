import argparse
import sys
from typing import List

from .core import analyze_write_churn
from .io_handler import stream_log_file


def main(argv: List[str]) -> int:
    """
    CLI entry point for the DiskChurnAuditor.

    Parses command-line arguments, streams the specified log file,
    and outputs a formatted report of high-churn processes.

    Args:
        argv: A list of command-line arguments.

    Returns:
        An integer exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Analyze disk write churn from JSONL telemetry logs."
    )
    parser.add_argument(
        "logfile",
        type=str,
        help="Path to the JSONL telemetry log file to analyze."
    )

    args = parser.parse_args(argv)

    try:
        log_stream = stream_log_file(args.logfile)
        metrics = analyze_write_churn(log_stream)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    if not metrics:
        print("No write churn data found in the provided log file.")
        return 0

    sorted_metrics = sorted(
        metrics.items(),
        key=lambda item: item[1].micro_writes,
        reverse=True
    )

    header = f"{'PID':<10} | {'Total Bytes':<15} | {'Write Count':<15} | {'Micro Writes':<15}"
    print(header)
    print("-" * len(header))

    for pid, data in sorted_metrics:
        print(
            f"{pid:<10} | {data.total_bytes:<15} | "
            f"{data.write_count:<15} | {data.micro_writes:<15}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))