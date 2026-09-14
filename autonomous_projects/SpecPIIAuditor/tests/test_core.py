import pytest
from src.spec_pii_auditor.core import audit_tool_spec_for_pii, PIIAuditReport


def test_compliant_spec_no_matches() -> None:
    """Test a tool spec with no fields matching the PII policy."""
    tool_spec = {
        "output_schema": {
            "user_id": "string",
            "timestamp": "integer",
            "action_type": "string"
        }
    }
    pii_policy = {"email", "address", "phone"}
    report = audit_tool_spec_for_pii(tool_spec, pii_policy)
    expected = PIIAuditReport(
        is_compliant=True,
        flagged_fields=[],
        total_fields=3
    )
    assert report == expected


def test_non_compliant_with_email() -> None:
    """Test a tool spec containing a field that matches 'email' in the policy."""
    tool_spec = {
        "output_schema": {
            "user_email": "string",
            "name": "string"
        }
    }
    pii_policy = {"email", "ssn"}
    report = audit_tool_spec_for_pii(tool_spec, pii_policy)
    expected = PIIAuditReport(
        is_compliant=False,
        flagged_fields=["user_email"],
        total_fields=2
    )
    assert report == expected


def test_empty_output_schema() -> None:
    """Test a tool spec with an empty output_schema."""
    tool_spec = {"output_schema": {}}
    pii_policy = {"email"}
    report = audit_tool_spec_for_pii(tool_spec, pii_policy)
    expected = PIIAuditReport(
        is_compliant=True,
        flagged_fields=[],
        total_fields=0
    )
    assert report == expected


def test_malformed_tool_spec_missing_output_schema() -> None:
    """Test a tool spec that lacks the 'output_schema' key."""
    tool_spec = {"name": "example_tool", "description": "A sample tool"}
    pii_policy = {"email"}
    report = audit_tool_spec_for_pii(tool_spec, pii_policy)
    expected = PIIAuditReport(
        is_compliant=True,
        flagged_fields=[],
        total_fields=0
    )
    assert report == expected


def test_case_sensitive_matching_by_default() -> None:
    """Test that regex matching is case-sensitive unless policy uses (?i)."""
    tool_spec = {
        "output_schema": {
            "user_email": "string"
        }
    }
    # Policy uses uppercase EMAIL but field is lowercase — should not match
    pii_policy = {".*EMAIL.*"}
    report = audit_tool_spec_for_pii(tool_spec, pii_policy)
    expected = PIIAuditReport(
        is_compliant=True,
        flagged_fields=[],
        total_fields=1
    )
    assert report == expected


def test_case_insensitive_matching_with_flag() -> None:
    """Test that regex with (?i) enables case-insensitive matching."""
    tool_spec = {
        "output_schema": {
            "User_Email": "string"
        }
    }
    # Policy uses (?i) to ignore case
    pii_policy = {r"(?i).*email.*"}
    report = audit_tool_spec_for_pii(tool_spec, pii_policy)
    expected = PIIAuditReport(
        is_compliant=False,
        flagged_fields=["User_Email"],
        total_fields=1
    )
    assert report == expected


def test_invalid_regex_in_policy_is_skipped() -> None:
    """Test that invalid regex patterns in the policy are skipped without error."""
    tool_spec = {
        "output_schema": {
            "email_address": "string"
        }
    }
    # One valid pattern, one invalid (unbalanced bracket)
    pii_policy = {"email", "[invalid-regex"}
    report = audit_tool_spec_for_pii(tool_spec, pii_policy)
    # Should still flag due to "email" pattern
    expected = PIIAuditReport(
        is_compliant=False,
        flagged_fields=["email_address"],
        total_fields=1
    )
    assert report == expected


def test_non_string_field_keys_are_ignored() -> None:
    """Test that non-string keys in output_schema are skipped."""
    tool_spec = {
        "output_schema": {
            "valid_field": "string",
            123: "integer",  # Non-string key
            "another_valid": "string"
        }
    }
    pii_policy = {"valid"}
    report = audit_tool_spec_for_pii(tool_spec, pii_policy)
    # Only string keys are checked; both "valid_field" and "another_valid" match "valid"
    expected = PIIAuditReport(
        is_compliant=False,
        flagged_fields=["valid_field", "another_valid"],
        total_fields=3  # Total includes non-string key
    )
    assert report == expected