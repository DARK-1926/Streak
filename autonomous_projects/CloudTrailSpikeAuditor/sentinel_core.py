import json
from typing import Any, Dict, Iterable

HIGH_RISK_EVENTS = frozenset({
    "RunInstances",
    "CreateVolume",
    "CreateBucket",
    "AllocateAddress",
})


def analyze_provisioning_spikes(
    lines: Iterable[str], spike_threshold: int = 100
) -> Dict[str, Any]:
    """
    Analyzes CloudTrail JSONL lines for provisioning spikes in a single pass.

    Parses each line and tracks the frequency of high-risk AWS API calls.
    Malformed JSON lines are silently ignored.

    Args:
        lines: An iterable of JSON-formatted strings.
        spike_threshold: The maximum allowed count before an event is flagged.

    Returns:
        A summary dictionary containing:
            - total_events (int): Total number of successfully parsed events.
            - spikes (Dict[str, int]): High-risk events exceeding the threshold.
            - is_anomalous (bool): True if any spikes were detected.
    """
    event_counts: Dict[str, int] = {event: 0 for event in HIGH_RISK_EVENTS}
    total_events = 0

    for line in lines:
        try:
            event_data = json.loads(line)
        except json.JSONDecodeError:
            continue

        total_events += 1
        event_name = event_data.get("eventName")

        if event_name in HIGH_RISK_EVENTS:
            event_counts[event_name] += 1

    spikes = {
        event: count
        for event, count in event_counts.items()
        if count > spike_threshold
    }

    return {
        "total_events": total_events,
        "spikes": spikes,
        "is_anomalous": bool(spikes),
    }