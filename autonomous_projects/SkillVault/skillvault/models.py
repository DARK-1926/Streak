from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class SkillSpec:
    """
    Immutable specification of a reusable agent skill.

    Attributes:
        name (str): The name of the skill function.
        inputs (Dict[str, str]): Mapping from parameter names to their type annotations as strings.
        outputs (str): The return type annotation as string.
        source_code (str): The full source code of the skill function as a string.
    """
    name: str
    inputs: Dict[str, str]
    outputs: str
    source_code: str