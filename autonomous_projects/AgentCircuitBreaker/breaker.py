from collections import deque
from typing import Dict, Iterable

from models import CircuitState, LogEntry


def evaluate_circuit_states(
    entries: Iterable[LogEntry],
    window_size: int = 50,
    error_threshold: float = 0.4,
    cooldown_period: float = 10.0,
) -> Dict[str, CircuitState]:
    """Evaluate circuit breaker states for each provider in a single pass.

    Maintains a sliding window of request outcomes per provider, dynamically
    calculates error rates, and transitions circuit states according to a
    deterministic state machine (CLOSED -> OPEN -> HALF-OPEN). Latency values
    are tracked alongside status codes for potential downstream analysis.

    Args:
        entries: Iterable of parsed LogEntry objects.
        window_size: Maximum number of recent requests to consider per provider.
        error_threshold: Error rate fraction that triggers an OPEN state.
        cooldown_period: Time duration to wait while OPEN before transitioning to HALF-OPEN.

    Returns:
        Dictionary mapping provider identifiers to their final CircuitState.
    """
    windows: Dict[str, deque] = {}
    states: Dict[str, str] = {}
    last_updated_ts: Dict[str, str] = {}

    for entry in entries:
        try:
            provider = entry.provider
            if provider not in windows:
                windows[provider] = deque(maxlen=window_size)
                states[provider] = "CLOSED"
                last_updated_ts[provider] = entry.timestamp

            is_error = 1 if entry.status_code >= 400 else 0
            windows[provider].append((is_error, entry.latency_ms))

            window = windows[provider]
            error_rate = sum(item[0] for item in window) / len(window) if window else 0.0
            current_state = states[provider]

            if current_state == "CLOSED" and error_rate >= error_threshold:
                states[provider] = "OPEN"
                last_updated_ts[provider] = entry.timestamp
            elif current_state == "OPEN":
                try:
                    if float(entry.timestamp) - float(last_updated_ts[provider]) >= cooldown_period:
                        states[provider] = "HALF-OPEN"
                        last_updated_ts[provider] = entry.timestamp
                except (ValueError, TypeError):
                    pass
        except Exception:
            continue

    return {
        provider: CircuitState(
            provider=provider,
            state=states[provider],
            error_rate=sum(item[0] for item in windows[provider]) / len(windows[provider]) if windows[provider] else 0.0,
        )
        for provider in windows
    }