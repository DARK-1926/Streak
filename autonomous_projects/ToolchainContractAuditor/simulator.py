from dataclasses import dataclass
from typing import Dict, List, Tuple, Iterable, Any, Set
import contracts


@dataclass
class AuditReport:
    """Structured report detailing the results of a deterministic toolchain audit."""
    valid: bool
    mismatches: List[Dict[str, Any]]
    circular_deps: List[Tuple[str, str]]
    missing_tools: List[str]


def audit_toolchain(registry: Dict[str, contracts.ToolContract], links: Iterable[Tuple[str, str]]) -> AuditReport:
    """
    Simulate execution flow in a single pass to validate a toolchain configuration.

    Iterates through the provided chain links exactly once, checking for missing
    tool definitions, I/O schema incompatibilities, and circular dependencies.
    This function is pure and produces no side effects.

    Args:
        registry: A mapping of tool names to their ToolContract definitions.
        links: An iterable of tuples representing the execution flow (source, target).

    Returns:
        An AuditReport containing validation results and any detected issues.
    """
    mismatches: List[Dict[str, Any]] = []
    circular_deps: List[Tuple[str, str]] = []
    missing_tools_set: Set[str] = set()
    visited: Set[str] = set()

    for src, tgt in links:
        if src not in registry:
            missing_tools_set.add(src)
        if tgt not in registry:
            missing_tools_set.add(tgt)

        if tgt in visited:
            circular_deps.append((src, tgt))

        visited.add(src)
        visited.add(tgt)

        if src in registry and tgt in registry:
            try:
                errors = contracts.validate_io_compatibility(
                    registry[src].output_schema,
                    registry[tgt].input_schema
                )
                for err in errors:
                    mismatches.append({
                        "source": src,
                        "target": tgt,
                        "error": err
                    })
            except Exception:
                mismatches.append({
                    "source": src,
                    "target": tgt,
                    "error": "Unexpected failure during I/O compatibility check."
                })

    is_valid = (
        len(mismatches) == 0 and
        len(circular_deps) == 0 and
        len(missing_tools_set) == 0
    )

    return AuditReport(
        valid=is_valid,
        mismatches=mismatches,
        circular_deps=circular_deps,
        missing_tools=sorted(list(missing_tools_set))
    )