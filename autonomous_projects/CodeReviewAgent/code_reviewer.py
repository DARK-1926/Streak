import ast
import os
import tempfile
from typing import Dict, List

def analyze_code(code: str) -> Dict[str, List[str]]:
    """
    Analyzes the given Python code and returns a dictionary of feedback and suggestions.
    
    The function checks for common issues such as unused imports, variable naming conventions,
    and potential bugs. It uses the abstract syntax tree (AST) to parse the code and perform
    static analysis.

    :param code: A string containing the Python code to be analyzed.
    :return: A dictionary where keys are categories of feedback (e.g., 'unused_imports',
             'naming_conventions', 'potential_bugs') and values are lists of specific feedback
             messages.
    """
    feedback = {
        'unused_imports': [],
        'naming_conventions': [],
        'potential_bugs': []
    }

    # Write the code to a temporary file
    fd, path = tempfile.mkstemp(suffix='.py')
    try:
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(code)
        
        # Parse the code into an AST
        with open(path, 'r') as file:
            tree = ast.parse(file.read(), filename=path)

        # Check for unused imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if not is_used(alias.name, tree):
                        feedback['unused_imports'].append(f"Unused import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if not is_used(alias.name, tree):
                        feedback['unused_imports'].append(f"Unused import: {node.module}.{alias.name}")

        # Check for naming conventions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not is_valid_name(node.name):
                    feedback['naming_conventions'].append(f"Invalid name for {type(node).__name__}: {node.name}")
            elif isinstance(node, ast.Name):
                if not is_valid_name(node.id):
                    feedback['naming_conventions'].append(f"Invalid variable name: {node.id}")

        # Check for potential bugs (e.g., using == to compare with None)
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                if isinstance(node.ops[0], ast.Eq) and (is_none_constant(node.left) or is_none_constant(node.comparators[0])):
                    feedback['potential_bugs'].append("Use 'is' to compare with None, not '=='")

    finally:
        os.remove(path)

    return feedback

def is_used(name: str, tree: ast.AST) -> bool:
    """Check if the given name is used in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == name:
            return True
    return False

import keyword
def is_valid_name(name: str) -> bool:
    """Check if the given name follows PEP 8 naming conventions."""
    return name.isidentifier() and not keyword.iskeyword(name) and name.lower() == name
    return name.isidentifier() and not keyword.iskeyword(name) and name.lower() == name

def is_none_constant(node: ast.AST) -> bool:
    """Check if the given AST node is a None constant."""
    return isinstance(node, ast.Constant) and node.value is None
