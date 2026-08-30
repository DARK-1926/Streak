from typing import Iterable, Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class LeakSignature:
    """Represents a single detected context leak event with metadata."""
    type: str
    step: int
    severity: str
    tokens_wasted: int


@dataclass
class LeakReport:
    """Aggregated report of context leaks and compression recommendations."""
    total_events: int
    total_leaks: int
    signatures: List[LeakSignature]
    recommendation: str


def detect_leaks(events: Iterable[Dict[str, Any]], budget_limit: int) -> LeakReport:
    """
    Analyze an iterable of agent event logs in a single pass to detect context leaks.
    Tracks rolling context size, identifies monotonic growth without truncation,
    and flags steps exceeding budget thresholds. Returns a deterministic report.
    """
    signatures: List[LeakSignature] = []
    prev_size = 0
    monotonic_streak = 0
    total_events = 0

    for event in events:
        total_events += 1
        step = int(event.get("step", total_events))
        raw_size = event.get("context_size", event.get("tokens", 0))

        try:
            curr_size = int(float(raw_size)) if raw_size is not None else 0
        except (ValueError, TypeError):
            curr_size = 0

        is_growing = curr_size > prev_size
        monotonic_streak = monotonic_streak + 1 if is_growing else 0
        excess = max(0, curr_size - budget_limit)
        is_leak = excess > 0 or monotonic_streak >= 3

        if is_leak:
            waste = excess if excess > 0 else (curr_size - prev_size)
            severity = "high" if waste > budget_limit * 0.2 else "medium" if waste > budget_limit * 0.1 else "low"
            leak_type = "budget_overflow" if excess > 0 else "monotonic_growth"
            signatures.append(LeakSignature(type=leak_type, step=step, severity=severity, tokens_wasted=max(0, waste)))

        prev_size = curr_size

    total_leaks = len(signatures)
    if total_leaks == 0:
        rec = "Context usage is healthy. No compression needed."
    elif any(s.type == "budget_overflow" for s in signatures):
        rec = "Critical budget overflow detected. Implement aggressive sliding window truncation and tool output summarization."
    else:
        rec = "Monotonic context growth detected. Apply incremental deduplication and cap tool response payloads."

    return LeakReport(total_events=total_events, total_leaks=total_leaks, signatures=signatures, recommendation=rec)