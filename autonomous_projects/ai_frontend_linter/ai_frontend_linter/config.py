import enum
from dataclasses import dataclass
from pathlib import Path

class ThinkingLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    XHIGH = "xhigh"

@dataclass
class LinterConfig:
    """Configuration for the linter.

    Attributes
    ----------
    max_file_size_kb: int
        Files larger than this are skipped (to avoid huge LLM costs).
    thinking_level: ThinkingLevel
        Controls how many LLM passes are performed per issue.
    openai_api_key: str | None
        If None, the LLM step is disabled (pure static analysis).
    """

    max_file_size_kb: int = 200
    thinking_level: ThinkingLevel = ThinkingLevel.MEDIUM
    openai_api_key: str | None = None
    # Internal mapping of level -> number of LLM tokens to request
    _level_token_budget = {
        ThinkingLevel.LOW: 256,
        ThinkingLevel.MEDIUM: 512,
        ThinkingLevel.HIGH: 1024,
        ThinkingLevel.XHIGH: 2048,
    }

    @property
    def token_budget(self) -> int:
        return self._level_token_budget[self.thinking_level]

    @classmethod
    def from_env(cls) -> "LinterConfig":
        import os
        level = os.getenv("AI_LINTER_THINKING_LEVEL", "medium").lower()
        return cls(
            max_file_size_kb=int(os.getenv("AI_LINTER_MAX_FILE_KB", "200")),
            thinking_level=ThinkingLevel(level),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )
