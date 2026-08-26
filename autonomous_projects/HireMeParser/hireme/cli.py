"""Command-line interface for HireMeParser."""

import argparse
import json
import sys
from pathlib import Path

from hireme.parser import parse_hn_hireme_post, ValidationError


def main() -> None:
    """Parse 'Who wants to be hired?' HN posts from stdin or a file and output JSON.

    This function sets up argument parsing, reads input content, processes it using
    the parser, and outputs the result as JSON. Errors are handled gracefully with
    appropriate exit codes.
    """
    parser = argparse.ArgumentParser(
        description="Parse 'Who wants to be hired?' Hacker News posts into structured JSON."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Input file path. If not provided, reads from stdin.",
    )
    args = parser.parse_args()

    try:
        if args.input is None:
            content = sys.stdin.read()
        else:
            content = args.input.read_text(encoding="utf-8")
    except OSError as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = parse_hn_hireme_post(content)
        print(json.dumps(result, indent=2))
    except ValidationError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()