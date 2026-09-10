import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

from .core import load_skill_from_source, compute_skill_hash, simulate_skill


def _read_source_file(file_path: Path) -> str:
    """Read and validate a source code file."""
    if not file_path.exists():
        print(f"Error: File '{file_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    if file_path.stat().st_size == 0:
        print(f"Error: File '{file_path}' is empty.", file=sys.stderr)
        sys.exit(1)
    
    try:
        return file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError as e:
        print(f"Error: Unable to read '{file_path}' as UTF-8 text: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: Failed to read file '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)


def _read_json_input(json_str: str) -> Dict[str, Any]:
    """Parse a JSON string into a dictionary."""
    try:
        data = json.loads(json_str)
        if not isinstance(data, dict):
            raise ValueError("Input must be a JSON object.")
        return data
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def add_command(args: argparse.Namespace) -> None:
    """Handle the 'add' subcommand."""
    source_code = _read_source_file(Path(args.file))
    try:
        skill_spec = load_skill_from_source(source_code)
        # Convert SkillSpec to dict for JSON serialization
        spec_dict = {
            "name": skill_spec.name,
            "inputs": skill_spec.inputs,
            "outputs": skill_spec.outputs,
            "source_code": skill_spec.source_code
        }
        print(json.dumps(spec_dict, indent=2))
    except ValueError as e:
        print(f"Error: Failed to parse skill from source: {e}", file=sys.stderr)
        sys.exit(1)


def verify_command(args: argparse.Namespace) -> None:
    """Handle the 'verify' subcommand."""
    source_code = _read_source_file(Path(args.file))
    try:
        skill_spec = load_skill_from_source(source_code)
        skill_hash = compute_skill_hash(skill_spec)
        print(skill_hash)
    except ValueError as e:
        print(f"Error: Failed to parse skill from source: {e}", file=sys.stderr)
        sys.exit(1)


def simulate_command(args: argparse.Namespace) -> None:
    """Handle the 'simulate' subcommand."""
    source_code = _read_source_file(Path(args.file))
    input_data = _read_json_input(args.input)
    
    try:
        skill_spec = load_skill_from_source(source_code)
        result = simulate_skill(skill_spec, input_data)
        print(json.dumps(result, indent=2))
    except ValueError as e:
        print(f"Error: Failed to parse skill from source: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: Simulation failed: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point for the SkillVault CLI."""
    parser = argparse.ArgumentParser(
        prog="vault",
        description="SkillVault: Manage, version, and validate reusable agent skills."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add subcommand
    add_parser = subparsers.add_parser("add", help="Parse a skill file and output its SkillSpec as JSON.")
    add_parser.add_argument("file", help="Path to the Python file containing a single annotated function.")

    # Verify subcommand
    verify_parser = subparsers.add_parser("verify", help="Compute and output the SHA-256 hash of a skill.")
    verify_parser.add_argument("file", help="Path to the Python file containing a single annotated function.")

    # Simulate subcommand
    simulate_parser = subparsers.add_parser("simulate", help="Execute a skill with provided inputs and output the result.")
    simulate_parser.add_argument("file", help="Path to the Python file containing a single annotated function.")
    simulate_parser.add_argument("input", help="JSON string representing the input arguments for the skill.")

    args = parser.parse_args()

    if args.command == "add":
        add_command(args)
    elif args.command == "verify":
        verify_command(args)
    elif args.command == "simulate":
        simulate_command(args)
    else:
        print(f"Error: Unknown command '{args.command}'.", file=sys.stderr)
        sys.exit(1)