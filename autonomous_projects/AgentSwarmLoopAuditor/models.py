"""
Data models for AgentSwarmLoopAuditor.

Defines strict data structures for agent actions and loop detection reports
using Python's standard library dataclasses.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentAction:
    """
    Represents a single action taken by an autonomous agent.
    
    Attributes:
        session_id: Unique identifier for the agent's session.
        tool_name: The name or identifier of the tool invoked.
        args_hash: A deterministic hash of the arguments passed to the tool.
        tokens_used: The number of tokens consumed by this action.
    """
    session_id: str
    tool_name: str
    args_hash: str
    tokens_used: int

    def __post_init__(self) -> None:
        """Validate field types and constraints for AgentAction."""
        if not isinstance(self.session_id, str) or not self.session_id:
            raise ValueError("session_id must be a non-empty string")
        if not isinstance(self.tool_name, str) or not self.tool_name:
            raise ValueError("tool_name must be a non-empty string")
        if not isinstance(self.args_hash, str) or not self.args_hash:
            raise ValueError("args_hash must be a non-empty string")
        if not isinstance(self.tokens_used, int) or isinstance(self.tokens_used, bool):
            raise TypeError("tokens_used must be an integer")
        if self.tokens_used < 0:
            raise ValueError(f"tokens_used must be non-negative, got {self.tokens_used}")


@dataclass(frozen=False)
class LoopReport:
    """
    Represents a detected degenerate behavioral loop in an agent session.

    Attributes:
        exact_loops: The number of exact loops detected.
        alternating_loops: The number of alternating (thrashing) loops detected.
        wasted_tokens: The estimated number of tokens wasted due to all loops.
    """
    exact_loops: int
    alternating_loops: int
    wasted_tokens: int
    session_id: str
    loop_type: str
    count: int

    def __post_init__(self) -> None:
        """Validate field types and constraints for LoopReport."""
        if not isinstance(self.session_id, str) or not self.session_id:
            raise ValueError("session_id must be a non-empty string")
        if not isinstance(self.loop_type, str) or not self.loop_type:
            raise ValueError("loop_type must be a non-empty string")
        if not isinstance(self.count, int) or isinstance(self.count, bool):
            raise TypeError("count must be an integer")
        if self.count < 0:
            raise ValueError(f"count must be non-negative, got {self.count}")
        if not isinstance(self.wasted_tokens, int) or isinstance(self.wasted_tokens, bool):
            raise TypeError("wasted_tokens must be an integer")
        if self.wasted_tokens < 0:
            raise ValueError(f"wasted_tokens must be non-negative, got {self.wasted_tokens}")