import sys
import argparse
import json
import dataclasses
from pathlib import Path
from typing import List

import contracts
import parser
import simulator


def _build_arg_parser() -> argparse.ArgumentParser:
    """Construct and return the CLI argument parser."""
    arg_parser = argparse.ArgumentParser(
        description="ToolchainContractAuditor: Deterministic pre-flight I/O contract validator."
    )
    arg_parser.add_argument(
        "--contracts",
        type=str,
        required=True,
        help="Path to the JSON/JSONL file containing tool contract definitions."
    )
    arg_parser.add_argument(
        "--chain",
        type=str,
        required=True,
        help="Path to the file containing chain link definitions."
    )
    return arg_parser


def _read_lines_safe(file_path: Path) -> List[str]:
    """
    Read a file line-by-line after validating existence and size.

    Guards against empty files using path.stat().st_size == 0 before reading
    to prevent win32 mmap/open crashes.

    Args:
        file_path: The pathlib.Path object pointing to the target file.

    Returns:
        A list of strings representing each line in the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is empty.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if file_path.stat().st_size == 0:
        raise ValueError(f"File is empty: {file_path}")
    with file_path.open("r", encoding="utf-8") as fh:
        return fh.readlines()


def main() -> int:
    """
    CLI entry point handling all side-effects and dependency injection wiring.

    Parses CLI arguments, reads input files, validates contracts and chains,
    runs the audit simulation, and outputs a structured JSON report to stdout.

    Returns:
        0 on success, 1 on failure.
    """
    try:
        arg_parser = _build_arg_parser()
        args = arg_parser.parse_args()

        contracts_path = Path(args.contracts)
        chain_path = Path(args.chain)

        contract_lines = _read_lines_safe(contracts_path)
        chain_lines = _read_lines_safe(chain_path)

        parsed_contracts = parser.parse_contracts(contract_lines)
        parsed_links = parser.parse_chain_links(chain_lines)

        registry = contracts.build_registry(parsed_contracts)
        report = simulator.audit_toolchain(registry, parsed_links)

        report_dict = dataclasses.asdict(report)
        print(json.dumps(report_dict, indent=2))
        return 0
    except Exception as exc:
        print(f"Audit failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())