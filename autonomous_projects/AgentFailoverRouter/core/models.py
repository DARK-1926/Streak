from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CallRecord:
    """Immutable record representing a single toolchain endpoint invocation."""
    target: str
    success: bool
    latency_ms: float
    error_code: str | None
    timestamp: float


@dataclass(frozen=True)
class FailoverPolicy:
    """Configuration policy governing failover thresholds and fallback routing."""
    max_retries: int
    latency_threshold_ms: float
    error_rate_threshold: float
    fallback_target: str
    window_size: int

    def __post_init__(self) -> None:
        """Validate policy thresholds and retry limits upon instantiation."""
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.latency_threshold_ms < 0.0:
            raise ValueError("latency_threshold_ms must be non-negative")
        if self.error_rate_threshold < 0.0:
            raise ValueError("error_rate_threshold must be non-negative")


@dataclass(frozen=True)
class RouterState:
    """Accumulated state tracking call metrics and current routing target."""
    total_calls: int
    total_failures: int
    rolling_latencies: list[float] = field(default_factory=list)
    current_target: str = ""


@dataclass(frozen=True)
class RoutingDecision:
    """Deterministic output representing the router's evaluated routing action."""
    route_to: str
    should_failover: bool
    reason: str
    updated_state: RouterState