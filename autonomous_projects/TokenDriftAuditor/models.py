from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LogEvent:
    """Represents a single LLM interaction log entry."""
    session_id: str
    prompt_tokens: int
    completion_tokens: int
    prompt_text: str
    status: str
    timestamp: float


@dataclass
class InefficiencyPattern:
    """Captures detected inefficiencies like retries or duplication."""
    pattern_type: str
    session_id: str
    count: int
    details: str


@dataclass
class AuditReport:
    """Aggregated audit results with cost drift and inefficiency metrics."""
    total_sessions: int
    total_tokens: int
    estimated_cost: float
    inefficiencies: List[InefficiencyPattern]
    drift_score: float

    def to_dict(self) -> dict:
        """Recursively convert the report and nested patterns to a dict."""
        return {
            "total_sessions": self.total_sessions,
            "total_tokens": self.total_tokens,
            "estimated_cost": self.estimated_cost,
            "inefficiencies": [{"pattern_type": p.pattern_type, "session_id": p.session_id, "count": p.count, "details": p.details} for p in self.inefficiencies],
            "drift_score": self.drift_score,
        }