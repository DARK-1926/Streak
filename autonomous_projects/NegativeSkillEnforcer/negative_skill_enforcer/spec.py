"""Module for defining and loading negative skill specifications."""

import re
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class NegativeSkillSpec:
    """Specification of forbidden functions and their required exception types.

    Attributes:
        forbidden_functions: A mapping from function names to the expected
            exception class name (e.g., 'PermissionError') that must be raised
            when the function is called.
    """

    forbidden_functions: Dict[str, str]

    def __post_init__(self) -> None:
        """Validate the contents of forbidden_functions after initialization."""
        if not isinstance(self.forbidden_functions, dict):
            raise ValueError("'forbidden_functions' must be a dictionary.")

        for func_name, exc_name in self.forbidden_functions.items():
            if not isinstance(func_name, str) or not func_name.isidentifier():
                raise ValueError(
                    f"Function name '{func_name}' is not a valid Python identifier."
                )
            if not isinstance(exc_name, str) or not exc_name:
                raise ValueError(
                    f"Exception name for function '{func_name}' must be a non-empty string."
                )
            if not _is_valid_identifier(exc_name):
                raise ValueError(
                    f"Exception name '{exc_name}' is not a valid Python identifier."
                )


def _is_valid_identifier(name: str) -> bool:
    """Check if a string is a valid Python identifier without dots."""
    return name.isidentifier() and "." not in name


def load_spec_from_dict(data: dict) -> NegativeSkillSpec:
    """Load a NegativeSkillSpec from a dictionary.

    Args:
        data: A dictionary expected to contain a 'forbidden_functions' key,
              whose value is a Dict[str, str] mapping function names to
              exception class names.

    Returns:
        A validated NegativeSkillSpec instance.

    Raises:
        ValueError: If the input dictionary is missing required keys,
                    or if any function or exception name is invalid.
    """
    if "forbidden_functions" not in data:
        raise ValueError("Input spec must contain 'forbidden_functions' key.")

    forbidden_functions = data["forbidden_functions"]

    if not isinstance(forbidden_functions, dict):
        raise ValueError("'forbidden_functions' must be a dictionary.")

    # Validate all entries
    validated_forbidden_functions: Dict[str, str] = {}
    for func_name, exc_name in forbidden_functions.items():
        if not isinstance(func_name, str):
            raise ValueError(f"Function name must be a string, got {type(func_name)}.")
        if not func_name.isidentifier():
            raise ValueError(f"Invalid function name: '{func_name}'.")

        if not isinstance(exc_name, str) or not exc_name:
            raise ValueError(
                f"Exception name for function '{func_name}' must be a non-empty string."
            )
        if not _is_valid_identifier(exc_name):
            raise ValueError(
                f"Exception name '{exc_name}' must be a valid Python identifier "
                f"without dots."
            )

        validated_forbidden_functions[func_name] = exc_name

    return NegativeSkillSpec(forbidden_functions=validated_forbidden_functions)