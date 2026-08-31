import argparse
import sys
import os
import mmap
import pathlib
import json
from typing import Iterable

import core
import models


def stream_jsonl_file(filepath: str) -> Iterable[dict]:
    """Stream and parse a JSONL file using memory-mapped I/O for efficiency."""
    p = pathlib.Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"Log file not found: {filepath}")
    if os.path.getsize(filepath) == 0:
        return
    with open(filepath, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for line in mm:
                parsed = core.parse_log_line(line.decode('utf-8'))
                if parsed is not None:
                    yield parsed


def main() -> None:
    """CLI entrypoint for TokenDriftAuditor."""
    parser = argparse.ArgumentParser(description="Audit LLM token drift and inefficiencies.")
    parser.add_argument("--input", required=True, help="Path to the JSONL log file.")
    parser.add_argument("--cost-rate", type=float, default=0.005, help="Cost per 1k tokens.")
    parser.add_argument("--output", help="Path to write the JSON audit report. Defaults to stdout.")
    args = parser.parse_args()

    try:
        events = stream_jsonl_file(args.input)
        report = core.run_audit_stream(events, cost_per_1k=args.cost_rate)
        report_json = json.dumps(report.to_dict(), indent=2)

        if args.output:
            pathlib.Path(args.output).write_text(report_json, encoding="utf-8")
        else:
            sys.stdout.write(report_json + "\n")
        sys.exit(0)
    except Exception as exc:
        print(f"Audit failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()