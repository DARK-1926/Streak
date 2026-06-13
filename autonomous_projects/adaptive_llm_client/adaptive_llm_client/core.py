import os
import hashlib
import json
from enum import Enum
from typing import Any, Dict, Tuple

import requests

# ---------------------------------------------------------------------------
# Configuration – you can override via environment variables
# ---------------------------------------------------------------------------
DEFAULT_API_BASE = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
DEFAULT_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ---------------------------------------------------------------------------
# Effort mapping – maps a high‑level effort to concrete model parameters
# ---------------------------------------------------------------------------
class EffortLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    XHIGH = "xhigh"

# The mapping can be extended; for now we target OpenAI's gpt‑3.5‑turbo and gpt‑4
_EFFORT_CONFIG: Dict[EffortLevel, Dict[str, Any]] = {
    EffortLevel.LOW: {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 150,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "cost_factor": 1,  # internal weighting for cost‑aware selection
    },
    EffortLevel.MEDIUM: {
        "model": "gpt-3.5-turbo",
        "temperature": 0.6,
        "max_tokens": 300,
        "top_p": 0.95,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "cost_factor": 1,
    },
    EffortLevel.HIGH: {
        "model": "gpt-4",
        "temperature": 0.5,
        "max_tokens": 500,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "cost_factor": 2,
    },
    EffortLevel.XHIGH: {
        "model": "gpt-4-32k",
        "temperature": 0.4,
        "max_tokens": 1500,
        "top_p": 0.85,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "cost_factor": 4,
    },
}


class AdaptiveLLM:
    """A thin wrapper around an LLM API that exposes effort‑based calling.

    Example
    -------
    >>> client = AdaptiveLLM()
    >>> answer = client.think(EffortLevel.HIGH, "Explain quantum tunnelling in 2 sentences.")
    """

    def __init__(self, api_key: str = DEFAULT_API_KEY, api_base: str = DEFAULT_API_BASE):
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set or passed explicitly.")
        self.api_key = api_key
        self.api_base = api_base.rstrip('/')
        self._cache: Dict[str, str] = {}

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def think(self, effort: EffortLevel, prompt: str) -> str:
        """Return a completion for *prompt* using the configuration for *effort*.

        The call is cached based on a hash of (effort, prompt).  Subsequent calls
        with identical inputs return the cached result instantly.
        """
        cfg = _EFFORT_CONFIG[effort]
        cache_key = self._make_cache_key(effort, prompt)
        if cache_key in self._cache:
            return self._cache[cache_key]

        payload = {
            "model": cfg["model"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": cfg["temperature"],
            "max_tokens": cfg["max_tokens"],
            "top_p": cfg["top_p"],
            "frequency_penalty": cfg["frequency_penalty"],
            "presence_penalty": cfg["presence_penalty"],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        response = requests.post(f"{self.api_base}/chat/completions", json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        text = data["choices"][0]["message"]["content"].strip()
        self._cache[cache_key] = text
        return text

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    @staticmethod
    def _make_cache_key(effort: EffortLevel, prompt: str) -> str:
        h = hashlib.sha256()
        h.update(effort.value.encode("utf-8"))
        h.update(b"|")
        h.update(prompt.encode("utf-8"))
        return h.hexdigest()

    # Expose the raw config for advanced users (read‑only)
    @property
    def effort_config(self) -> Dict[EffortLevel, Dict[str, Any]]:
        return json.loads(json.dumps(_EFFORT_CONFIG))  # deep copy
