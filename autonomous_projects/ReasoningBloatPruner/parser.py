import json
from typing import Iterable, Iterator

from models import TraceEntry


def parse_trace_lines(lines: Iterable[str]) -> Iterator[TraceEntry]:
    """Parse an iterable of JSONL strings into validated TraceEntry objects.

    This pure function processes each input line, strips surrounding whitespace,
    and attempts to decode it as JSON. It safely extracts the required fields
    using dictionary .get() calls to avoid KeyError exceptions. Lines that are
    empty, contain malformed JSON, lack required fields, or fail dataclass
    validation constraints are silently skipped.

    Args:
        lines: An iterable of strings representing JSON-encoded trace steps.

    Yields:
        TraceEntry instances that successfully pass parsing and validation.
    """
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        if not isinstance(data, dict):
            continue

        entry_id = data.get("id")
        content = data.get("content")
        tokens = data.get("tokens")

        if not isinstance(content, str):
            continue
        if not isinstance(tokens, (int, float)):
            continue
        if not isinstance(entry_id, (int, str)):
            continue

        try:
            token_count = int(tokens)
            entry = TraceEntry(id=int(entry_id), content=content, tokens=token_count)
            yield entry
        except (ValueError, TypeError):
            continue