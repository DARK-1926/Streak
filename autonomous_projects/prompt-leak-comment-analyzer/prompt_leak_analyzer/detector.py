import re
from typing import List, Tuple

# Common patterns for prompt‑leak comments
_PATTERN = re.compile(r"#\s*Prompt:\s*.*", re.IGNORECASE)

def detect(source: str) -> List[Tuple[int, str]]:
    """Return a list of (line_number, line) where a prompt‑leak comment is found.

    Args:
        source: The full source code as a string.
    Returns:
        List of tuples with 1‑based line numbers and the offending line.
    """
    results = []
    for i, line in enumerate(source.splitlines(), start=1):
        if _PATTERN.search(line):
            results.append((i, line))
    return results

def strip(source: str) -> str:
    """Remove all prompt‑leak comments from the source code.

    Args:
        source: The original source code.
    Returns:
        Cleaned source code with leak comments removed.
    """
    cleaned_lines = []
    for line in source.splitlines():
        if not _PATTERN.search(line):
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines) + ("\n" if source.endswith("\n") else "")
