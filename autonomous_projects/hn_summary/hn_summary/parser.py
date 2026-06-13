import re
from dataclasses import dataclass
from typing import List, Iterable

@dataclass
class Post:
    title: str
    content: str
    tags: List[str]

def _extract_title(line: str) -> str:
    """Extract the title from a raw line.

    The raw line format is "Problem: <title>\nText: <body>".
    Anything before the first newline after "Problem:" is taken as the title.
    """
    m = re.match(r"Problem:\s*(.*)", line, re.IGNORECASE)
    return m.group(1).strip() if m else ""

def _extract_body(lines: Iterable[str]) -> str:
    """Join all lines after the first "Text:" marker into a single string."""
    body_parts = []
    capture = False
    for l in lines:
        if capture:
            body_parts.append(l.rstrip())
        elif l.lower().startswith("text:"):
            # start capturing after the "Text:" marker (exclude the marker itself)
            capture = True
            # include the remainder of the line after "Text:" if any
            remainder = l[5:].lstrip()
            if remainder:
                body_parts.append(remainder)
    return "\n".join(body_parts).strip()

def _detect_tags(text: str) -> List[str]:
    """Very simple heuristic tags based on keywords.

    Returns a list of lower‑case tags such as 'ai', 'design', 'startup', etc.
    """
    keywords = {
        "ai": ["anthropic", "gpt", "llm", "chatgpt", "claude"],
        "design": ["design", "webdesign", "ui", "ux"],
        "startup": ["lean", "startup", "incorruptible", "eric ries"],
        "ticket": ["ticketmaster", "ticket"],
        "security": ["phishing", "security", "call"],
        "opensource": ["open source", "opensource", "github"],
        "gaming": ["game", "golf", "mini"],
    }
    tags = []
    lowered = text.lower()
    for tag, words in keywords.items():
        if any(w in lowered for w in words):
            tags.append(tag)
    return tags

def parse_raw_feed(raw: str) -> List[Post]:
    """Parse a raw HN‑style feed into a list of :class:`Post` objects.

    The feed is a series of blocks separated by blank lines. Each block starts
    with a line like ``Problem: <title>`` followed by a line ``Text:`` and the
    body. The function is tolerant to missing sections – it will still return a
    ``Post`` with whatever information could be extracted.
    """
    posts: List[Post] = []
    # split on double newlines (allow Windows CRLF as well)
    blocks = re.split(r"\r?\n\r?\n", raw.strip())
    for block in blocks:
        lines = block.splitlines()
        if not lines:
            continue
        title = _extract_title(lines[0])
        body = _extract_body(lines[1:])
        tags = _detect_tags(body)
        posts.append(Post(title=title, content=body, tags=tags))
    return posts

def summarize_posts(posts: List[Post]) -> str:
    """Return a human‑readable summary of the supplied posts.

    The summary groups posts by the first tag (if any) and lists the title and a
    120‑character preview of the body.
    """
    from collections import defaultdict
    groups = defaultdict(list)
    for p in posts:
        key = p.tags[0] if p.tags else "untagged"
        groups[key].append(p)
    lines = []
    for tag in sorted(groups):
        lines.append(f"## {tag.capitalize()} ({len(groups[tag])})")
        for p in groups[tag]:
            preview = p.content.replace("\n", " ")[:120]
            if len(p.content) > 120:
                preview += "..."
            lines.append(f"- {p.title}: {preview}")
        lines.append("")
    return "\n".join(lines).strip()
