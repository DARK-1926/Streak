'''Utility helpers for searching and summarising HN posts.'''

from typing import List
from .models import HNPost


def filter_by_keyword(posts: List[HNPost], keyword: str) -> List[HNPost]:
    """Return posts whose title contains *keyword* (case‑insensitive)."""
    kw = keyword.lower()
    return [p for p in posts if kw in p.title.lower()]


def summarize_titles(posts: List[HNPost]) -> str:
    """Return a bullet‑list string of all post titles.

    Example output::

        - Ask HN: How are thinking efforts implemented?
        - Ask HN: Favorite text heavy blogs that are a joy to read?
    """
    return "\n".join(f"- {p.title}" for p in posts)
