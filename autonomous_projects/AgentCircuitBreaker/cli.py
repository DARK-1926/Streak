import argparse
import json
import os
import sys
from typing import Dict, List

from models import AuditReport
from parser import parse_log_stream
from breaker import evaluate_circuit_states
from router import simulate_fallback_routing


def run_audit(file_path: str, policy_json_str: str) -> AuditReport:
    """Execute the resilience audit pipeline on a log file and routing policy.

    Args:
        file_path: Path to the log file containing JSON lines.
        policy_json_str: JSON string defining the fallback routing policy.

    Returns:
        An AuditReport containing circuit states and routing decisions.

    Raises:
        FileNotFoundError: If the log file does not exist.
        ValueError: If the log file is empty.
        json.JSONDecodeError: If the policy JSON is malformed.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Log file not found: {file_path}")

    if not os.path.getsize(file_path) > 0:
        raise ValueError(f"Log file is empty: {file_path}")

    try:
        policy: Dict[str, List[str]] = json.loads(policy_json_str)
    except json.JSONDecodeError as exc:
        raise json.JSONDecodeError(
            msg=f"Invalid policy JSON: {exc.msg}",
            doc=exc.doc,
            pos=exc.pos
        ) from exc

    with open(file_path, "r", encoding="utf-8") as f:
        entries = parse_log_stream(f)
        states = evaluate_circuit_states(entries)
        decisions = simulate_fallback_routing(states, policy)

    return AuditReport(
        circuit_states=states,
        routing_decision=decisions,
    )


def main() -> None:
    """CLI entry point for the AgentCircuitBreaker audit tool."""
    arg_parser = argparse.ArgumentParser(
        description="Audit agentic workflow resilience via circuit breaker analysis."
    )
    arg_parser.add_argument(
        "--log",
        required=True,
        help="Path to the JSON-lines log file."
    )
    arg_parser.add_argument(
        "--policy",
        required=True,
        help="Path to the JSON policy file."
    )

    args = arg_parser.parse_args()

    try:
        with open(args.policy, "r", encoding="utf-8") as f:
            policy_content = f.read()
        report = run_audit(args.log, policy_content)
        print(json.dumps(report.to_dict(), indent=2))
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()