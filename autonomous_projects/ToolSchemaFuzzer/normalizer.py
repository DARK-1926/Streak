from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class NormalizedField:
    """Represents a single field extracted from a JSON schema."""
    name: str
    expected_type: str
    required: bool
    nested_schema: Optional['NormalizedSchema'] = None


@dataclass(frozen=True)
class NormalizedSchema:
    """Represents a normalized, validated internal specification of a JSON schema."""
    fields: List[NormalizedField]
    raw: Dict[str, Any]


def _validate_schema_node(node: Dict[str, Any]) -> None:
    """Validate the structural integrity of a single JSON schema node."""
    if not isinstance(node, dict):
        raise ValueError("Schema node must be a dictionary.")
    if "type" not in node or not isinstance(node["type"], str):
        raise ValueError("Schema node must contain a string 'type' key.")
    if "required" in node:
        req = node["required"]
        if not isinstance(req, list) or not all(isinstance(k, str) for k in req):
            raise ValueError("'required' must be a list of strings.")
    if node["type"] == "object":
        if "properties" not in node or not isinstance(node["properties"], dict):
            raise ValueError("Object type must define a 'properties' dictionary.")
    if node["type"] == "array":
        if "items" not in node or not isinstance(node["items"], dict):
            raise ValueError("Array type must define an 'items' dictionary.")


def _build_fields(
    properties: Dict[str, Any], required_keys: List[str]
) -> List[NormalizedField]:
    """Recursively build normalized fields from schema properties."""
    normalized: List[NormalizedField] = []
    for key in sorted(properties.keys()):
        prop_def = properties[key]
        _validate_schema_node(prop_def)
        prop_type = prop_def["type"]
        is_required = key in required_keys
        nested: Optional[NormalizedSchema] = None

        if prop_type == "object":
            nested = normalize_schema(prop_def)
        elif prop_type == "array":
            nested = normalize_schema(prop_def["items"])

        normalized.append(NormalizedField(
            name=key,
            expected_type=prop_type,
            required=is_required,
            nested_schema=nested
        ))
    return normalized


def normalize_schema(raw: dict) -> NormalizedSchema:
    """Parse raw JSON schema into a validated internal spec.

    Recursively processes a simplified JSON schema dictionary, validating
    structure and flattening nested objects into a deterministic traversal
    order. Raises ValueError on malformed specifications.

    Args:
        raw: The raw JSON schema dictionary.

    Returns:
        A strict NormalizedSchema instance.
    """
    if not isinstance(raw, dict):
        raise ValueError("Raw schema input must be a dictionary.")

    _validate_schema_node(raw)
    required_keys = raw.get("required", [])
    properties = raw.get("properties", {})

    fields = _build_fields(properties, required_keys) if isinstance(properties, dict) else []
    return NormalizedSchema(fields=fields, raw=raw)