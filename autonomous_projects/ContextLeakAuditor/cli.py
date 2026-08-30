import argparse
import json
import mmap
import os
import sys
from typing import Any, Dict, List, Optional

from core import LeakReport, detect_leaks
from patterns import scan_redundancy
from simulator import run_budget_simulation
from parser import parse_log_stream


def _write_output(report: Dict[str, Any], output_path: Optional[str]) -> None:
    """Serialize the audit report to JSON and write to stdout or a file."""
    json_payload = json.dumps(report, indent=2)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as out_f:
            out_f.write(json_payload)
            out_f.write("\n")
    else:
        sys.stdout.write(json_payload)
        sys.stdout.write("\n")


def _build_empty_report() -> Dict[str, Any]:
    """Construct a standardized empty report structure."""
    return {
        "total_events": 0,
        "total_leaks": 0,
        "signatures": [],
        "redundancy_leaks": [],
        "simulation": {
            "steps": 0,
            "peak_tokens": 0,
            "projected_savings": 0,
            "would_overflow": False
        },
        "recommendation": "No events to analyze."
    }


def _execute_audit(input_path: str, budget: int, output_path: Optional[str]) -> None:
    """Run the single-pass audit pipeline on the specified JSONL log file."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if os.path.getsize(input_path) == 0:
        _write_output(_build_empty_report(), output_path)
        return

    with open(input_path, "rb") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            raw_text = mm.read().decode("utf-8")

    lines = raw_text.splitlines()
    parsed_events: List[Dict[str, Any]] = list(parse_log_stream(lines))

    leak_report: LeakReport = detect_leaks(parsed_events, budget)
    redundancy_sigs = scan_redundancy(parsed_events)
    sim_result = run_budget_simulation(parsed_events, budget)

    final_report: Dict[str, Any] = {
        "total_events": leak_report.total_events,
        "total_leaks": leak_report.total_leaks,
        "signatures": [
            {
                "type": sig.type,
                "step": sig.step,
                "severity": sig.severity,
                "tokens_wasted": sig.tokens_wasted
            }
            for sig in leak_report.signatures
        ],
        "redundancy_leaks": [
            {
                "type": sig.type,
                "step": sig.step,
                "severity": sig.severity,
                "tokens_wasted": sig.tokens_wasted
            }
            for sig in redundancy_sigs
        ],
        "simulation": {
            "steps": sim_result.steps,
            "peak_tokens": sim_result.peak_tokens,
            "projected_savings": sim_result.projected_savings,
            "would_overflow": sim_result.would_overflow
        },
        "recommendation": leak_report.recommendation
    }

    _write_output(final_report, output_path)


def main() -> None:
    """CLI entry point for ContextLeakAuditor."""
    parser = argparse.ArgumentParser(
        description="Deterministic single-pass auditor for agentic context leaks."
    )
    parser.add_argument(
        "--input", required=True, help="Path to the JSONL agent log file."
    )
    parser.add_argument(
        "--budget", type=int, required=True, help="Context window budget limit in tokens."
    )
    parser.add_argument(
        "--output", default=None, help="Optional file path to write the JSON report."
    )
    args = parser.parse_args()

    try:
        _execute_audit(args.input, args.budget, args.output)
        sys.exit(0)
    except FileNotFoundError as exc:
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(1)
    except PermissionError as exc:
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(1)
    except ValueError as exc:
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(1)
    except Exception as exc:
        sys.stderr.write(f"Error: Unexpected failure: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()