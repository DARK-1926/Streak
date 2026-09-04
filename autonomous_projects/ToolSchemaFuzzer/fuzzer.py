import copy
import random
from dataclasses import dataclass
from typing import Any, Dict, Iterable

from normalizer import NormalizedField, NormalizedSchema


@dataclass(frozen=True)
class FuzzVariant:
    """Represents a single fuzzed payload variant with execution metadata."""
    payload: Dict[str, Any]
    strategy: str
    description: str = ""
    seed: int = 0


def _generate_base_payload(schema: NormalizedSchema, rng: random.Random) -> Dict[str, Any]:
    """Construct a minimally valid JSON payload from a normalized schema."""
    payload: Dict[str, Any] = {}
    for field in schema.fields:
        if field.expected_type == "string":
            payload[field.name] = "valid_string"
        elif field.expected_type == "integer":
            payload[field.name] = 42
        elif field.expected_type == "number":
            payload[field.name] = 3.14
        elif field.expected_type == "boolean":
            payload[field.name] = True
        elif field.expected_type == "null":
            payload[field.name] = None
        elif field.expected_type == "array":
            payload[field.name] = ["item_a", "item_b"]
        elif field.expected_type == "object":
            if field.nested_schema is not None:
                payload[field.name] = _generate_base_payload(field.nested_schema, rng)
            else:
                payload[field.name] = {"nested_key": "nested_value"}
        else:
            payload[field.name] = None
    return payload


def _mutate_omit_required(payload: Dict[str, Any], field: NormalizedField) -> Dict[str, Any]:
    """Remove a mandatory field from the payload to test parser resilience."""
    if field.required and field.name in payload:
        del payload[field.name]
    return payload


def _mutate_inject_extra(payload: Dict[str, Any], field: NormalizedField, rng: random.Random) -> Dict[str, Any]:
    """Insert an unexpected key-value pair into the payload."""
    extra_key = f"_fuzz_extra_{rng.randint(1000, 9999)}"
    payload[extra_key] = f"injected_{rng.randint(0, 100)}"
    return payload


def _mutate_type_mismatch(payload: Dict[str, Any], field: NormalizedField, rng: random.Random) -> Dict[str, Any]:
    """Replace the field value with a deliberately incompatible data type."""
    if field.name not in payload:
        return payload
    mismatch_lookup = {
        "string": 9999,
        "integer": "not_an_integer",
        "number": False,
        "boolean": {"unexpected": "dict"},
        "null": 12345,
        "array": "not_an_array",
        "object": [1, 2, 3],
    }
    payload[field.name] = mismatch_lookup.get(field.expected_type, "type_mismatch")
    return payload


def _mutate_boundary_values(payload: Dict[str, Any], field: NormalizedField, rng: random.Random) -> Dict[str, Any]:
    """Assign extreme, empty, or boundary values to the target field."""
    if field.name not in payload:
        return payload
    boundary_lookup = {
        "string": "",
        "integer": 9223372036854775807,
        "number": 1.7976931348623157e+308,
        "boolean": False,
        "null": None,
        "array": [],
        "object": {},
    }
    payload[field.name] = boundary_lookup.get(field.expected_type, None)
    return payload


def _mutate_deep_truncate(payload: Dict[str, Any], field: NormalizedField) -> Dict[str, Any]:
    """Truncate nested structures or complex types to empty containers."""
    if field.name not in payload:
        return payload
    current_val = payload[field.name]
    if isinstance(current_val, dict):
        payload[field.name] = {}
    elif isinstance(current_val, list):
        payload[field.name] = []
    else:
        payload[field.name] = None
    return payload


def generate_variants(schema: NormalizedSchema, seed: int = 42) -> Iterable[FuzzVariant]:
    """
    Generate deterministic fuzz variants for a normalized schema.

    Applies five distinct mutation strategies to each top-level field,
    yielding exactly one variant per strategy per field. Uses a seeded
    RNG to guarantee reproducible outputs across runs.
    """
    rng = random.Random(seed)
    base_payload = _generate_base_payload(schema, rng)

    strategies = [
        ("omit_required", "Drops a required field from the payload."),
        ("inject_extra", "Injects an unexpected extra key into the payload."),
        ("type_mismatch", "Replaces field value with an incompatible type."),
        ("boundary_values", "Sets field value to extreme or empty boundaries."),
        ("deep_truncate", "Truncates or empties nested object structures."),
    ]

    for field in schema.fields:
        for strategy_name, base_desc in strategies:
            try:
                mutated = copy.deepcopy(base_payload)
                if strategy_name == "omit_required":
                    mutated = _mutate_omit_required(mutated, field)
                elif strategy_name == "inject_extra":
                    mutated = _mutate_inject_extra(mutated, field, rng)
                elif strategy_name == "type_mismatch":
                    mutated = _mutate_type_mismatch(mutated, field, rng)
                elif strategy_name == "boundary_values":
                    mutated = _mutate_boundary_values(mutated, field, rng)
                elif strategy_name == "deep_truncate":
                    mutated = _mutate_deep_truncate(mutated, field)

                yield FuzzVariant(
                    payload=mutated,
                    strategy=strategy_name,
                    description=f"{base_desc} Target field: '{field.name}'."
                )
            except Exception as exc:
                yield FuzzVariant(
                    payload=base_payload,
                    strategy=strategy_name,
                    description=f"Mutation failed for '{field.name}': {exc}"
                )