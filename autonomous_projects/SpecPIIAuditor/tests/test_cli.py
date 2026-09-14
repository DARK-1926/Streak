import json
import os
import tempfile
from pathlib import Path

import pytest

from src.spec_pii_auditor.cli import load_tool_spec, load_pii_policy


def test_load_tool_spec_valid_json() -> None:
    """Test loading a valid tool spec JSON file."""
    tool_spec_content = {
        "output_schema": {
            "user_email": "string",
            "name": "string"
        }
    }
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(tool_spec_content, f)
        f.flush()
        f.close()  # Close file before unlinking on Windows
        try:
            result = load_tool_spec(f.name)
            assert result == tool_spec_content
        finally:
            os.unlink(f.name)


def test_load_tool_spec_empty_file_raises_value_error() -> None:
    """Test that loading an empty tool spec file raises ValueError."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        # File is empty
        pass
    try:
        with pytest.raises(ValueError, match="Tool spec file is empty"):
            load_tool_spec(f.name)
    finally:
        os.unlink(f.name)


def test_load_tool_spec_invalid_json_raises_json_decode_error() -> None:
    """Test that loading invalid JSON raises JSONDecodeError."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        f.write("{ invalid json }")
        f.flush()
    try:
        with pytest.raises(json.JSONDecodeError):
            load_tool_spec(f.name)
    finally:
        os.unlink(f.name)


def test_load_tool_spec_nonexistent_file_raises_file_not_found_error() -> None:
    """Test that loading a non-existent file raises FileNotFoundError."""
    nonexistent_path = "/this/path/does/not/exist.json"
    with pytest.raises(FileNotFoundError):
        load_tool_spec(nonexistent_path)


def test_load_pii_policy_valid_json_list_of_strings() -> None:
    """Test loading a valid PII policy JSON file containing a list of strings."""
    pii_policy_content = ["email", "address", "phone"]
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(pii_policy_content, f)
        f.flush()
        f.close()  # Close file handle before unlinking on Windows
        try:
            result = load_pii_policy(f.name)
            assert result == set(pii_policy_content)
        finally:
            os.unlink(f.name)


def test_load_pii_policy_empty_file_raises_value_error() -> None:
    """Test that loading an empty PII policy file raises ValueError."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        # File is empty
        pass
    try:
        with pytest.raises(ValueError, match="PII policy file is empty"):
            load_pii_policy(f.name)
    finally:
        os.unlink(f.name)


def test_load_pii_policy_invalid_json_raises_json_decode_error() -> None:
    """Test that loading invalid JSON for PII policy raises JSONDecodeError."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        f.write("[ invalid json ]")
        f.flush()
    try:
        with pytest.raises(json.JSONDecodeError):
            load_pii_policy(f.name)
    finally:
        os.unlink(f.name)


def test_load_pii_policy_non_list_raises_value_error() -> None:
    """Test that PII policy file not containing a JSON array raises ValueError."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump({"not": "a list"}, f)
        f.flush()
        f.close()  # Close file handle before unlinking on Windows
        try:
            with pytest.raises(ValueError, match="PII policy file must contain a JSON array"):
                load_pii_policy(f.name)
        finally:
            os.unlink(f.name)


def test_load_pii_policy_non_string_items_raises_value_error() -> None:
    """Test that PII policy containing non-string items raises ValueError."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(["email", 123, "address"], f)
        f.flush()
        f.close()
        try:
            with pytest.raises(ValueError, match="All items in PII policy must be strings"):
                load_pii_policy(f.name)
        finally:
            os.unlink(f.name)


def test_load_pii_policy_nonexistent_file_raises_file_not_found_error() -> None:
    """Test that loading a non-existent PII policy file raises FileNotFoundError."""
    nonexistent_path = "/this/path/does/not/exist.json"
    with pytest.raises(FileNotFoundError):
        load_pii_policy(nonexistent_path)