import sys
from typing import List, Callable
from normalizer import normalize_schema, NormalizedSchema
from fuzzer import generate_variants, FuzzVariant
from validator import validate_variant, ValidationReport


def dummy_agent_parser(payload: dict) -> dict:
    """Dummy parser that deterministically fails based on mutation strategy markers."""
    marker = payload.get("strategy", "")
    if marker == "type_mismatch":
        raise TypeError("type_mismatch")
    if marker == "omit_required":
        raise KeyError("omit_required")
    return {"status": "ok"}


def test_normalize_schema() -> None:
    """Test 1: normalize_schema with valid dict -> assert NormalizedSchema fields."""
    raw_schema = {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "age": {"type": "integer"},
            "active": {"type": "boolean"}
        },
        "required": ["username", "age"]
    }
    schema = normalize_schema(raw_schema)
    assert isinstance(schema, NormalizedSchema), "Expected NormalizedSchema instance"
    assert hasattr(schema, "fields"), "NormalizedSchema must have 'fields' attribute"
    assert len(schema.fields) == 3, f"Expected 3 fields, got {len(schema.fields)}"
    field_names = {f.name for f in schema.fields}
    assert field_names == {"username", "age", "active"}, f"Field names mismatch: {field_names}"
    for field in schema.fields:
        assert hasattr(field, "required"), "NormalizedField must have 'required' attribute"
        if field.name in ("username", "age"):
            assert field.required is True, f"{field.name} should be required"
        else:
            assert field.required is False, f"{field.name} should not be required"
    print("PASS: test_normalize_schema")


def test_generate_variants_deterministic() -> None:
    """Test 2: generate_variants with seed=42 -> consume into list, assert deterministic count and strategy names."""
    raw_schema = {
        "type": "object",
        "properties": {"id": {"type": "integer"}, "tag": {"type": "string"}},
        "required": ["id"]
    }
    schema = normalize_schema(raw_schema)
    variants_run1: List[FuzzVariant] = list(generate_variants(schema, seed=42))
    variants_run2: List[FuzzVariant] = list(generate_variants(schema, seed=42))
    assert len(variants_run1) > 0, "Generator must yield at least one variant"
    assert len(variants_run1) == len(variants_run2), "Deterministic seed must produce identical count"
    for v1, v2 in zip(variants_run1, variants_run2):
        assert v1.strategy == v2.strategy, "Strategies must match across deterministic runs"
        assert v1.payload == v2.payload, "Payloads must match across deterministic runs"
    valid_strategies = {"omit_required", "inject_extra", "type_mismatch", "boundary_values", "deep_truncate"}
    observed_strategies = {v.strategy for v in variants_run1}
    assert observed_strategies.issubset(valid_strategies), f"Invalid strategies found: {observed_strategies - valid_strategies}"
    print("PASS: test_generate_variants_deterministic")


def test_validate_variant_exceptions() -> None:
    """Test 3: validate_variant with dummy_agent_parser -> assert exact exception_type captures and success flags."""
    v_type = FuzzVariant(payload={"strategy": "type_mismatch", "id": 1}, strategy="type_mismatch", seed=0)
    v_key = FuzzVariant(payload={"strategy": "omit_required", "id": 1}, strategy="omit_required", seed=0)
    v_ok = FuzzVariant(payload={"strategy": "inject_extra", "id": 1}, strategy="inject_extra", seed=0)

    r_type = validate_variant(v_type, dummy_agent_parser)
    assert isinstance(r_type, ValidationReport), "Must return ValidationReport"
    assert r_type.success is False, "type_mismatch should fail"
    assert r_type.exception_type == "TypeError", f"Expected TypeError, got {r_type.exception_type}"

    r_key = validate_variant(v_key, dummy_agent_parser)
    assert r_key.success is False, "omit_required should fail"
    assert r_key.exception_type == "KeyError", f"Expected KeyError, got {r_key.exception_type}"

    r_ok = validate_variant(v_ok, dummy_agent_parser)
    assert r_ok.success is True, "inject_extra should succeed"
    assert r_ok.exception_type is None, "Success should have no exception_type"
    assert r_ok.result == {"status": "ok"}, f"Expected ok status, got {r_ok.result}"
    print("PASS: test_validate_variant_exceptions")


def test_full_pipeline_integration() -> None:
    """Test 4: Full pipeline integration -> run generator through validator, collect reports, assert counts."""
    raw_schema = {
        "type": "object",
        "properties": {"val": {"type": "number"}, "name": {"type": "string"}},
        "required": ["val"]
    }
    schema = normalize_schema(raw_schema)
    variants = list(generate_variants(schema, seed=42))
    reports: List[ValidationReport] = []
    for variant in variants:
        variant.payload["strategy"] = variant.strategy
        report = validate_variant(variant, dummy_agent_parser)
        reports.append(report)

    assert len(reports) == len(variants), "Report count must match variant count"
    expected_type_err = sum(1 for v in variants if v.strategy == "type_mismatch")
    expected_key_err = sum(1 for v in variants if v.strategy == "omit_required")
    expected_success = len(variants) - expected_type_err - expected_key_err

    actual_type_err = sum(1 for r in reports if r.exception_type == "TypeError")
    actual_key_err = sum(1 for r in reports if r.exception_type == "KeyError")
    actual_success = sum(1 for r in reports if r.success)

    assert actual_type_err == expected_type_err, "TypeError count mismatch"
    assert actual_key_err == expected_key_err, "KeyError count mismatch"
    assert actual_success == expected_success, "Success count mismatch"
    print("PASS: test_full_pipeline_integration")


def main() -> None:
    """Execute all tests sequentially and handle failures gracefully."""
    try:
        test_normalize_schema()
        test_generate_variants_deterministic()
        test_validate_variant_exceptions()
        test_full_pipeline_integration()
        print("\nALL TESTS PASSED")
    except AssertionError as exc:
        print(f"\nTEST FAILED: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\nUNEXPECTED ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()