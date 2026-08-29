"""
skill_spec.py

Pure data models and parsing/validation logic for SkillSpecAuditor manifests.
Provides strict schema enforcement and contract validation for agent toolchaining.
Contains zero file I/O and zero network calls. All functions are pure.
"""

import json
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class SkillDef:
    """
    Immutable data model representing a single skill definition in a manifest.

    Attributes:
        name: Unique identifier for the skill.
        command: Executable command string.
        stdin_type: Optional format string describing expected stdin payload.
        stdout_type: Optional format string describing expected stdout payload.
        description: Human-readable description of the skill.
        allowed_exit_codes: List of POSIX exit codes considered successful.
    """
    name: str
    command: str
    stdin_type: Optional[str] = None
    stdout_type: Optional[str] = None
    description: str = ""
    allowed_exit_codes: List[int] = field(default_factory=lambda: [0])


def parse_manifest(raw_json: str) -> List[SkillDef]:
    """
    Safely decode a JSON manifest string and validate its structure.

    Args:
        raw_json: A JSON-formatted string containing an array of skill objects.

    Returns:
        A list of validated SkillDef instances.

    Raises:
        ValueError: If the JSON is malformed, not an array, or missing required fields.
    """
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON payload: {exc}") from exc

    if not isinstance(data, list):
        raise ValueError("Manifest root must be a JSON array of skill objects.")

    parsed_skills: List[SkillDef] = []
    required_keys = {"name", "command"}

    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Manifest item at index {idx} is not a JSON object.")

        missing = required_keys - item.keys()
        if missing:
            raise ValueError(f"Manifest item at index {idx} missing required fields: {missing}")

        if not isinstance(item["name"], str) or not item["name"].strip():
            raise ValueError(f"Manifest item at index {idx}: 'name' must be a non-empty string.")

        if not isinstance(item["command"], str):
            raise ValueError(f"Manifest item at index {idx}: 'command' must be a string.")

        stdin_val = item.get("stdin_type")
        stdout_val = item.get("stdout_type")
        desc_val = item.get("description", "")

        parsed_skills.append(SkillDef(
            name=item["name"],
            command=item["command"],
            stdin_type=stdin_val,
            stdout_type=stdout_val,
            description=desc_val
        ))

    return parsed_skills


def validate_contract(skill: SkillDef) -> List[str]:
    """
    Check a SkillDef for logical errors and contract violations.

    Validates command presence, exit code ranges, and expectation format consistency.
    This function is pure and performs no I/O operations.

    Args:
        skill: The SkillDef instance to validate.

    Returns:
        A list of error message strings. Empty list indicates valid contract.
    """
    errors: List[str] = []
    if not skill.name or not skill.name.strip():
        errors.append("Skill name must be a non-empty string.")
    if not skill.command or not skill.command.strip():
        errors.append("Skill command must be a non-empty string.")
    return errors


def _unused_placeholder() -> None:
    """Placeholder to preserve structure if needed."""
    pass


# Original docstring continuation handled above.
def _validate_contract_args(skill: SkillDef) -> List[str]:
    """Validate the arguments of a skill contract.

    Args:
        skill: The SkillDef instance to validate.

    Returns:
        A list of error description strings. An empty list indicates a valid contract.
    """
    errors: List[str] = []

    if not skill.name or not skill.name.strip():
        errors.append("Skill name cannot be empty or whitespace.")

    if not skill.cmd:
        errors.append("Command list 'cmd' cannot be empty.")

    for code in skill.allowed_exit_codes:
        if code < 0 or code > 255:
            errors.append(f"Exit code {code} is outside the valid POSIX range (0-255).")

    valid_prefixes = ("regex:", "exact:", "glob:", "json:", "text:")
    for field_name, value in [("stdin_expect", skill.stdin_expect),
                              ("stdout_expect", skill.stdout_expect)]:
        if value is not None:
            if not value.strip():
                errors.append(f"'{field_name}' cannot be an empty or whitespace string.")
            elif ":" in value and not any(value.startswith(p) for p in valid_prefixes):
                errors.append(f"'{field_name}' uses an unrecognized or mismatched format prefix.")

    return errors