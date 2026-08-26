import json
import subprocess
import sys
from pathlib import Path
from typing import Dict

import pytest

from hireme.parser import parse_hn_hireme_post, ValidationError


# Valid full post example (based on real HN format)
VALID_POST = """Location: San Francisco, CA
Remote: Yes
Willing to relocate: Yes
Technologies: Python, JavaScript, React, PostgreSQL
Résumé: https://example.com/resume.pdf
Email: alice@example.com"""

EXPECTED_VALID_RESULT = {
    "location": "San Francisco, CA",
    "remote": "Yes",
    "willing_to_relocate": "Yes",
    "technologies": "Python, JavaScript, React, PostgreSQL",
    "resume_cv": "https://example.com/resume.pdf",
    "email": "alice@example.com",
}


def test_parse_valid_full_post() -> None:
    """Test parsing a valid full 'Who wants to be hired?' post."""
    result = parse_hn_hireme_post(VALID_POST)
    assert result == EXPECTED_VALID_RESULT


def test_parse_missing_field_raises_validation_error() -> None:
    """Test that missing any required field raises ValidationError."""
    # Remove the Email line
    invalid_post = VALID_POST.replace("Email: alice@example.com", "")
    with pytest.raises(ValidationError, match="Missing required field: Email"):
        parse_hn_hireme_post(invalid_post)


def test_parse_invalid_email_raises_validation_error() -> None:
    """Test that an invalid email format raises ValidationError."""
    invalid_post = VALID_POST.replace("alice@example.com", "not-an-email")
    with pytest.raises(ValidationError, match="Invalid email format: not-an-email"):
        parse_hn_hireme_post(invalid_post)


def test_parse_empty_technologies_raises_validation_error() -> None:
    """Test that empty Technologies field raises ValidationError."""
    invalid_post = VALID_POST.replace(
        "Technologies: Python, JavaScript, React, PostgreSQL", "Technologies: "
    )
    with pytest.raises(ValidationError, match="Technologies field must not be empty."):
        parse_hn_hireme_post(invalid_post)


def test_parse_handles_extra_whitespace() -> None:
    """Test that extra whitespace around values is stripped correctly."""
    post_with_whitespace = """Location:   New York, NY   
Remote:  No 
Willing to relocate:   Maybe  
Technologies:   Go, Docker, Kubernetes  
Résumé:   https://example.com/cv.pdf  
Email:   bob@example.org  """

    expected = {
        "location": "New York, NY",
        "remote": "No",
        "willing_to_relocate": "Maybe",
        "technologies": "Go, Docker, Kubernetes",
        "resume_cv": "https://example.com/cv.pdf",
        "email": "bob@example.org",
    }
    result = parse_hn_hireme_post(post_with_whitespace)
    assert result == expected


def test_cli_with_valid_input_file(tmp_path: Path) -> None:
    """Test CLI with a valid input file produces correct JSON output."""
    input_file = tmp_path / "valid_post.txt"
    input_file.write_text(VALID_POST, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "hireme.cli", "--input", str(input_file)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    parsed_output = json.loads(result.stdout)
    assert parsed_output == EXPECTED_VALID_RESULT


def test_cli_with_invalid_input_file(tmp_path: Path) -> None:
    """Test CLI with an invalid input file exits with code 1 and prints error."""
    invalid_post = VALID_POST.replace("Email: alice@example.com", "Email: invalid-email")
    input_file = tmp_path / "invalid_post.txt"
    input_file.write_text(invalid_post, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "hireme.cli", "--input", str(input_file)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent,
    )

    assert result.returncode == 1
    assert "Validation error:" in result.stderr
    assert "Invalid email format" in result.stderr
    assert result.stdout == ""


def test_cli_reads_from_stdin_when_no_input_specified() -> None:
    """Test CLI reads from stdin when --input is not provided."""
    result = subprocess.run(
        [sys.executable, "-m", "hireme.cli"],
        input=VALID_POST,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    parsed_output = json.loads(result.stdout)
    assert parsed_output == EXPECTED_VALID_RESULT


def test_cli_stdin_invalid_input() -> None:
    """Test CLI with invalid input via stdin exits with code 1."""
    invalid_post = VALID_POST.replace("Technologies: Python, JavaScript, React, PostgreSQL", "Technologies: ")
    result = subprocess.run(
        [sys.executable, "-m", "hireme.cli"],
        input=invalid_post,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent,
    )

    assert result.returncode == 1
    assert "Validation error:" in result.stderr
    assert "Technologies field must not be empty." in result.stderr
    assert result.stdout == ""