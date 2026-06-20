#!/usr/bin/env python3
"""
Local Duplicate Code Detector & Refactor Assistant (LDCDRA)
Detects duplicate code blocks across a project and suggests refactorings.
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any

# Import configuration
import config


def setup_logging(level: str = config.LOG_LEVEL) -> None:
    """Configure logging based on the provided level."""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_project_root(start_path: Path = Path.cwd()) -> Path:
    """Determine the project root by looking for common markers."""
    markers = {".git", "pyproject.toml", "setup.py", "setup.cfg", "tox.ini"}
    current = start_path.resolve()
    while current != current.parent:
        if any((current / marker).exists() for marker in markers):
            return current
        current = current.parent
    return start_path


def collect_files(
    root: Path,
    exclude_dirs: Set[str] = config.EXCLUDE_DIRS,
    extensions: Set[str] = config.EXTENSIONS,
) -> List[Path]:
    """Collect all source files under the given root, respecting exclusions."""
    file_list: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        # Modify dirnames in-place to skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for fname in filenames:
            if Path(fname).suffix.lower() in extensions:
                file_list.append(Path(dirpath) / fname)
    return file_list


def read_file(path: Path, max_size: int = config.MAX_FILE_SIZE) -> str:
    """Read the content of a file, ensuring it does not exceed max_size."""
    try:
        if path.stat().st_size > max_size:
            logging.warning(f"File {path} exceeds max size ({max_size} bytes). Skipping.")
            return ""
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError as e:
        logging.error(f"Failed to read {path}: {e}")
        return ""


def compute_content_hash(content: str) -> str:
    """Compute a SHA-256 hash of the given content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def detect_duplicate_groups(files: List[Path]) -> Dict[str, List[Path]]:
    """Detect duplicate files based on content hash."""
    hash_map: Dict[str, List[Path]] = {}
    for file_path in files:
        content = read_file(file_path)
        if not content:
            continue
        file_hash = compute_content_hash(content)
        hash_map.setdefault(file_hash, []).append(file_path)
    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}


def find_common_subsequence(strings: List[str]) -> List[str]:
    """
    Find the longest common subsequence among a list of strings using difflib.
    Returns a list of lines that appear in all strings.
    """
    import difflib

    if not strings:
        return []
    # Start with the first string as reference
    reference = strings[0].splitlines()
    common = reference[:]
    for s in strings[1:]:
        current = s.splitlines()
        # Use SequenceMatcher to get common blocks
        matcher = difflib.SequenceMatcher(None, common, current)
        common = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                common.extend(current[j1:j2])
    return common


def suggest_refactor(duplicate_groups: Dict[str, List[Path]]) -> List[Dict[str, Any]]:
    """
    Generate refactor suggestions for each duplicate group.
    Returns a list of suggestion dictionaries.
    """
    suggestions: List[Dict[str, Any]] = []
    for file_hash, file_list in duplicate_groups.items():
        # Read the content of the first file to extract duplicate lines
        sample_content = read_file(file_list[0])
        if not sample_content:
            continue
        lines = sample_content.splitlines()
        # Use a simple heuristic: duplicate entire file content
        # In a real implementation, we would perform more sophisticated analysis
        suggestion = {
            "duplicate_hash": file_hash,
            "affected_files": [str(p) for p in file_list],
            "common_lines": find_common_subsequence(
                [read_file(p) for p in file_list if read_file(p)]
            ),
            "refactor_type": "extract_common_function",
        }
        suggestions.append(suggestion)
        logging.info(f"Suggested refactor for {len(file_list)} duplicate files.")
    return suggestions


def apply_refactor(suggestion: Dict[str, Any], output_dir: Path = Path("refactored")) -> None:
    """
    Apply a refactor suggestion by extracting common lines into a new utility file.
    The new file is placed under output_dir.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    common_lines = suggestion.get("common_lines", [])
    if not common_lines:
        logging.warning("No common lines to extract.")
        return

    # Create a unique filename based on hash
    file_hash = suggestion.get("duplicate_hash", "unknown")
    new_file = output_dir / f"extracted_{file_hash[:8]}.py"
    # Generate a function name
    func_name = f"extracted_{hash(tuple(common_lines)) & 0xFFFFFFFF:x}"
    # Build the extracted code
    extracted_code = f'"""\nExtracted common code block.\n"""\n'
    extracted_code += f"def {func_name}() -> str:\n"
    for line in common_lines:
        extracted_code += f"    {line}\n"
    extracted_code += "    return \"\"\n"

    try:
        with open(new_file, "w", encoding="utf-8") as f:
            f.write(extracted_code)
        logging.info(f"Created extracted code file: {new_file}")
    except OSError as e:
        logging.error(f"Failed to write extracted code to {new_file}: {e}")


def cli_detect(args: argparse.Namespace) -> None:
    """Command-line handler for duplicate detection."""
    setup_logging()
    root = Path(args.path).resolve() if args.path else get_project_root()
    logging.info(f"Scanning project root: {root}")

    files = collect_files(root)
    logging.info(f"Collected {len(files)} source files.")

    duplicates = detect_duplicate_groups(files)
    if not duplicates:
        logging.info("No duplicate files found.")
        return

    logging.info(f"Found {len(duplicates)} duplicate groups.")
    for file_hash, file_list in duplicates.items():
        logging.info(f"Duplicate group (hash {file_hash[:8]}):")
        for p in file_list:
            logging.info(f"  - {p}")


def cli_refactor(args: argparse.Namespace) -> None:
    """Command-line handler for refactor suggestion and application."""
    setup_logging()
    root = Path(args.path).resolve() if args.path else get_project_root()
    logging.info(f"Scanning project root for refactor analysis: {root}")

    files = collect_files(root)
    logging.info(f"Collected {len(files)} source files.")

    duplicates = detect_duplicate_groups(files)
    if not duplicates:
        logging.info("No duplicate files to refactor.")
        return

    suggestions = suggest_refactor(duplicates)
    if args.suggest_only:
        logging.info("Refactor suggestions (not applied):")
        for idx, sug in enumerate(suggestions, start=1):
            logging.info(f"Suggestion {idx}:")
            logging.info(f"  Type: {sug['refactor_type']}")
            logging.info(f"  Affected files: {len(sug['affected_files'])}")
            logging.info(f"  Common lines count: {len(sug['common_lines'])}")
        return

    # Apply each suggestion
    for sug in suggestions:
        apply_refactor(sug)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local Duplicate Code Detector & Refactor Assistant (LDCDRA)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    detect_parser = subparsers.add_parser("detect", help="Detect duplicate code files")
    detect_parser.add_argument(
        "path", nargs="?", help="Root directory to scan (default: current project root)"
    )

    refactor_parser = subparsers.add_parser(
        "refactor", help="Suggest and optionally apply refactorings for duplicates"
    )
    refactor_parser.add_argument(
        "path", nargs="?", help="Root directory to scan (default: current project root)"
    )
    refactor_parser.add_argument(
        "--suggest-only", action="store_true", help="Only output suggestions without applying"
    )

    args = parser.parse_args()

    if args.command == "detect":
        cli_detect(args)
    elif args.command == "refactor":
        cli_refactor(args)


if __name__ == "__main__":
    main()