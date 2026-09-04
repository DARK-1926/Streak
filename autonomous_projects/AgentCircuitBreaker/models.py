import dataclasses
from typing import Literal, Dict, List, Any


import dataclasses
from typing import Literal, Dict, List, Any


@dataclasses.dataclass(frozen=True)
class LogEntry:
    provider: str
    status_code: int
    latency_ms: float
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class CircuitState:
    provider: str
    state: Literal['CLOSED', 'OPEN', 'HALF-OPEN']
    error_rate: float

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class RoutingDecision:
    task: str
    provider: str
    is_fallback: bool
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class AuditReport:
    circuit_states: Dict[str, CircuitState]
    routing_decision: Any

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the full audit report to a dictionary for JSON encoding.
        
        Returns:
            A nested dictionary representation of the report and its components.
        """
        try:
            return dataclasses.asdict(self)
        except Exception as exc:
            return {
                "breaker_states": {k: v.to_dict() for k, v in self.breaker_states.items()},
                "routing_decisions": [rd.to_dict() for rd in self.routing_decisions],
                "anomalies": list(self.anomalies),
                "serialization_error": str(exc)
            }