import ast
import tempfile
import os
from typing import Any, Dict
from .models import SkillSpec
from .loader import parse_function_signature
from .hasher import normalize_and_hash, stable_hash


def safe_exec_function(func_code: str, func_name: str, args: Dict[str, Any]) -> Any:
    """
    Safely execute a function from its source code in a restricted environment.

    Compiles the provided function code and executes it in a namespace with no builtins
    to prevent access to unsafe operations. Retrieves the function by name and calls it
    with the provided arguments.

    Args:
        func_code (str): The full source code containing the function definition.
        func_name (str): The name of the function to execute.
        args (Dict[str, Any]): Keyword arguments to pass to the function.

    Returns:
        Any: The return value of the executed function.

    Raises:
        RuntimeError: If any exception occurs during compilation, execution, or function call.
    """
    try:
        # Compile the function code
        compiled = compile(func_code, filename="<string>", mode="exec")
    except Exception as e:
        raise RuntimeError(f"Compilation failed: {e}")

    # Create a namespace with minimal safe builtins
    safe_builtins = {
        'int': int,
        'str': str,
        'float': float,
        'bool': bool,
        'list': list,
        'dict': dict,
        'tuple': tuple,
        'None': None,
        '__build_class__': __build_class__,
    }
    namespace = {"__builtins__": safe_builtins}

    try:
        # Execute the compiled code in the restricted namespace
        exec(compiled, namespace)
    except Exception as e:
        raise RuntimeError(f"Execution of function definition failed: {e}")

    if func_name not in namespace:
        raise RuntimeError(f"Function '{func_name}' not found in the provided source code.")

    func = namespace[func_name]

    # Ensure it's a callable
    if not callable(func):
        raise RuntimeError(f"'{func_name}' is not a callable function.")

    try:
        # Call the function with the provided arguments
        result = func(**args)
    except TypeError as e:
        raise e
    except Exception as e:
        raise RuntimeError(f"Function execution failed: {e}")

    return result


def simulate_skill(skill_spec: SkillSpec, input_dict: Dict[str, Any]) -> Any:
    """
    Simulate the execution of a skill using its SkillSpec and provided inputs.

    Validates that the input_dict keys match the expected input parameters in the SkillSpec.
    Executes the function in a safe, restricted environment and returns the result.

    Args:
        skill_spec (SkillSpec): The specification of the skill to simulate.
        input_dict (Dict[str, Any]): Input values keyed by parameter name.

    Returns:
        Any: The return value of the skill function.

    Raises:
        ValueError: If input_dict keys do not exactly match the skill's expected inputs.
        RuntimeError: If execution fails for any reason (compilation, safety, runtime error).
    """
    expected_inputs = set(skill_spec.inputs.keys())
    provided_inputs = set(input_dict.keys())

    if expected_inputs != provided_inputs:
        missing = expected_inputs - provided_inputs
        extra = provided_inputs - expected_inputs
        msg_parts = []
        if missing:
            msg_parts.append(f"missing required inputs: {sorted(missing)}")
        if extra:
            msg_parts.append(f"unexpected inputs: {sorted(extra)}")
        raise ValueError("Input validation failed: " + "; ".join(msg_parts))

    return safe_exec_function(skill_spec.source_code, skill_spec.name, input_dict)


def compute_skill_hash(skill_spec: SkillSpec) -> str:
    """
    Compute a deterministic SHA-256 hash for a SkillSpec.

    The hash is computed over a stable JSON representation of the SkillSpec's metadata
    (name, inputs, outputs) combined with a normalized version of the source code.

    Normalization of source code includes:
        - Stripping leading/trailing whitespace
        - Standardizing line endings to \\n
        - Converting to lowercase

    This ensures the hash is consistent across platforms and minor formatting differences.

    Args:
        skill_spec (SkillSpec): The skill specification to hash.

    Returns:
        str: The SHA-256 hexdigest representing the skill's content and interface.
    """
    # Prepare metadata dict for stable hashing
    metadata = {
        "name": skill_spec.name,
        "inputs": skill_spec.inputs,
        "outputs": skill_spec.outputs,
    }

    metadata_hash = stable_hash(metadata)
    source_hash = normalize_and_hash(skill_spec.source_code)

    # Combine both hashes to form the final skill hash
    combined = metadata_hash + source_hash
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()


def load_skill_from_source(source_code: str) -> SkillSpec:
    """
    Load a SkillSpec from raw Python function source code.

    Parses the function signature to extract name, input types, and output type.
    Validates that the source contains exactly one properly annotated function.

    Args:
        source_code (str): The source code string of a single Python function.

    Returns:
        SkillSpec: The parsed skill specification.

    Raises:
        ValueError: If parsing fails due to syntax errors, missing annotations, etc.
    """
    name, inputs, outputs = parse_function_signature(source_code)
    return SkillSpec(
        name=name,
        inputs=inputs,
        outputs=outputs,
        source_code=source_code
    )