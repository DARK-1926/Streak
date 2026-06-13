import re
from typing import List, Dict

# Regular expression that captures the title after the literal "Problem:" up to the end of the line.
_TITLE_RE = re.compile(r"^Problem:\s*(?P<title>.+?)\s*$", re.MULTILINE)


def extract_titles(snippets: List[str]) -> List[Dict[str, str]]:
    """Extract HN post titles from a list of raw snippet strings.

    Each snippet follows the pattern::

        Problem: <title>\nText: <body>\n...

    The function returns a list of dictionaries with a single key ``"title"``
    containing the cleaned title string (without surrounding whitespace).

    Parameters
    ----------
    snippets: List[str]
        Raw snippet strings as supplied by the tests.

    Returns
    -------
    List[Dict[str, str]]
        A list where each element is ``{"title": <extracted title>}``.
    """
    results: List[Dict[str, str]] = []
    for snippet in snippets:
        # Search for the first line that starts with "Problem:".
        match = _TITLE_RE.search(snippet)
        if not match:
            # Fallback: if the pattern is not found, return an empty title so the
            # caller can handle the anomaly gracefully.
            title = ""
        else:
            title = match.group("title").strip()
        results.append({"title": title})
    return results
