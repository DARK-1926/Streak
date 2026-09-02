from dataclasses import dataclass
from typing import List
import collections


@dataclass(frozen=True)
class TraceEntry:
    """Represents a single step in an agent inference trace log.

    Attributes:
        id: Unique identifier for the trace step.
        content: The textual content of the reasoning step.
        tokens: The token count for this step. Must be non-negative.
    """
    id: int
    content: str
    tokens: int

    def __post_init__(self) -> None:
        """Validate field constraints upon instantiation."""
        if self.tokens < 0:
            raise ValueError("tokens must be a non-negative integer.")


@dataclass(frozen=True)
class BloatSegment:
    """Represents a detected span of repetitive or circular reasoning steps.

    Attributes:
        start_index: The starting index of the bloat segment in the trace. Must be non-negative.
        end_index: The ending index of the bloat segment in the trace. Must be non-negative.
        score: A float indicating the degree of repetition detected.
    """
    start_index: int
    end_index: int
    score: float

    def __post_init__(self) -> None:
        """Validate field constraints upon instantiation."""
        if self.start_index < 0:
            raise ValueError("start_index must be a non-negative integer.")
        if self.end_index < 0:
            raise ValueError("end_index must be a non-negative integer.")
        if self.start_index > self.end_index:
            raise ValueError("start_index must be less than or equal to end_index.")
        if not (0.0 <= self.score <= 1.0):
            raise ValueError("score must be a float between 0.0 and 1.0.")


@dataclass(frozen=True)
class CompressionReport:
    """Summarizes the results and metrics of a trace compression operation.

    Attributes:
        original_tokens: Total token count before compression. Must be non-negative.
        saved_tokens: Total tokens removed during compression. Must be non-negative.
        segments_pruned: Number of bloat segments collapsed. Must be non-negative.
        pruned_entries: List of resulting TraceEntry objects after compression.
    """
    original_tokens: int
    saved_tokens: int
    segments_pruned: int
    pruned_entries: List[TraceEntry]

    def __post_init__(self) -> None:
        """Validate field constraints upon instantiation."""
        if self.original_tokens < 0:
            raise ValueError("original_tokens must be a non-negative integer.")
        if self.saved_tokens < 0:
            raise ValueError("saved_tokens must be a non-negative integer.")
        if self.saved_tokens > self.original_tokens:
            raise ValueError("saved_tokens cannot exceed original_tokens.")
        if self.segments_pruned < 0:
            raise ValueError("segments_pruned must be a non-negative integer.")
        if not isinstance(self.pruned_entries, list):
            raise ValueError("pruned_entries must be a list.")
        for entry in self.pruned_entries:
            if not isinstance(entry, TraceEntry):
                raise ValueError("All items in pruned_entries must be TraceEntry instances.")