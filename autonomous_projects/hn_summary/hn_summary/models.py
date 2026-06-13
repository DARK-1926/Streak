'''Data models for the hn_summary package.'''

from dataclasses import dataclass
from typing import List


@dataclass
class HNPost:
    """Represents a single Hacker News post snippet.

    Attributes
    ----------
    title: str
        The title of the post (e.g. "Ask HN: How are thinking efforts implemented?").
    text: str
        The raw body text that follows the title.
    """

    title: str
    text: str

    def keywords(self) -> List[str]:
        """Return a list of lower‑cased words from the title that are longer than 3 characters.
        This simple heuristic is enough for the demo tests.
        """
        return [w.lower() for w in self.title.split() if len(w) > 3]
