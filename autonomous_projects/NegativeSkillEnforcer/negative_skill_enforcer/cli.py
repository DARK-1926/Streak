"""Command-line interface for the NegativeSkillEnforcer tool."""

import argparse
import json
import sys
from pathlib import Path

from negative_skill_enforcer.enforcer import enforce_negative_skills
from negative_skill_enforcer.spec import load_spec_from_dict


def main() -> None:
    """Run the NegativeSkillEnforcer CLI.

    Parses command-line arguments, validates input files, loads the negative
    skill specification, reads the agent skill source code, enforces the
    specification, and outputs a JSON report. Exits with code 0 if no violations
    are found, 1 if input files are invalid, or 2 if violations are detected.
    """
    parser = argparse.ArgumentParser(
        description="Statically verify that agent skill modules enforce declared negative capabilities."
    )
    parser.add_argument(
        "--skill-file",
        required=True,
        type=Path,
        help="Path to the agent skill module source file.",
    )
    parser.add_argument(
        "--spec-file",
        required=True,
        type=Path,
        help="Path to the negative skill specification JSON file.",
    )
    args = parser.parse_args()

    skill_file: Path = args.skill_file
    spec_file: Path = args.spec_file

    # Validate that both files exist and are non-empty
    for file_path in (skill_file, spec_file):
        if not file_path.exists():
            print(f"Error: File does not exist: {file_path}", file=sys.stderr)
            sys.exit(1)
        try:
            if file_path.stat().st_size == 0:
                print(f"Error: File is empty: {file_path}", file=sys.stderr)
                sys.exit(1)
        except OSError as e:
            print(f"Error accessing file {file_path}: {e}", file=sys.stderr)
            sys.exit(1)

    # Load and parse the spec file
    try:
        with open(spec_file, "r", encoding="utf-8") as f:
            spec_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading or parsing spec file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        spec = load_spec_from_dict(spec_data)
    except ValueError as e:
        print(f"Invalid spec format: {e}", file=sys.stderr)
        sys.exit(1)

    # Read the skill source code
    try:
        with open(skill_file, "r", encoding="utf-8") as f:
            skill_source = f.read()
    except OSError as e:
        print(f"Error reading skill file: {e}", file=sys.stderr)
        sys.exit(1)

    # Enforce the negative skills
    try:
        report = enforce_negative_skills(skill_source, spec)
    except ValueError as e:
        print(f"Error analyzing skill source: {e}", file=sys.stderr)
        sys.exit(1)

    # Output the report as JSON
    report_dict = {
        "missing_functions": report.missing_functions,
        "incorrect_exceptions": report.incorrect_exceptions,
    }
    print(json.dumps(report_dict, indent=2))

    # Exit based on whether violations were found
    if not report.missing_functions and not report.incorrect_exceptions:
        sys.exit(0)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()