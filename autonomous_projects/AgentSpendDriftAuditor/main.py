import argparse
import sys

from core import run_audit


def main() -> int:
    """
    CLI entry point for the AgentSpendDriftAuditor.
    
    Parses command-line arguments, executes the audit via run_audit,
    and prints the results in a clean, cross-platform text format.
    
    Returns:
        int: Exit status code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description="Audit agent JSONL logs for AWS-style billing spikes and floating-point drift."
    )
    parser.add_argument(
        "file_path",
        type=str,
        help="Path to the JSONL log file to be audited."
    )
    parser.add_argument(
        "--window",
        type=int,
        default=60,
        help="Time window in seconds for spike detection (default: 60)."
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=100,
        help="Number of events required to trigger a spike (default: 100)."
    )
    
    args = parser.parse_args()
    
    try:
        total_cost, spikes = run_audit(args.file_path, args.window, args.threshold)
    except FileNotFoundError:
        print(f"Error: The file '{args.file_path}' was not found.", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: An unexpected error occurred during the audit: {exc}", file=sys.stderr)
        return 1
        
    print(f"Exact Total Cost: {total_cost}")
    
    if not spikes:
        print("Spikes Detected: None")
    else:
        print(f"Spikes Detected: {len(spikes)}")
        for idx, spike in enumerate(spikes, start=1):
            agent_id = spike.get("agent_id", "unknown")
            count = spike.get("count", 0)
            start = spike.get("start_time", "N/A")
            end = spike.get("end_time", "N/A")
            print(f"  [{idx}] Agent: {agent_id} | Events: {count} | Window: {start} - {end}")
            
    return 0


if __name__ == "__main__":
    sys.exit(main())