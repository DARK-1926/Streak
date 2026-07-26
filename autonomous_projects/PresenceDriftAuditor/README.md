# PresenceDriftAuditor

A stateless, O(N) log auditor that tracks agent presence stability, detects process migrations, and filters connection flapping without relying on sticky sessions.

## Architecture

PresenceDriftAuditor is built on a strict Dependency Injection (DI) architecture to ensure high testability, performance, and separation of concerns:

* **Data Contracts (`models.py`)**: Defines strict, validated data structures (`LogEvent`, `AuditReport`) and a pure JSONL parser that guarantees type safety and schema adherence.
* **State Machine (`engine.py`)**: Operates purely on an `Iterable[LogEvent]`. It contains zero I/O logic, making it entirely decoupled from the data source and trivially testable.
* **I/O Handler (`cli.py`)**: Manages memory-mapped I/O (`mmap`) to stream large log files efficiently. It includes specific guards against win32 empty-file crashes and feeds the parsed stream directly into the engine.

## How it Works

The core of the auditor is an O(N) single-pass state machine that processes log events sequentially:

1. **State Tracking**: For each unique `agent_id`, the engine maintains a lightweight state tracking the last seen timestamp, connection status, and current `process_id`.
2. **Flap Detection**: When an agent reconnects, the engine calculates the time delta since the last disconnect. If this delta is less than or equal to the configured `flap_threshold_sec`, the event is classified as a connection flap rather than a new session.
3. **Migration Detection**: If an agent emits a `CONNECT` event with a `process_id` that differs from the currently tracked `process_id`, the engine registers a process migration.
4. **Stability Scoring**: Upon completion of the stream, the engine calculates a deterministic stability score (0.0 to 1.0) for each agent. This score is derived from total connection duration and heavily penalized by the frequency of connection flaps.

## Usage

Run the auditor against a JSONL log file using the command-line interface. You can optionally specify the flap threshold in seconds (defaults to 5.0).

```bash
python cli.py logs.jsonl --flap-threshold 5.0
```

The output will be a JSON array of `AuditReport` objects printed to standard output.

## Testing

The project includes a comprehensive test suite (`test_main.py`) that validates the parser, the state machine's migration and flapping logic, and the memory-mapped I/O using real temporary files.

Run the tests using pytest:

```bash
pytest test_main.py