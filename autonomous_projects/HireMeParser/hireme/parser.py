"""Parser module for 'Who wants to be hired?' Hacker News posts."""

import re
from typing import Dict


class ValidationError(ValueError):
    """Raised when a parsed post fails validation against the expected schema."""


# Pre-compiled regex patterns for performance and readability
_LOCATION_PATTERN = re.compile(r"^Location:\s*(.+)$", re.MULTILINE | re.IGNORECASE)
_REMOTE_PATTERN = re.compile(r"^Remote:\s*(.+)$", re.MULTILINE | re.IGNORECASE)
_RELOCATE_PATTERN = re.compile(
    r"^Willing to relocate:\s*(.+)$", re.MULTILINE | re.IGNORECASE
)
_TECHNOLOGIES_PATTERN = re.compile(
    r"^Technologies:\s*(.+)$", re.MULTILINE | re.IGNORECASE
)
_RESUME_PATTERN = re.compile(r"^(?:Résumé|Resume|CV):\s*(.+)$", re.MULTILINE | re.IGNORECASE)
_EMAIL_PATTERN = re.compile(r"^Email:\s*(.+)$", re.MULTILINE | re.IGNORECASE)

# RFC5322-lite email regex (simplified but reasonably strict)
_EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)


def parse_hn_hireme_post(content: str) -> Dict[str, str]:
    """Parse a 'Who wants to be hired?' Hacker News post into a structured dictionary.

    Extracts and validates the following fields from the input content:
        - Location
        - Remote
        - Willing to relocate
        - Technologies
        - Résumé/CV
        - Email

    All fields are required. The function normalizes field names to snake_case keys.

    Args:
        content: The raw text of the HN post.

    Returns:
        A dictionary with normalized keys and extracted values.

    Raises:
        ValidationError: If any required field is missing, empty, or fails validation.
    """
    if not isinstance(content, str):
        raise ValidationError("Input content must be a string.")

    def _extract(pattern: re.Pattern, field_name: str) -> str:
        match = pattern.search(content)
        if not match:
            raise ValidationError(f"Missing required field: {field_name}")
        value = match.group(1).strip()
        if not value:
            raise ValidationError(f"Field '{field_name}' must not be empty.")
        return value

    location = _extract(_LOCATION_PATTERN, "Location")
    remote = _extract(_REMOTE_PATTERN, "Remote")
    willing_to_relocate = _extract(_RELOCATE_PATTERN, "Willing to relocate")
    technologies = _extract(_TECHNOLOGIES_PATTERN, "Technologies")
    resume_cv = _extract(_RESUME_PATTERN, "Résumé/CV")
    email_raw = _extract(_EMAIL_PATTERN, "Email")

    # Validate email format
    if not _EMAIL_REGEX.match(email_raw):
        raise ValidationError(f"Invalid email format: {email_raw}")

    # Validate technologies is non-empty and doesn't contain resume-like content
    technologies_stripped = technologies.strip()
    if not technologies_stripped:
        raise ValidationError("Technologies field must not be empty.")
    # Additional check to prevent capturing resume line
    if technologies_stripped.startswith(("Résumé:", "Resume:", "CV:")):
        raise ValidationError("Technologies field must not be empty.")

    return {
        "location": location,
        "remote": remote,
        "willing_to_relocate": willing_to_relocate,
        "technologies": technologies,
        "resume_cv": resume_cv,
        "email": email_raw,
    }