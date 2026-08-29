"""
router.py

Deterministic I/O chain routing and compatibility verification for SkillSpecAuditor.
Provides pure functions to resolve execution chains based on stdout/stdin contract
matching and to validate chain integrity. Contains zero side-effects.
"""

from typing import List, Optional, Set

from skill_spec import SkillDef


def resolve_chain(skills: List[SkillDef], start_type: str, end_type: str) -> List[SkillDef]:
    """
    Resolve a deterministic execution chain matching I/O types from start to end.

    Args:
        skills: Ordered list of available skill definitions.
        start_type: The stdin_type to start the chain.
        end_type: The stdout_type to terminate the chain.

    Returns:
        A list of SkillDef instances representing the resolved execution chain.
    """
    entry_skill = next((s for s in skills if s.stdin_type == start_type), None)
    if entry_skill is None:
        return []

    chain: List[SkillDef] = [entry_skill]
    visited: Set[str] = {entry_skill.name}
    current = entry_skill

    while current.stdout_type != end_type:
        prev_stdout = current.stdout_type
        if prev_stdout is None:
            return []

        next_skill: Optional[SkillDef] = next(
            (s for s in skills if s.stdin_type == prev_stdout and s.name not in visited), None
        )

        if next_skill is None:
            return []

        if next_skill.name in visited:
            return chain

        visited.add(next_skill.name)
        chain.append(next_skill)
        current = next_skill

    return chain


def verify_chain_compatibility(chain: List[SkillDef]) -> List[str]:
    """
    Perform a single-pass validation of a resolved skill chain.

    Checks adjacent skills for I/O contract compatibility and generates
    descriptive warnings or errors for any mismatches or risky configurations.

    Args:
        chain: Ordered list of SkillDef instances representing the execution chain.

    Returns:
        A list of strings describing incompatibility warnings or errors.
        An empty list indicates full compatibility.
    """
    issues: List[str] = []
    for i in range(len(chain) - 1):
        src = chain[i]
        dst = chain[i + 1]

        if src.stdout_type is None:
            issues.append(
                f"Warning: Skill '{src.name}' has no stdout_type, "
                f"chain may terminate prematurely before '{dst.name}'."
            )
        elif dst.stdin_type is None:
            issues.append(
                f"Warning: Skill '{dst.name}' has no stdin_type, "
                f"acting as wildcard for '{src.name}' output."
            )
        elif src.stdout_type != dst.stdin_type:
            issues.append(
                f"Error: Mismatch between '{src.name}' stdout_type "
                f"('{src.stdout_type}') and '{dst.name}' stdin_type "
                f"('{dst.stdin_type}')."
            )

    return issues