import ast
import hashlib
import json
import tempfile
import os
from typing import Dict, Tuple, Any
from .models import SkillSpec


def parse_function_signature(source_code: str) -> Tuple[str, Dict[str, str], Dict[str, str]]:
    """
    Parse a Python function's source code to extract its name, input parameters with type annotations,
    and return type annotation.

    Args:
        source_code (str): The source code string of a single Python function.

    Returns:
        Tuple[str, Dict[str, str], Dict[str, str]]: A tuple containing:
            - function name (str)
            - inputs: mapping from parameter names to their type annotation strings
            - outputs: mapping with a single key 'return' to its type annotation string

    Raises:
        ValueError: If the source contains no function, multiple functions, or invalid syntax.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}")

    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    if len(functions) == 0:
        raise ValueError("Source code must contain exactly one function.")
    if len(functions) > 1:
        raise ValueError("Source code must contain exactly one function.")

    func_node = functions[0]
    func_name = func_node.name

    inputs = {}
    for arg in func_node.args.args:
        if arg.annotation is None:
            raise ValueError(f"Parameter '{arg.arg}' missing type annotation.")
        annotation_str = _annotation_to_string(arg.annotation)
        inputs[arg.arg] = annotation_str

    # Handle return annotation
    if func_node.returns is None:
        raise ValueError("Function must have a return type annotation.")
    return_annotation_str = _annotation_to_string(func_node.returns)
    outputs = return_annotation_str

    return func_name, inputs, outputs


def _annotation_to_string(annotation: ast.AST) -> str:
    """Convert an AST annotation node to a canonical string representation."""
    if isinstance(annotation, ast.Name):
        return annotation.id
    elif isinstance(annotation, ast.Constant):
        # For Python 3.8+, handles cases like 'int' as string literal in annotation
        return str(annotation.value)
    elif isinstance(annotation, ast.Subscript):
        # e.g., List[int], Dict[str, int]
        value = _annotation_to_string(annotation.value)
        slice_node = annotation.slice
        if isinstance(slice_node, ast.Tuple):
            args = ", ".join(_annotation_to_string(elt) for elt in slice_node.elts)
        else:
            args = _annotation_to_string(slice_node)
        return f"{value}[{args}]"
    elif isinstance(annotation, ast.Attribute):
        # e.g., typing.List
        return f"{_annotation_to_string(annotation.value)}.{annotation.attr}"
    elif isinstance(annotation, ast.Index):
        # For older Python versions (<3.9), where slice may be wrapped in Index
        return _annotation_to_string(annotation.value)
    else:
        # Fallback: use ast.unparse if available (Python 3.9+), otherwise dump
        try:
            return ast.unparse(annotation)
        except AttributeError:
            return ast.dump(annotation)


def load_skill_from_source(source_code: str) -> SkillSpec:
    """
    Load a skill specification from raw Python source code.

    Args:
        source_code (str): The source code of a single annotated Python function.

    Returns:
        SkillSpec: The parsed skill specification.

    Raises:
        ValueError: If the source code does not define exactly one valid annotated function.
    """
    name, inputs, outputs = parse_function_signature(source_code)
    return SkillSpec(
        name=name,
        inputs=inputs,
        outputs=outputs,
        source_code=source_code.strip()
    )


def simulate_skill(skill_spec: SkillSpec, input_dict: Dict[str, Any]) -> Any:
    """
    Safely execute a skill function in a restricted environment with provided inputs,
    and validate I/O compliance.

    Args:
        skill_spec (SkillSpec): The skill specification to execute.
        input_dict (Dict[str, Any]): Input arguments matching the function's parameters.

    Returns:
        Any: The return value of the executed function.

    Raises:
        ValueError: If inputs don't match expected parameters or types (basic check).
        RuntimeError: If execution fails due to code errors.
    """
    # Basic input validation: check parameter names
    expected_params = set(skill_spec.inputs.keys())
    provided_params = set(input_dict.keys())
    if expected_params != provided_params:
        missing = expected_params - provided_params
        extra = provided_params - expected_params
        msg = ""
        if missing:
            msg += f"Missing inputs: {missing}. "
        if extra:
            msg += f"Unexpected inputs: {extra}."
        raise ValueError(msg.strip())

    # Write source to a temporary file to avoid exec issues with complex scoping
    fd, temp_path = tempfile.mkstemp(suffix='.py')
    try:
        os.close(fd)  # Required on Windows to allow deletion later
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(skill_spec.source_code)

        # Create a restricted global namespace
        restricted_globals = {
            "__builtins__": {
                "len": len,
                "range": range,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "abs": abs,
                "max": max,
                "min": min,
                "sum": sum,
                "round": round,
                "isinstance": isinstance,
                "type": type,
                "Exception": Exception,
                "ValueError": ValueError,
                "TypeError": TypeError,
                "RuntimeError": RuntimeError,
            }
        }

        # Execute the module
        with open(temp_path, 'r', encoding='utf-8') as f:
            code = compile(f.read(), temp_path, 'exec')
            exec(code, restricted_globals)

        # Retrieve the function
        func = restricted_globals.get(skill_spec.name)
        if func is None:
            raise RuntimeError(f"Function '{skill_spec.name}' not found after execution.")

        # Call the function
        result = func(**input_dict)
        return result

    finally:
        os.unlink(temp_path)


def compute_skill_hash(skill_spec: SkillSpec) -> str:
    """
    Compute a deterministic SHA-256 hash of a SkillSpec by normalizing its contents.

    The hash is computed over:
      - function name
      - sorted JSON of inputs
      - sorted JSON of outputs
      - normalized source code (stripped and with consistent line endings)

    Args:
        skill_spec (SkillSpec): The skill specification to hash.

    Returns:
        str: Hexadecimal SHA-256 hash string.
    """
    # Normalize source: strip and use \n for line endings
    normalized_source = '\n'.join(skill_spec.source_code.strip().splitlines())

    # Use stable JSON serialization with sorted keys
    data = {
        "name": skill_spec.name,
        "inputs": json.dumps(skill_spec.inputs, sort_keys=True, separators=(',', ':')),
        "outputs": json.dumps(skill_spec.outputs, sort_keys=True, separators=(',', ':')),
        "source_code": normalized_source
    }

    # Serialize the entire structure deterministically
    serialized = json.dumps(data, sort_keys=True, separators=(',', ':'))
    hash_obj = hashlib.sha256(serialized.encode('utf-8'))
    return hash_obj.hexdigest()