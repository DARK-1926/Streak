from dataclasses import dataclass
from typing import Dict, List, Iterable, Any

_TYPE_ALIASES: Dict[str, str] = {
    "string": "str", "str": "str",
    "integer": "int", "int": "int",
    "number": "float", "float": "float", "double": "float",
    "boolean": "bool", "bool": "bool",
    "array": "list", "list": "list",
    "object": "dict", "dict": "dict",
    "null": "none", "none": "none",
}


def _normalize_type_name(type_str: str) -> str:
    """Normalize a type string to a canonical Python type name."""
    if not isinstance(type_str, str):
        return str(type_str).strip().lower()
    return _TYPE_ALIASES.get(type_str.strip().lower(), type_str.strip().lower())


@dataclass
class ToolContract:
    """Represents a deterministic I/O contract for a single tool in a chain."""
    name: str
    input_schema: Dict[str, str]
    output_schema: Dict[str, str]


def check_type_drift(expected: str, actual: str) -> bool:
    """
    Determine if two type strings are incompatible after normalization.

    Args:
        expected: The expected type string from the target schema.
        actual: The actual type string from the source schema.

    Returns:
        True if a type drift (incompatibility) is detected, False otherwise.
    """
    return _normalize_type_name(expected) != _normalize_type_name(actual)


def validate_io_compatibility(src_out: Dict[str, str], tgt_in: Dict[str, str]) -> List[str]:
    """
    Validate compatibility between a source tool's output schema and a target tool's input schema.

    Args:
        src_out: The output schema dictionary of the source tool.
        tgt_in: The input schema dictionary of the target tool.

    Returns:
        A list of explicit mismatch error strings describing missing keys or type drifts.
    """
    errors: List[str] = []
    for key, expected_type in tgt_in.items():
        if key not in src_out:
            errors.append(f"Missing key: '{key}' required by target but not provided by source.")
        else:
            actual_type = src_out[key]
            if check_type_drift(expected_type, actual_type):
                errors.append(
                    f"Type drift on key '{key}': expected '{expected_type}', got '{actual_type}'."
                )
    return errors


def build_registry(contracts: Iterable[Dict[str, Any]]) -> Dict[str, ToolContract]:
    """
    Safely convert an iterable of raw contract dictionaries into a registry of ToolContract instances.

    Malformed entries are skipped gracefully with explicit KeyError and TypeError handling.
    This function is pure, deterministic, and performs no file I/O or side-effects.

    Args:
        contracts: An iterable of dictionaries representing raw tool contracts.

    Returns:
        A dictionary mapping tool names to their corresponding ToolContract instances.
    """
    registry: Dict[str, ToolContract] = {}
    for raw in contracts:
        try:
            if not isinstance(raw, dict):
                raise TypeError("Contract entry must be a dictionary.")

            name = raw["name"]
            input_schema = raw["input_schema"]
            output_schema = raw["output_schema"]

            if not isinstance(name, str):
                raise TypeError("Contract 'name' must be a string.")
            if not isinstance(input_schema, dict) or not isinstance(output_schema, dict):
                raise TypeError("Contract schemas must be dictionaries.")

            registry[name] = ToolContract(
                name=name,
                input_schema=input_schema,
                output_schema=output_schema
            )
        except (KeyError, TypeError):
            continue

    return registry