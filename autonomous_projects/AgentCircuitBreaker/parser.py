import json
from typing import Iterable, Iterator

from models import LogEntry


def parse_log_stream(lines: Iterable[str]) -> Iterator[LogEntry]:
    for line in lines:
        try:
            payload = json.loads(line)
            provider = str(payload["provider"])
            status_code = int(payload["status_code"])
            latency_ms = float(payload["latency_ms"])
            timestamp = str(payload["timestamp"])

            yield LogEntry(
                provider=provider,
                status_code=status_code,
                latency_ms=latency_ms,
                timestamp=timestamp,
            )
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            continue