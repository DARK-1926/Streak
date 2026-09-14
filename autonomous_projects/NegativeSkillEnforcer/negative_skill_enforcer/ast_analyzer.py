"""Module for analyzing Python AST to verify negative skill enforcement."""

import ast
from typing import Dict


def extract_function_nodes(source_code: str) -> Dict[str, ast.FunctionDef]:
    """Parse source code and extract all function definitions by name.

    Args:
        source_code: The Python source code as a string.

    Returns:
        A dictionary mapping function names to their corresponding ast.FunctionDef nodes.

    Raises:
        ValueError: If the source code contains a syntax error.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Syntax error in source code: {e}") from e

    function_nodes: Dict[str, ast.FunctionDef] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_nodes[node.name] = node
    return function_nodes


def _check_statement_for_raise(stmt, expected_exception: str) -> bool:
    """Recursively check a statement and its children for the expected raise."""
    if isinstance(stmt, ast.Raise):
        exc = stmt.exc
        if exc is None:
            return False

        # Case (a): `raise Exception()`
        if isinstance(exc, ast.Call):
            if (
                isinstance(exc.func, ast.Name)
                and exc.func.id == expected_exception
            ):
                return True

        # Case (b): `raise Exception`
        elif isinstance(exc, ast.Name) and exc.id == expected_exception:
            return True

    # Recursively check child statements for compound statements
    if isinstance(stmt, (ast.If, ast.For, ast.While, ast.With)):
        for child_stmt in stmt.body:
            if _check_statement_for_raise(child_stmt, expected_exception):
                return True
        for child_stmt in getattr(stmt, 'orelse', []):
            if _check_statement_for_raise(child_stmt, expected_exception):
                return True
    elif isinstance(stmt, ast.Try):
        # Check try body
        for child_stmt in stmt.body:
            if _check_statement_for_raise(child_stmt, expected_exception):
                return True
        # Check except handlers
        for handler in stmt.handlers:
            for child_stmt in handler.body:
                if _check_statement_for_raise(child_stmt, expected_exception):
                    return True
        # Check else and finally blocks
        for child_stmt in getattr(stmt, 'orelse', []):
            if _check_statement_for_raise(child_stmt, expected_exception):
                return True
        for child_stmt in getattr(stmt, 'finalbody', []):
            if _check_statement_for_raise(child_stmt, expected_exception):
                return True

    return False

def check_function_raises_exception(
    func_node: ast.FunctionDef, expected_exception: str
) -> bool:
    """Check if a function raises the expected exception type.

    The function is considered compliant if it contains a `raise` statement that
    either:
      (a) raises an exception instance created by calling the expected exception
          class (e.g., `raise PermissionError()`), or
      (b) raises the exception class directly (e.g., `raise PermissionError`).

    Attribute access (e.g., `module.Exception`) is not supported.

    Args:
        func_node: The AST node representing the function definition.
        expected_exception: The name of the expected exception class (e.g.,
            'PermissionError').

    Returns:
        True if the function raises the expected exception; False otherwise.
    """
    for stmt in func_node.body:
        if _check_statement_for_raise(stmt, expected_exception):
            return True
    return False