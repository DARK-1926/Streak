# AgentCircuitBreaker

Deterministic Resilience Auditing for Agentic Workflows

## The Agentic Gap

Modern agentic AI systems orchestrate complex workflows across multiple external LLM providers. When these providers degrade, rate-limit, or fail simultaneously, agents typically crash, enter infinite retry loops, or route requests blindly. This vulnerability is known as the **Agentic Gap**: a critical lack of local, deterministic resilience auditing at the orchestration layer.

Traditional circuit breakers are often network-bound, framework-heavy, or reliant on external state stores. They introduce latency, complicate deployment, and fail to provide auditable, reproducible routing decisions. AgentCircuitBreaker closes this gap by providing a lightweight, purely functional audit engine that evaluates provider health and simulates fallback routing deterministically, without external dependencies or runtime side effects.

## Solution & Vision

AgentCircuitBreaker ingests telemetry logs, evaluates provider health via a sliding-window circuit breaker state machine, and outputs structured routing decisions based on configurable priority policies. The entire pipeline is designed for local execution, auditability, and strict determinism.

**Core Vision:**
- Eliminate blind retries and cascading failures in agentic orchestrators.
- Provide reproducible, auditable routing decisions from raw telemetry.
- Maintain zero external dependencies and cross-platform compatibility.
- Enforce strict type safety, immutability, and single-pass execution.

## Architecture & Spec-Driven Development

This project is built using a strict Spec-Driven Development methodology. Every component adheres to explicit interface contracts, pure function boundaries, and immutable data structures.

- **Pure Functions & Immutability:** Core logic (`parser`, `breaker`, `router`) consists exclusively of pure functions. State is never mutated in place; instead, new dataclass instances are yielded or returned.
- **Explicit Dependency Injection:** The CLI layer (`cli.py`) acts as the composition root. It handles I/O, argument parsing, and explicitly wires pure functions together. No global state or implicit singletons.
- **Single-Pass Execution:** Both log parsing and circuit state evaluation operate in O(n) time complexity. Streams are consumed exactly once, minimizing memory footprint and enabling processing of arbitrarily large telemetry files.
- **Win32-Safe File Guards:** All file operations, including temporary file creation in tests, strictly manage file descriptors. Descriptors from `tempfile.mkstemp()` are immediately closed via `os.close(fd)` to prevent `[WinError 32] PermissionError` on Windows systems.
- **Zero-Mock Testing:** The test suite validates behavior using real in-memory data structures and direct assertions against dataclass fields. CLI integration is validated via `subprocess` calls against actual temporary files. No mocking frameworks are used.

## How it Works

The audit pipeline executes in four deterministic stages:

1. **Ingestion & Parsing (`parser.py`)**
   Streams raw JSON-lines from a log file. Each line is decoded, validated against strict type expectations, and mapped to a `LogEntry` dataclass. Malformed lines, missing keys, or invalid timestamps are gracefully skipped to ensure stream continuity.

2. **State Evaluation (`breaker.py`)**
   Processes parsed entries in a single pass. Maintains a sliding window of request outcomes per provider. Calculates real-time error rates and transitions circuit states deterministically:
   - `CLOSED`: Normal operation. Error rate below threshold.
   - `OPEN`: Error rate exceeds threshold. Provider is considered degraded.
   - `HALF-OPEN`: Cooldown period elapsed. Provider is eligible for probing.

3. **Routing Simulation (`router.py`)**
   Consumes the final circuit states and a user-defined priority policy. For each task, it iterates through the prioritized provider list and selects the first provider with a `CLOSED` or `HALF-OPEN` state. If all providers are `OPEN`, it forces a fallback to the last provider in the list, ensuring deterministic task assignment.

4. **Orchestration & Output (`cli.py`)**
   Wires the pipeline, validates inputs, and executes the audit. Outputs a structured JSON `AuditReport` containing final circuit states and routing decisions. Exit codes strictly reflect execution success or failure.

## Interface Contracts

All public interfaces are strictly typed and documented. Core data models are immutable `frozen=True` dataclasses.

### Data Models (`models.py`)
- `LogEntry(provider: str, status_code: int, latency_ms: float, timestamp: str)`
- `CircuitState(state: Literal['CLOSED', 'OPEN', 'HALF-OPEN'], error_rate: float, last_updated: str)`
- `RoutingDecision(task: str, provider: str, reason: str)`
- `AuditReport(circuit_states: Dict[str, CircuitState], routing_decisions: List[RoutingDecision])`

### Core Functions
- `parse_log_stream(lines: Iterable[str]) -> Iterator[LogEntry]`
- `evaluate_circuit_states(entries: Iterable[LogEntry], window_size: int = 50, error_threshold: float = 0.4, cooldown_entries: int = 10) -> Dict[str, CircuitState]`
- `simulate_fallback_routing(states: Dict[str, CircuitState], policy: Dict[str, List[str]]) -> List[RoutingDecision]`
- `run_audit(file_path: str, policy_json_str: str) -> AuditReport`

## Usage

### CLI Execution

Run the audit pipeline against a JSON-lines log file and a routing policy:

```bash
python cli.py --log-file telemetry.jsonl --policy-json '{"summarization": ["openai", "anthropic", "cohere"], "code_generation": ["anthropic", "openai"]}'
```

Or pass a policy file via shell substitution:

```bash
python cli.py --log-file telemetry.jsonl --policy-json "$(cat policy.json)"
```

### Expected Output

The CLI prints a JSON-encoded `AuditReport` to stdout:

```json
{
  "circuit_states": {
    "openai": {"state": "OPEN", "error_rate": 0.65, "last_updated": "2024-01-15T10:30:00Z"},
    "anthropic": {"state": "CLOSED", "error_rate": 0.05, "last_updated": "2024-01-15T10:30:05Z"}
  },
  "routing_decisions": [
    {"task": "code_generation", "provider": "anthropic", "reason": "AVAILABLE"},
    {"task": "summarization", "provider": "anthropic", "reason": "AVAILABLE"}
  ]
}
```

### Exit Codes
- `0`: Audit completed successfully.
- `1`: Runtime error (missing file, empty log, malformed policy JSON, or pipeline failure).

## Testing Strategy

The test suite enforces 100% coverage of core logic paths using a strict, mock-free methodology.

- **Pure Function Validation:** Tests construct real `LogEntry` and `CircuitState` instances in memory, pass them to core functions, and assert exact field values on returned dataclasses.
- **State Transition Verification:** Breaker tests generate controlled sequences of success/failure entries to verify exact threshold crossings and cooldown transitions.
- **CLI Integration:** Uses `subprocess.run()` to execute `cli.py` against real temporary files. Validates stdout JSON structure, stderr messages, and process exit codes.
- **Win32 Safety:** Temporary files are created using `tempfile.mkstemp()`. The file descriptor is immediately closed with `os.close(fd)` before writing, ensuring safe deletion on Windows without permission locks.

### Running Tests

Execute the full suite using the standard library unittest runner:

```bash
python -m unittest test_main.py -v
```

No external test runners, fixtures, or mocking libraries are required.

## Design Principles

- **Stdlib-Only:** Zero third-party dependencies. Runs anywhere Python 3.8+ is available.
- **Cross-Platform:** Explicitly handles path separators, encoding (`utf-8`), and Windows file locking semantics.
- **Deterministic Validation:** Given identical logs and policies, the output is byte-for-byte identical. No randomness, no network calls, no hidden state.
- **Type Safety:** Comprehensive type hints across all signatures. Static analysis ready.
- **Graceful Degradation:** Malformed telemetry never crashes the pipeline. Invalid lines are skipped; missing providers default to `CLOSED` state; exhausted fallbacks trigger forced routing with explicit reason codes.
- **Production-Ready:** Functions are kept under 50 lines, exceptions are explicitly caught and contextualized, and all public APIs include comprehensive docstrings following PEP 257.

## Requirements

- Python 3.8+
- Standard Library Only (`dataclasses`, `typing`, `json`, `re`, `collections`, `argparse`, `os`, `sys`, `tempfile`, `subprocess`, `unittest`)

## License

MIT License. See LICENSE for details.