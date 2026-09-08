import argparse
import sys
import os
import json
from pathlib import Path
from typing import Dict, Any

from core.models import FailoverPolicy
from adapters.executor import execute_with_failover


def main(args: list[str] | None = None) -> None:
    """
    CLI entry point for AgentFailoverRouter.

    Parses command-line arguments, loads configuration and context from JSON files,
    executes the failover-aware routing logic, and outputs the result as JSON.

    Args:
        args: Optional list of command-line arguments (for testing). If None, uses sys.argv[1:].
    """
    parser = argparse.ArgumentParser(
        description="AgentFailoverRouter: Deterministic failover routing for agentic toolchains."
    )
    parser.add_argument(
        "--config",
        required=True,
        type=str,
        help="Path to JSON file containing FailoverPolicy configuration."
    )
    parser.add_argument(
        "--input",
        required=True,
        type=str,
        help="Path to JSON file containing initial context dictionary."
    )
    parser.add_argument(
        "--simulate-failure",
        action="store_true",
        help="If set, primary runner will simulate a failure for deterministic demo."
    )

    parsed_args = parser.parse_args(args)

    # Load policy config with size guard
    config_path = Path(parsed_args.config)
    try:
        config_stat = config_path.stat()
        if config_stat.st_size == 0:
            print(f"Error: Config file '{config_path}' is empty.", file=sys.stderr)
            sys.exit(1)
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file '{config_path}': {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error reading config file '{config_path}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        policy = FailoverPolicy(**config_data)
    except (TypeError, ValueError) as e:
        print(f"Error: Invalid policy configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # Load input context with size guard
    input_path = Path(parsed_args.input)
    try:
        input_stat = input_path.stat()
        if input_stat.st_size == 0:
            print(f"Error: Input context file '{input_path}' is empty.", file=sys.stderr)
            sys.exit(1)
        with open(input_path, 'r', encoding='utf-8') as f:
            context = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input context file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input context file '{input_path}': {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error reading input context file '{input_path}': {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(context, dict):
        print(f"Error: Input context must be a JSON object, got {type(context).__name__}.", file=sys.stderr)
        sys.exit(1)

    # Define runners
    def target_runner(ctx: Dict[str, Any]) -> Dict[str, Any]:
        if parsed_args.simulate_failure:
            raise RuntimeError("Simulated failure")
        return {"status": "ok"}

    def fallback_runner(ctx: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "recovered"}

    # Execute with failover
    try:
        result, call_record = execute_with_failover(
            target_runner=target_runner,
            fallback_runner=fallback_runner,
            context=context,
            policy=policy
        )
    except KeyboardInterrupt:
        sys.exit(130)
    except SystemExit:
        raise
    except Exception as e:
        print(f"Unexpected error during execution: {e}", file=sys.stderr)
        sys.exit(2)

    # Output structured result
    output = {
        "result": result,
        "call_record": {
            "target": call_record.target,
            "success": call_record.success,
            "latency_ms": call_record.latency_ms,
            "error_code": call_record.error_code,
            "timestamp": call_record.timestamp
        }
    }

    try:
        sys.stdout.write(json.dumps(output, separators=(',', ':')) + "\n")
        sys.stdout.flush()
    except BrokenPipeError:
        # Handle broken pipe gracefully (e.g., when piped to `head`)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)


if __name__ == "__main__":
    main()