import json
import sys
from typing import Iterable, Dict, Any


def parse_log_stream(lines: Iterable[str]) -> Iterable[Dict[str, Any]]:
    """
    Parse an iterable of JSONL log lines into an iterable of dictionaries.

    Iterates over the provided lines, strips whitespace, and skips empty lines.
    Each non-empty line is parsed using json.loads(). Valid dictionary results
    are yielded immediately. Lines that fail JSON parsing are skipped, with a
    warning written to stderr to aid debugging without interrupting the stream.
    This function performs zero file I/O, maintains pure data transformation
    semantics, and relies solely on the Python standard library.

    Args:
        lines: An iterable of strings representing JSONL log entries.

    Yields:
        Dict[str, Any]: Parsed dictionary objects from valid JSON lines.
    """
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, dict):
                yield parsed
        except json.JSONDecodeError as exc:
            sys.stderr.write(f"Warning: Invalid JSON line skipped: {exc}\n")
        except Exception as exc:
            sys.stderr.write(f"Warning: Unexpected parsing error skipped: {exc}\n")