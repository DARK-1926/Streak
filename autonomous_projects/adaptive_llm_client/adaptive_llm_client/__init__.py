"""adaptive_llm_client package

Provides:
- `EffortLevel` enum defining supported effort tiers.
- `AdaptiveLLM` class exposing `think(effort, prompt)`.
- Simple in‑memory cache to deduplicate identical calls.
"""

from .core import AdaptiveLLM, EffortLevel
