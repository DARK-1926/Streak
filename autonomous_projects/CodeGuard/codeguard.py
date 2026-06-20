#!/usr/bin/env python3
"""
CodeGuard – Duplicate Test Case Detector

This module implements a lightweight, zero‑dependency command‑line tool that
detects duplicated or nearly‑duplicated test cases within a Python codebase.
It parses test files, normalizes test logic into a canonical representation,
computes SimHash fingerprints, and reports groups of tests with high
similarity.

Usage:
    python -m codeguard <path> [--json]

Author: OpenAI ChatGPT
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

try:
    from simhash import Simhash
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "The 'simhash' package is required. Install with: pip install simhash"
    ) from exc


@dataclass(frozen=True)
class TestInfo:
    """Represents a single test function extracted from a file."""

    file_path: Path
    function_name: str
    canonical: str
    simhash: Simhash


def find_test_files(root: Path) -> List[Path]:
    """
    Recursively find all *.py files under the given root that are either
    inside a directory named 'tests' or contain 'test_' in any part of the
    path.

    Args:
        root: Root directory to search.

    Returns:
        List of Path objects pointing to test files.
    """
    test_files: List[Path] = []
    for path in root.rglob("*.py"):
        parts = [p.lower() for p in path.parts]
        if "tests" in parts or any("test_" in p for p in parts):
            test_files.append(path.resolve())
    return test_files


class TestExtractor(ast.NodeVisitor):
    """
    AST visitor that extracts assertions, helper calls, and literals from a
    test function.
    """

    def __init__(self) -> None:
        self.assertions: Set[str] = set()
        self.helper_calls: Set[str] = set()
        self.literals: Set[str] = set()

    def visit_Assert(self, node: ast.Assert) -> None:  # noqa: N802
        expr = ast.unparse(node.test).strip()
        self.assertions.add(expr)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        # Detect calls to helper functions that start with 'test_'
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        if func_name and func_name.startswith("test_"):
            self.helper_calls.add(func_name)
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, (str, int, float, bool, type(None))):
            self.literals.add(repr(node.value))
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        # Replace variable names with placeholder during canonicalization
        self.generic_visit(node)


class PlaceholderTransformer(ast.NodeTransformer):
    """
    Replaces all variable names with a generic placeholder 'VAR'.
    """

    def visit_Name(self, node: ast.Name) -> ast.AST:
        return ast.copy_location(ast.Name(id="VAR", ctx=node.ctx), node)


def canonicalize(tree: ast.Module) -> str:
    """
    Generate a canonical string representation of a test function.

    The canonical string consists of sorted assertions, sorted literals,
    and sorted helper calls, all separated by newlines.

    Args:
        tree: AST of the test function body.

    Returns:
        Canonical string representation.
    """
    extractor = TestExtractor()
    extractor.visit(tree)

    sorted_asserts = sorted(extractor.assertions)
    sorted_literals = sorted(extractor.literals)
    sorted_helpers = sorted(extractor.helper_calls)

    parts: List[str] = []
    if sorted_asserts:
        parts.append("ASSERTS:" + ",".join(sorted_asserts))
    if sorted_literals:
        parts.append("LITERALS:" + ",".join(sorted_literals))
    if sorted_helpers:
        parts.append("HELPERS:" + ",".join(sorted_helpers))

    return "\n".join(parts)


def extract_tests_from_file(file_path: Path) -> List[TestInfo]:
    """
    Parse a Python file and extract all test functions.

    Args:
        file_path: Path to the Python file.

    Returns:
        List of TestInfo objects for each test function.
    """
    try:
        source = file_path.read_text(encoding="utf-8")
        module = ast.parse(source, filename=str(file_path))
    except Exception as exc:
        print(f"Error parsing {file_path}: {exc}", file=sys.stderr)
        return []

    tests: List[TestInfo] = []

    for node in ast.walk(module):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            # Replace variable names with placeholders
            body_copy = ast.Module(body=node.body, type_ignores=[])
            transformed = PlaceholderTransformer().visit(body_copy)
            ast.fix_missing_locations(transformed)

            canonical = canonicalize(transformed)
            simhash = Simhash(canonical)
            tests.append(
                TestInfo(
                    file_path=file_path,
                    function_name=node.name,
                    canonical=canonical,
                    simhash=simhash,
                )
            )
    return tests


def hamming_distance(a: int, b: int) -> int:
    """
    Compute Hamming distance between two integer hashes.

    Args:
        a: First hash.
        b: Second hash.

    Returns:
        Hamming distance.
    """
    return bin(a ^ b).count("1")


def group_similar_tests(tests: List[TestInfo], threshold: int = 3) -> List[Set[int]]:
    """
    Group tests that are similar based on SimHash Hamming distance.

    Args:
        tests: List of TestInfo objects.
        threshold: Maximum Hamming distance to consider tests similar.

    Returns:
        List of sets, each containing indices of similar tests.
    """
    n = len(tests)
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        fx, fy = find(x), find(y)
        if fx != fy:
            parent[fy] = fx

    for i in range(n):
        for j in range(i + 1, n):
            dist = hamming_distance(tests[i].simhash.value, tests[j].simhash.value)
            if dist < threshold:
                union(i, j)

    groups: Dict[int, Set[int]] = defaultdict(set)
    for idx in range(n):
        root = find(idx)
        groups[root].add(idx)

    return [group for group in groups.values() if len(group) > 1]


def build_report(tests: List[TestInfo], groups: List[Set[int]]) -> List[Dict]:
    """
    Construct a human‑readable report from grouped test indices.

    Args:
        tests: List of TestInfo objects.
        groups: List of sets of indices representing duplicate groups.

    Returns:
        List of dictionaries representing each duplicate group.
    """
    report: List[Dict] = []

    for group in groups:
        group_list = []
        for idx in group:
            t = tests[idx]
            group_list.append(
                {
                    "file": str(t.file_path),
                    "function": t.function_name,
                }
            )
        # Compute average similarity score (1 - distance/bit_length)
        scores = []
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a = tests[list(group)[i]].simhash.value
                b = tests[list(group)[j]].simhash.value
                dist = hamming_distance(a, b)
                scores.append(1 - dist / 64)  # Simhash default bits
        avg_score = sum(scores) / len(scores) if scores else 0.0
        report.append(
            {
                "group_size": len(group),
                "average_similarity": round(avg_score, 3),
                "tests": group_list,
            }
        )
    return report


def main() -> None:
    """
    Entry point for the command‑line interface.
    """
    parser = argparse.ArgumentParser(
        description="Detect duplicated or nearly‑duplicated test cases."
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Root directory containing tests.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output report in JSON format.",
    )
    args = parser.parse_args()

    root = args.path.resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory.", file=sys.stderr)
        sys.exit(1)

    test_files = find_test_files(root)
    all_tests: List[TestInfo] = []

    for file_path in test_files:
        all_tests.extend(extract_tests_from_file(file_path))

    if not all_tests:
        print("No test functions found.", file=sys.stderr)
        sys.exit(0)

    groups = group_similar_tests(all_tests)
    if not groups:
        print("No duplicate test groups detected.")
        sys.exit(0)

    report = build_report(all_tests, groups)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for idx, group in enumerate(report, 1):
            print(f"\nDuplicate Group {idx} (size: {group['group_size']}, "
                  f"avg similarity: {group['average_similarity']:.3f})")
            for test in group["tests"]:
                print(f"  - {test['file']}::{test['function']}")


if __name__ == "__main__":  # pragma: no cover
    main()