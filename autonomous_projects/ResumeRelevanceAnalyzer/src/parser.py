import re
from typing import Iterable, Dict, List


def parse_document(lines: Iterable[str]) -> Dict[str, List[str]]:
    """
    Parse a document (e.g., resume or job description) into structured sections.

    This function heuristically identifies section headers such as 'Experience:',
    'Skills:', etc., and groups subsequent lines under those sections until the
    next header is encountered. Each section's content is normalized by:
      - Converting to lowercase
      - Collapsing multiple whitespace characters into single spaces
      - Splitting into individual words

    Sections that are not present in the input are simply omitted from the output.
    The function is robust to empty inputs and malformed text.

    Args:
        lines: An iterable of strings representing the lines of the document.

    Returns:
        A dictionary mapping section names (without trailing colons) to lists of
        normalized words found in that section.
    """
    # Common section headers we expect to find (case-insensitive)
    # We match these at the start of a line, possibly with leading whitespace
    header_pattern = re.compile(r'^\s*(?P<header>[\w\s]+):\s*$')

    sections: Dict[str, List[str]] = {}
    current_section: str | None = None

    for line in lines:
        line = line.rstrip('\r\n')  # Remove line endings but preserve internal whitespace

        # Check if this line matches a section header
        match = header_pattern.match(line)
        if match:
            # Normalize header name: strip whitespace and remove colon
            raw_header = match.group('header')
            current_section = raw_header.strip().lower()
            # Initialize list for this section if not already present
            if current_section not in sections:
                sections[current_section] = []
            continue

        # If we're inside a section, process the line
        if current_section is not None:
            # Normalize whitespace: replace any sequence of whitespace with a single space
            normalized_line = re.sub(r'\s+', ' ', line.strip())
            if normalized_line:
                # Split into words and extend the current section's word list
                words = normalized_line.lower().split()
                sections[current_section].extend(words)

    return sections