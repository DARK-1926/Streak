#!/usr/bin/env python3
"""
Local Duplicate Code Detector & Refactor Assistant (LDCDRA) - AI Review Module

This module provides functionality to scan a Python codebase for duplicate code,
analyze the duplicates, and generate refactoring suggestions. It avoids using
external commands (e.g., 'refactor' or 'timeout') and relies solely on Python
standard library utilities for robustness and portability.
"""

import argparse
import ast
import difflib
import hashlib
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union


class CodeSnippet:
    """Represents a piece of code (function, class, method) extracted from a file."""

    def __init__(self, path: Path, name: str, node: ast.AST, source: str):
        self.path = path
        self.name = name
        self.node = node
        self.source = source
        self.hash = self._compute_hash()
        self.normalized_source = self._normalize_source(source)

    def _compute_hash(self) -> str:
        """Compute a SHA‑256 hash of the raw source code for exact duplicate detection."""
        return hashlib.sha256(self.source.encode('utf-8')).hexdigest()

    def _normalize_source(self, source: str) -> str:
        """
        Return a canonical representation of the source code.
        Uses AST unparse when available to normalize formatting; otherwise falls back
        to stripped source.
        """
        try:
            tree = ast.parse(source)
            if hasattr(ast, 'unparse'):
                return ast.unparse(tree)
            return source.strip()
        except SyntaxError:
            return source.strip()


class DuplicateDetector:
    """Detects duplicate code snippets within a codebase based on hash and similarity."""

    def __init__(self, min_similarity: float = 0.8):
        self.min_similarity = min_similarity
        self.snippets: List[CodeSnippet] = []

    def add_snippet(self, snippet: CodeSnippet):
        """Register a code snippet for duplicate detection."""
        self.snippets.append(snippet)

    def detect_duplicates(self) -> List[List[CodeSnippet]]:
        """
        Group snippets that are considered duplicates.

        First groups exact duplicates by hash, then performs similarity analysis
        for remaining snippets.
        """
        # Exact duplicate groups
        hash_groups: Dict[str, List[CodeSnippet]] = {}
        for snippet in self.snippets:
            hash_groups.setdefault(snippet.hash, []).append(snippet)

        duplicate_groups = [group for group in hash_groups.values() if len(group) > 1]

        # Similarity‑based detection for singletons
        for snippet in self.snippets:
            if any(snippet in group for group in duplicate_groups):
                continue
            similar = self._find_similar(snippet)
            if similar:
                duplicate_groups.append([snippet] + similar)

        return duplicate_groups

    def _find_similar(self, snippet: CodeSnippet) -> List[CodeSnippet]:
        """Return a list of snippets that are similar to the given snippet."""
        similar: List[CodeSnippet] = []
        for other in self.snippets:
            if other is snippet or any(other in group for group in self.detect_duplicates()):
                continue
            similarity = self._compute_similarity(snippet.normalized_source, other.normalized_source)
            if similarity >= self.min_similarity:
                similar.append(other)
        return similar

    def _compute_similarity(self, a: str, b: str) -> float:
        """Compute a similarity ratio between two source strings using difflib."""
        return difflib.SequenceMatcher(None, a, b).ratio()


class RefactorAssistant:
    """Generates refactoring suggestions for duplicate code groups."""

    @staticmethod
    def suggest_extraction(group: List[CodeSnippet]) -> Optional[str]:
        """
        Suggest extracting common code into a new helper function.

        Returns a human‑readable suggestion or None if extraction is not feasible.
        """
        if len(group) < 2:
            return None

        first_source = group[0].source
        try:
            first_tree = ast.parse(first_source)
            func_def = first_tree.body[0]
            if not isinstance(func_def, ast.FunctionDef):
                return None

            # Placeholder logic: indicate that a helper could be extracted.
            return (
                f"# Suggested extraction: create a helper function to avoid duplication "
                f"among {len(group)} occurrences."
            )
        except (SyntaxError, IndexError):
            return None

    @staticmethod
    def suggest_rename(group: List[CodeSnippet]) -> Optional[str]:
        """Suggest renaming duplicate identifiers to improve clarity."""
        return (
            f"# Suggested rename: consider using more descriptive names "
            f"for the duplicated entities."
        )


def scan_directory(root: Path) -> List[Path]:
    """Recursively find all Python files under the given directory."""
    python_files: List[Path] = []
    for path in root.rglob('*.py'):
        if path.is_file():
            python_files.append(path)
    return python_files


def extract_functions_from_file(file_path: Path) -> List[CodeSnippet]:
    """
    Extract function definitions from a Python file and return them as CodeSnippet objects.
    """
    snippets: List[CodeSnippet] = []
    try:
        source = file_path.read_text(encoding='utf-8')
        tree = ast.parse(source, filename=str(file_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Attempt to retrieve the exact source segment for the function.
                if hasattr(ast, 'get_source_segment'):
                    func_source = ast.get_source_segment(source, node)
                else:
                    # Fallback for older Python versions.
                    func_source = (
                        source[node.col_offset:node.col_offset + node.end_col_offset]
                        if hasattr(node, 'col_offset') and hasattr(node, 'end_col_offset')
                        else source
                    )
                snippets.append(CodeSnippet(file_path, node.name, node, func_source))
    except (SyntaxError, OSError) as e:
        logging.warning(f"Failed to parse {file_path}: {e}")
    return snippets


def analyze_codebase(directory: Path) -> Tuple[DuplicateDetector, List[List[CodeSnippet]]]:
    """Scan a directory, extract code snippets, and detect duplicates."""
    detector = DuplicateDetector()
    for file_path in scan_directory(directory):
        for snippet in extract_functions_from_file(file_path):
            detector.add_snippet(snippet)
    duplicate_groups = detector.detect_duplicates()
    return detector, duplicate_groups


def generate_suggestions(duplicate_groups: List[List[CodeSnippet]]) -> List[str]:
    """Generate refactoring suggestions for each duplicate group."""
    suggestions: List[str] = []
    assistant = RefactorAssistant()
    for group in duplicate_groups:
        extraction = assistant.suggest_extraction(group)
        rename = assistant.suggest_rename(group)
        if extraction:
            suggestions.append(extraction)
        if rename:
            suggestions.append(rename)
    return suggestions


def main():
    parser = argparse.ArgumentParser(
        description='Local Duplicate Code Detector & Refactor Assistant'
    )
    parser.add_argument('directory', type=Path, help='Root directory of the Python codebase')
    parser.add_argument(
        '--min-similarity',
        type=float,
        default=0.8,
        help='Minimum similarity threshold for detecting near‑duplicates',
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging verbosity',
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

    if not args.directory.exists() or not args.directory.is_dir():
        logging.error(f"Directory not found: {args.directory}")
        sys.exit(1)

    # Re‑initialise detector with the user‑specified similarity threshold.
    detector = DuplicateDetector(min_similarity=args.min_similarity)
    for file_path in scan_directory(args.directory):
        for snippet in extract_functions_from_file(file_path):
            detector.add_snippet(snippet)
    duplicate_groups = detector.detect_duplicates()

    suggestions = generate_suggestions(duplicate_groups)

    if suggestions:
        print("Duplicate code detected. Suggested refactoring actions:")
        for idx, suggestion in enumerate(suggestions, start=1):
            print(f"{idx}. {suggestion}")
    else:
        print("No duplicate code detected.")


if __name__ == '__main__':
    main()