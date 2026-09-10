from typing import Dict, Any
from .models import SkillSpec
from .loader import parse_function_signature
from .hasher import normalize_and_hash
from .simulator import safe_exec_function
import json


def load_skill_from_source(source_code: str) -> SkillSpec:
    """
    Load a skill from its source code string and return a SkillSpec.

    Parses the function signature to extract name, inputs, and outputs,
    then constructs an immutable SkillSpec.

    Args:
        source_code (str): The source code of a single Python function with type annotations.

    Returns:
        SkillSpec: The parsed skill specification.

    Raises:
        ValueError: If parsing fails due to missing annotations, multiple functions, etc.
    """
    name, inputs, outputs = parse_function_signature(source_code)
    return SkillSpec(
        name=name,
        inputs=inputs,
        outputs=outputs,
        source_code=source_code
    )


def compute_skill_hash(skill_spec: SkillSpec) -> str:
    """
    Compute a deterministic SHA-256 hash for a SkillSpec.

    Serializes the name, inputs, outputs, and source_code into a stable JSON-like structure,
    normalizes it (lowercase, consistent line endings), and hashes using SHA-256.

    Args:
        skill_spec (SkillSpec): The skill specification to hash.

    Returns:
        str: The hexadecimal SHA-256 hash of the normalized representation.
    """
    # Build a dictionary that captures all semantic content
    data = {
        "name": skill_spec.name,
        "inputs": skill_spec.inputs,
        "outputs": skill_spec.outputs,
        "source_code": skill_spec.source_code
    }
    # Serialize deterministically
    serialized = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return normalize_and_hash(serialized)


def simulate_skill(skill_spec: SkillSpec, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate execution of a skill with given inputs in a restricted environment.

    Validates that input_data keys exactly match the expected input parameters,
    executes the function safely, and returns the result wrapped in {'output': ...}.

    Note: Full runtime type validation is not performed due to Python's dynamic nature,
    but structural validation (keys and presence of return annotation) is enforced.

    Args:
        skill_spec (SkillSpec): The skill specification to execute.
        input_data (Dict[str, Any]): Input arguments keyed by parameter name.

    Returns:
        Dict[str, Any]: A dictionary with a single key 'output' containing the result.

    Raises:
        ValueError: If input keys don't match expected parameters.
        RuntimeError: If execution fails in the sandboxed environment.
    """
    expected_params = set(skill_spec.inputs.keys())
    provided_params = set(input_data.keys())

    if expected_params != provided_params:
        missing = expected_params - provided_params
        extra = provided_params - expected_params
        msg_parts = []
        if missing:
            msg_parts.append(f"missing required inputs: {sorted(missing)}")
        if extra:
            msg_parts.append(f"unexpected inputs: {sorted(extra)}")
        raise ValueError("Input validation failed: " + "; ".join(msg_parts))

    result = safe_exec_function(
        func_code=skill_spec.source_code,
        func_name=skill_spec.name,
        args=input_data
    )

    return {"output": result}