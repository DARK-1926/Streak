from typing import Iterable, Dict, Any
from dataclasses import dataclass


@dataclass
class SimulationResult:
    """Deterministic output of a budget simulation run."""
    steps: int
    peak_tokens: int
    projected_savings: int
    would_overflow: bool


def run_budget_simulation(events: Iterable[Dict[str, Any]], cap: int) -> SimulationResult:
    """
    Simulate context window accumulation over an iterable of agent events.
    Applies a mock truncation strategy when the cap is approached and
    calculates theoretical token savings if unbounded leaks were prevented.
    Pure, single-pass, and deterministic.
    """
    if cap <= 0:
        cap = 1

    current_size = 0
    peak_tokens = 0
    steps = 0
    projected_savings = 0
    would_overflow = False
    trunc_threshold = int(cap * 0.8)
    trunc_target = int(cap * 0.5)

    for event in events:
        steps += 1
        raw_val = event.get("context_size", event.get("tokens", 0))
        try:
            added = max(0, int(float(raw_val)))
        except (ValueError, TypeError):
            added = 0

        current_size += added
        if current_size > peak_tokens:
            peak_tokens = current_size

        if current_size > cap:
            would_overflow = True

        if current_size >= trunc_threshold:
            saved = current_size - trunc_target
            projected_savings += saved
            current_size = trunc_target

    return SimulationResult(
        steps=steps,
        peak_tokens=peak_tokens,
        projected_savings=projected_savings,
        would_overflow=would_overflow
    )