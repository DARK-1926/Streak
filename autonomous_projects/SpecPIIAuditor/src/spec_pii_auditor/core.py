from dataclasses import dataclass
from typing import Dict, List, Set, Any
import re


@dataclass(frozen=True)
class PIIAuditReport:
    """Represents the result of a PII audit on a tool's output schema.

    Attributes:
        is_compliant (bool): True if no fields in the output schema match any PII pattern.
        flagged_fields (List[str]): List of field names that matched at least one PII pattern.
        total_fields (int): Total number of fields in the output schema.
    """
    is_compliant: bool
    flagged_fields: List[str]
    total_fields: int


def audit_tool_spec_for_pii(tool_spec: Dict[str, Any], pii_policy: Set[str]) -> PIIAuditReport:
    """Analyzes a tool specification for potential PII leakage in its output schema.

    This function examines the 'output_schema' key of the provided tool_spec dictionary.
    It checks each field name in the output schema against a set of regex patterns defined
    in the pii_policy. A field is considered to potentially contain PII if any pattern
    in the policy matches the field name (using re.search).

    Args:
        tool_spec (Dict[str, Any]): The tool specification dictionary, expected to contain
            an 'output_schema' key with a dictionary value mapping field names to types.
        pii_policy (Set[str]): A set of regex patterns (as strings) used to identify field
            names that may contain PII. Patterns are used as-is with re.search.

    Returns:
        PIIAuditReport: A report detailing compliance status, flagged fields, and total fields.

    Note:
        - If 'output_schema' is missing or not a dictionary, it is treated as empty.
        - Patterns in pii_policy are not automatically anchored; they should be designed
          to match appropriately (e.g., '.*email.*' will match any field containing 'email').
    """
    # Extract output_schema, defaulting to empty dict if missing or invalid
    output_schema_raw = tool_spec.get('output_schema', {})
    if not isinstance(output_schema_raw, dict):
        output_schema = {}
    else:
        output_schema = output_schema_raw

    total_fields = len(output_schema)
    flagged_fields: List[str] = []

    # Precompile regex patterns for efficiency
    compiled_patterns = []
    for pattern in pii_policy:
        try:
            compiled = re.compile(pattern)
            compiled_patterns.append(compiled)
        except re.error:
            # Skip invalid regex patterns to avoid crashing; treat as non-matching
            continue

    # Check each field name against all compiled patterns
    for field_name in output_schema.keys():
        if not isinstance(field_name, str):
            # Skip non-string keys (though unlikely in valid schemas)
            continue
        for pattern in compiled_patterns:
            if pattern.search(field_name) is not None:
                flagged_fields.append(field_name)
                break  # No need to check other patterns once flagged

    is_compliant = len(flagged_fields) == 0
    return PIIAuditReport(
        is_compliant=is_compliant,
        flagged_fields=flagged_fields,
        total_fields=total_fields
    )