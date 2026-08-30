# ContextLeakAuditor

A deterministic, single-pass auditor for agentic toolchain execution logs. Identifies context budget leaks, simulates token trajectories, and recommends compression strategies. Built exclusively with the Python standard library.

## The Agentic Gap

Modern LLM agents operate by chaining tools, injecting system prompts, and appending tool outputs to a rolling context window. Without explicit truncation, deduplication, or budget awareness, these pipelines silently leak context budget. Redundant system prompt injections and unbounded tool outputs cause monotonic context growth, leading to window starvation, increased latency, and eventual reasoning collapse.

ContextLeakAuditor bridges this gap by providing offline, deterministic analysis of JSONL execution traces. It quantifies token waste, identifies leak signatures, and projects budget trajectories under simulated compression strategies, enabling engineers to harden agentic pipelines against context exhaustion.

## Architecture & Design Principles

- **Single-Pass Processing**: Core detectors consume `Iterable[Dict[str, Any]]` exactly once. No `itertools.tee`, no backtracking, no hidden buffering.
- **DI-Driven Design**: All core functions accept iterables and primitive configuration. No global state, no implicit I/O, no framework coupling. Dependencies are injected explicitly at the call site.
- **Stdlib-Only Constraint**: Zero third-party dependencies. Relies exclusively on `json`, `mmap`, `argparse`, `dataclasses`, `typing`, and `sys`.
- **Win32 mmap Safety**: File ingestion uses `mmap.mmap` with `ACCESS_READ` and strict context managers. This avoids exclusive file locks and `[WinError 32] PermissionError` on Windows platforms.
- **Safe List Materialization for Fan-Out**: While individual analyzers are strictly single-pass, the CLI safely materializes the parsed stream into a list once. This enables deterministic fan-out to multiple pure analyzers (leak detector, redundancy scanner, simulator) without re-reading disk or duplicating iterators unsafely.

## How it Works

1. **Ingestion**: `parser.py` streams raw JSONL lines, stripping whitespace and yielding validated dictionaries. Malformed lines are logged to `stderr` and skipped without interrupting the pipeline.
2. **Materialization**: The CLI consumes the generator into a memory-safe list to enable parallel analysis branches. This is the only point of materialization in the pipeline.
3. **Leak Detection**: `core.py` tracks rolling context size across steps. It flags monotonic growth streaks (≥3 consecutive steps) and hard budget overflows. Wasted tokens and severity levels are calculated deterministically.
4. **Redundancy Scanning**: `patterns.py` computes deterministic trigram shingle hashes for `system` and `tool_output` payloads. It tracks repetition counts in a single pass, flagging duplicate injections that bloat context.
5. **Budget Simulation**: `simulator.py` replays the event stream, applying a mock truncation strategy at 80% capacity. It projects peak usage, calculates theoretical token savings, and determines if the trajectory would overflow the budget.
6. **Reporting**: Results are aggregated into a structured JSON report containing leak signatures, redundancy metrics, simulation projections, and actionable compression recommendations.

## Interface Contracts

All public interfaces use strict type hints and dataclasses for predictable composition.

```python
from typing import Iterable, Dict, Any, List
from dataclasses import dataclass

@dataclass
class LeakSignature:
    type: str
    step: int
    severity: str
    tokens_wasted: int

@dataclass
class LeakReport:
    total_events: int
    total_leaks: int
    signatures: List[LeakSignature]
    recommendation: str

def detect_leaks(events: Iterable[Dict[str, Any]], budget_limit: int) -> LeakReport: ...

def compute_text_signature(text: str) -> int: ...

def scan_redundancy(events: Iterable[Dict[str, Any]]) -> List[LeakSignature]: ...

@dataclass
class SimulationResult:
    steps: int
    peak_tokens: int
    projected_savings: int
    would_overflow: bool

def run_budget_simulation(events: Iterable[Dict[str, Any]], cap: int) -> SimulationResult: ...

def parse_log_stream(lines: Iterable[str]) -> Iterable[Dict[str, Any]]: ...
```

## Usage Examples

### CLI Execution

```bash
python cli.py agent_trace.jsonl --budget 4096 --output audit_report.json
```

**Flags:**
- `input_path` (positional): Path to the JSONL log file.
- `--budget` (int, required): Context window token limit for analysis.
- `--output` (str, optional): File path for JSON report. Defaults to stdout.

### Expected JSONL Format

Each line must be a valid JSON object. The auditor recognizes the following keys:

```json
{"step": 1, "context_size": 1200, "system": "You are a helpful assistant..."}
{"step": 2, "tokens": 450, "tool_output": "Query returned 15 rows..."}
{"step": 3, "context_size": 1850}
```

- `step`: Integer step identifier (optional, defaults to line index).
- `context_size` or `tokens`: Integer/float representing token count at that step.
- `system` or `tool_output`: String payloads used for redundancy scanning.

### Example Output Structure

```json
{
  "total_events": 42,
  "total_leaks": 5,
  "signatures": [
    {"type": "monotonic_growth", "step": 12, "severity": "medium", "tokens_wasted": 410}
  ],
  "redundancy_leaks": [
    {"type": "redundant_injection", "step": 8, "severity": "high", "tokens_wasted": 256}
  ],
  "simulation": {
    "steps": 42,
    "peak_tokens": 5120,
    "projected_savings": 1840,
    "would_overflow": true
  },
  "recommendation": "Apply truncation at step 10. Deduplicate system prompt injections."
}
```

## Testing Strategy

The test suite enforces strict purity and determinism:

- **Pure Function Validation**: Core logic is tested via synthetic `Iterable[Dict]` payloads. No filesystem or network access in unit tests.
- **Exact Dataclass Assertions**: Tests verify leak counts, signature types, severity thresholds, and token waste calculations with exact equality checks.
- **CLI Integration**: The command-line interface is tested via `subprocess` to validate exit codes, stderr warnings, and JSON output structure.
- **Zero Mocks, Zero Side-Effects**: Core modules contain no implicit state. Tests rely entirely on in-memory iterables and deterministic inputs.
- **Cross-Platform Safety**: Temporary files in tests explicitly close file descriptors immediately after creation to prevent `[WinError 32]` on Windows.

Run the suite:
```bash
python -m unittest test_main.py -v
```

## Extending Pattern Detectors

The architecture supports modular pattern detection without modifying core pipelines.

1. Create a pure function in `patterns.py` or a new module:
```python
from typing import Iterable, Dict, Any, List
from core import LeakSignature

def scan_custom_pattern(events: Iterable[Dict[str, Any]]) -> List[LeakSignature]:
    """Detect custom context leak signatures in a single pass."""
    signatures: List[LeakSignature] = []
    # Implement single-pass state tracking here
    return signatures
```
2. Ensure the function accepts `Iterable[Dict[str, Any]]` and returns `List[LeakSignature]`.
3. Wire the detector into `_execute_audit` in `cli.py` by calling it on the materialized event list and merging results into the final report dictionary.
4. Maintain the single-pass constraint per detector. Avoid global caches or external I/O.

## Requirements

- Python 3.8+
- No external dependencies (stdlib only)

## License

MIT