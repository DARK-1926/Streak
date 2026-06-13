# Adaptive LLM Client 🚀

## Overview
`adaptive_llm_client` is a tiny, **zero‑dependency** (except `requests`) Python library that gives you a high‑level *thinking effort* API on top of any OpenAI‑compatible chat model.

| Effort | Model (default) | Temperature | Max Tokens | Typical Use‑case |
|--------|-----------------|-------------|------------|-----------------|
| **low**   | `gpt-3.5-turbo`   | 0.7         | 150        | Quick answers, cheap ops |
| **medium**| `gpt-3.5-turbo`   | 0.6         | 300        | Balanced depth & cost |
| **high**  | `gpt-4`           | 0.5         | 500        | In‑depth reasoning |
| **xhigh** | `gpt-4-32k`       | 0.4         | 1500       | Research‑grade analysis |

The library automatically selects the appropriate model and parameters, caches identical calls, and exposes a **single method**:

```python
from adaptive_llm_client import AdaptiveLLM, EffortLevel

client = AdaptiveLLM()
answer = client.think(EffortLevel.HIGH, "Explain recursion in one paragraph.")
print(answer)
```

## Why this solves a real‑world problem
- **Predictable cost & latency** – map business‑level SLAs ("fast", "thorough") to concrete API settings.
- **No model‑hopping headaches** – change effort mid‑conversation without rewriting code.
- **Cache‑driven efficiency** – identical prompts hit an in‑memory store, saving dollars.
- **Easy integration** – works with any OpenAI‑compatible endpoint (Azure, self‑hosted).

## Architecture Diagram
```
+-------------------+          +---------------------------+
|   Application    |  uses    |   AdaptiveLLM (client)    |
+-------------------+          +---------------------------+
          |                                 |
          | think(effort, prompt)           |
          v                                 v
+-------------------+          +---------------------------+
|   Effort Mapper   |<--------|   In‑Memory Cache (dict)  |
+-------------------+          +---------------------------+
          |                                 |
          | config → request payload        |
          v                                 v
+-------------------+          +---------------------------+
|   HTTP Transport  |--------->|   OpenAI / compatible API |
+-------------------+          +---------------------------+
```

## Installation & Quick Start (Windows)
```bat
# From the repository root
setup_and_test.bat
```
The batch script will:
1. Create a virtual environment (`venv`).
2. Install `requests` and `pytest`.
3. Run the unit test suite – you should see **4 passed**.
4. Leave you inside the activated venv ready to import the package.

## Development
- **Tests** live in `tests/` and use `pytest`.
- To add a new effort level, edit `_EFFORT_CONFIG` in `adaptive_llm_client/core.py`.
- The cache implementation is deliberately simple; for production you can swap it for Redis or memcached by subclassing `AdaptiveLLM`.

## License
MIT – feel free to copy, modify, and ship it in commercial products.
