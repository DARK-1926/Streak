import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Set

from .core import audit_tool_spec_for_pii


def load_tool_spec(filepath: str) -> Dict:
    """Load a tool specification from a JSON file.

    Args:
        filepath (str): Path to the JSON file containing the tool spec.

    Returns:
        Dict: The parsed tool specification dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is empty or contains invalid JSON.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Tool spec file not found: {filepath}")
    if path.stat().st_size == 0:
        raise ValueError(f"Tool spec file is empty: {filepath}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_pii_policy(filepath: str) -> Set[str]:
    """Load a PII policy from a JSON file containing a list of regex patterns.

    Args:
        filepath (str): Path to the JSON file containing a list of regex strings.

    Returns:
        Set[str]: A set of regex pattern strings.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is empty, invalid JSON, or not a list of strings.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"PII policy file not found: {filepath}")
    if path.stat().st_size == 0:
        raise ValueError(f"PII policy file is empty: {filepath}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("PII policy file must contain a JSON array")
    if not all(isinstance(item, str) for item in data):
        raise ValueError("All items in PII policy must be strings")
    return set(data)


def main() -> None:
    """Main entry point for the SpecPIIAuditor CLI.

    Parses command-line arguments, loads the tool spec and PII policy files,
    runs the PII audit, and outputs the report as JSON.
    """
    parser = argparse.ArgumentParser(
        description="Audit tool output schemas for potential PII leakage."
    )
    parser.add_argument(
        "--tool-spec",
        required=True,
        help="Path to the tool specification JSON file.",
    )
    parser.add_argument(
        "--pii-policy",
        required=True,
        help="Path to the PII policy JSON file (list of regex patterns).",
    )
    args = parser.parse_args()

    try:
        tool_spec = load_tool_spec(args.tool_spec)
        pii_policy = load_pii_policy(args.pii_policy)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"Error loading input files: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        report = audit_tool_spec_for_pii(tool_spec, pii_policy)
        print(json.dumps(report.__dict__))
    except Exception as e:
        print(f"Error during audit: {e}", file=sys.stderr)
        sys.exit(1)