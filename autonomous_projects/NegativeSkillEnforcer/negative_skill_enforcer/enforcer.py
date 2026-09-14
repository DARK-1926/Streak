"""Module for enforcing negative skill specifications against agent skill source code."""

from dataclasses import dataclass
from typing import List

from negative_skill_enforcer.ast_analyzer import (
    extract_function_nodes,
    check_function_raises_exception,
)
from negative_skill_enforcer.spec import NegativeSkillSpec


@dataclass(frozen=True)
class EnforcementReport:
    """Report of violations found when enforcing a negative skill specification.

    Attributes:
        missing_functions: List of function names that are declared as forbidden
            in the spec but are not defined in the skill source code.
        incorrect_exceptions: List of function names that are defined but do not
            raise the expected exception type as specified.
    """

    missing_functions: List[str]
    incorrect_exceptions: List[str]


def enforce_negative_skills(
    skill_source: str, spec: NegativeSkillSpec
) -> EnforcementReport:
    """Enforce a negative skill specification against agent skill source code.

    This function verifies that every function listed in the spec's
    `forbidden_functions` is both present in the source code and raises the
    expected exception type.

    Args:
        skill_source: The Python source code of the agent's skill module as a string.
        spec: A validated NegativeSkillSpec defining which functions must be
            present and what exception they must raise.

    Returns:
        An EnforcementReport detailing any missing functions or functions that
        do not raise the correct exception.

    Raises:
        ValueError: If the skill_source contains a syntax error.
    """
    function_nodes = extract_function_nodes(skill_source)

    missing_functions = []
    incorrect_exceptions = []

    for func_name, expected_exception in spec.forbidden_functions.items():
        if func_name not in function_nodes:
            missing_functions.append(func_name)
        else:
            func_node = function_nodes[func_name]
            if not check_function_raises_exception(func_node, expected_exception):
                incorrect_exceptions.append(func_name)

    return EnforcementReport(
        missing_functions=missing_functions,
        incorrect_exceptions=incorrect_exceptions,
    )