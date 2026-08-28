"""
Command-line interface for AgentSwarmLoopAuditor.

Provides a CLI to analyze JSONL agent logs for degenerate behavioral loops
and output the results in either plain text or JSON format.
"""

import argparse
import json
import sys
from dataclasses import asdict
from typing import Dict, List

from core import audit_sessions, parse_action
from io import stream_jsonl
from models import LoopReport


def build_parser() -> argparse.ArgumentParser:
    """
    Builds and returns the argument parser for the CLI.
    
    Returns:
        An argparse.ArgumentParser configured with the necessary arguments.
    """
    parser = argparse.ArgumentParser(
        description="Audit autonomous agent logs for infinite loops and thrashing."
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the JSONL log file to analyze."
    )
    parser.add_argument(
        "-f", "--format",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format for the audit report (default: text)."
    )
    return parser


def format_text(reports: Dict[str, List[LoopReport]]) -> str:
    """
    Formats the audit reports as a human-readable plain text string.
    
    Args:
        reports: A dictionary mapping session IDs to lists of LoopReports.
        
    Returns:
        A formatted multi-line string representing the reports.
    """
    lines = []
    has_loops = False
    
    for session_id, session_reports in reports.items():
        if not session_reports:
            continue
            
        has_loops = True
        lines.append(f"Session: {session_id}")
        
        for report in session_reports:
            lines.append(
                f"  - Type: {report.loop_type} | "
                f"Count: {report.count} | "
                f"Wasted Tokens: {report.wasted_tokens}"
            )
            
    return "\n".join(lines) if has_loops else "No loops detected."


def format_json(reports: Dict[str, List[LoopReport]]) -> str:
    """
    Formats the audit reports as a JSON string.
    
    Args:
        reports: A dictionary mapping session IDs to lists of LoopReports.
        
    Returns:
        A JSON-formatted string representing the reports.
    """
    serializable = {
        sid: [asdict(r) for r in reps]
        for sid, reps in reports.items()
    }
    return json.dumps(serializable, indent=2)


def main() -> None:
    """
    Main entry point for the AgentSwarmLoopAuditor CLI.
    
    Parses arguments, streams the input file, audits the sessions,
    and prints the formatted results. Handles common I/O and user
    interruption exceptions gracefully.
    """
    parser = build_parser()
    args = parser.parse_args()
    
    try:
        # Validate file accessibility to trigger standard I/O exceptions
        with open(args.input_file, 'rb') as f:
            pass
            
        # Stream lines, parse actions, and filter out invalid entries
        raw_lines = stream_jsonl(args.input_file)
        parsed_actions = (parse_action(line) for line in raw_lines)
        actions = (action for action in parsed_actions if action is not None)
        
        # Run the core audit logic
        reports = audit_sessions(actions)
        
        # Output the results
        if args.format == "json":
            print(format_json(reports))
        else:
            print(format_text(reports))
            
    except FileNotFoundError:
        print(f"Error: File not found - {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied - {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAudit interrupted by user.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()