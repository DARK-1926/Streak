import sys
import argparse
import json
from typing import Optional, List

import core
import io_handler


def main(argv: Optional[List[str]] = None) -> int:
    """
    CLI entry point for the LicenseInfectionAuditor.

    Parses command-line arguments, orchestrates the file I/O and
    scanning engine, and outputs the results as formatted JSON.

    Args:
        argv: Optional list of command-line arguments. Defaults to sys.argv[1:].

    Returns:
        int: Exit code (0 for success, 1 for file/permission errors).
    """
    parser = argparse.ArgumentParser(
        description="Scan JSONL logs for GPL license signatures."
    )
    parser.add_argument(
        "logfile",
        help="Path to the JSONL log file to scan."
    )

    args = parser.parse_args(argv)

    try:
        lines_generator = io_handler.yield_log_lines(args.logfile)
        scan_results = core.scan_stream(lines_generator)
        
        print(json.dumps(scan_results, indent=4))
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 1
    except PermissionError as e:
        print(f"Error: Permission denied - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: An unexpected error occurred - {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())