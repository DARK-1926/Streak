# ToolSchemaFuzzer

Deterministic stress-testing for agent tool-parser JSON schema contracts.

## Problem Solved

Agent tool-parsers frequently crash or silently corrupt internal state when encountering minor JSON schema deviations. Common failure points include missing required keys, type drift, boundary value overflows, and deeply nested truncations. Developers lack a reliable, deterministic mechanism to stress-test these contracts before deployment. ToolSchemaFuzzer solves this by generating controlled, seeded edge-case variants and safely executing user-defined parsers against them, capturing failures and execution metrics without crashing the host pipeline.

## Architecture & Core Modules

The system is built around four isolated, single-responsibility modules that communicate via strict dataclass contracts and pure functions.

- **`normalizer.py`**: Parses raw JSON schema dictionaries into a flat, validated internal specification. Recursively validates node structure, enforces type constraints, and extracts required field metadata into immutable `NormalizedSchema` and `NormalizedField` objects.
- **`fuzzer.py`**: Generates edge-case payload variants via seeded mutation strategies. Strategies include `omit_required`, `inject_extra`, `type_mismatch`, `boundary_values`, and `deep_truncate`. Uses a localized `random.Random` instance to guarantee deterministic output across runs.
- **`validator.py`**: Provides a safe execution harness that runs user parser callables against fuzz variants. Captures exceptions, execution time, and success states without allowing unhandled errors to bubble up and crash the orchestration layer.
- **`cli.py`**: Orchestrates the pipeline. Handles safe file I/O, dynamic module loading via `importlib`, argument parsing, and structured JSON report generation. Implements strict error handling and Windows-safe file descriptor management.

## Interface Contracts

All public interfaces use strict type hints and return frozen dataclasses to prevent accidental state mutation.

### Normalizer
```python
@dataclass(frozen=True)
class NormalizedField:
    name: str
    expected_type: str
    required: bool
    nested_schema: Optional['NormalizedSchema'] = None

@dataclass(frozen=True)
class NormalizedSchema:
    fields: List[NormalizedField]
    raw: Dict[str, Any]

def normalize_schema(raw_schema: Dict[str, Any]) -> NormalizedSchema: ...
```

### Fuzzer
```python
@dataclass(frozen=True)
class FuzzVariant:
    payload: Dict[str, Any]
    strategy: str
    description: str

def generate_variants(
    schema: NormalizedSchema,
    seed: int = 42,
    max_variants: int = 50
) -> Iterable[FuzzVariant]: ...
```

### Validator
```python
@dataclass(frozen=True)
class ValidationReport:
    variant_strategy: str
    success: bool
    exception_type: Optional[str]
    exception_msg: Optional[str]
    execution_time_ms: float

def validate_variant(
    variant: FuzzVariant,
    parser_fn: Callable[[dict], Any]
) -> ValidationReport: ...
```

### CLI
```python
def run_audit(
    schema_path: str,
    module_path: str,
    func_name: str,
    seed: int = 42,
    output_path: Optional[str] = None
) -> List[ValidationReport]: ...
```

## Dependency Injection & Single-Pass Execution

ToolSchemaFuzzer avoids global state and implicit coupling. Components are wired explicitly via function arguments (Dependency Injection). The fuzzer yields variants lazily via Python generators. The validator consumes these generators in a single pass, ensuring memory efficiency and deterministic ordering. No intermediate lists are held in memory unless explicitly requested by the test harness. This architecture guarantees predictable execution flows and simplifies unit testing without requiring mocking frameworks.

## How it Works

1. **Schema Ingestion & Normalization**: The CLI reads a raw JSON schema file and passes it to `normalize_schema()`. The normalizer recursively validates structural integrity, extracts properties, maps required keys, and returns an immutable `NormalizedSchema`.
2. **Seeded RNG Initialization**: A `random.Random(seed)` instance is created. This isolates the fuzzing randomness from the global Python RNG, ensuring that identical seeds always produce identical mutation sequences.
3. **Lazy Variant Generation**: `generate_variants()` constructs a minimally valid base payload, then applies mutation strategies sequentially. Each mutation yields a `FuzzVariant` immediately. Generators ensure that payloads are created on-demand rather than pre-allocated.
4. **Safe Validation Harness**: Each variant is passed to `validate_variant()` alongside the user-provided parser callable. The harness wraps execution in a strict `try/except` block, catching all standard exceptions while allowing `SystemExit` and `KeyboardInterrupt` to propagate. Execution time is measured via `time.perf_counter()`.
5. **Report Aggregation & Output**: Validation results are collected into `ValidationReport` dataclasses. The CLI serializes these reports into a structured JSON array and writes them to disk or stdout. All file operations use context managers and explicit descriptor closure to guarantee cross-platform safety.

## CLI Usage

Run the audit pipeline against a target schema and parser module:

```bash
python cli.py --schema schema.json --parser-module my_parser.py --parser-func parse_tool_output
```

**Arguments:**
- `--schema`: Path to the JSON schema file.
- `--parser-module`: Path to the Python module containing the parser function.
- `--parser-func`: Name of the callable to test.
- `--seed`: Integer seed for deterministic fuzzing (default: 42).
- `--output`: Optional path to write the JSON report. Defaults to stdout.

**Example Output Structure:**
```json
[
  {
    "variant_strategy": "omit_required",
    "success": false,
    "exception_type": "KeyError",
    "exception_msg": "'username'",
    "execution_time_ms": 0.142
  },
  {
    "variant_strategy": "type_mismatch",
    "success": false,
    "exception_type": "TypeError",
    "exception_msg": "expected str, got int",
    "execution_time_ms": 0.089
  }
]
```

## Testing Strategy

Execute the integrated test suite:

```bash
python test_main.py
```

The test suite follows a strict, mock-free methodology:
- **Real Dummy Parser**: `dummy_agent_parser()` is a genuine callable that deterministically raises exceptions based on payload markers. No `unittest.mock` or patching is used.
- **Deterministic Assertions**: Generator outputs are consumed into lists for exact count verification. Strategy names, exception types, and report counts are asserted explicitly.
- **Single-Pass Verification**: Tests validate that the pipeline executes exactly once per variant, confirming lazy evaluation and DI wiring.
- **Isolated Execution**: Each test function is self-contained, importing actual modules and verifying contract compliance without external test runners.

## Key Highlights

- **Zero Dependencies**: Built entirely on the Python standard library. No third-party packages required.
- **Deterministic Seeding**: All randomness is scoped to a `random.Random` instance initialized with a user-provided seed. Identical inputs always yield identical fuzz sequences.
- **Safe Generator Consumption**: Variants are yielded lazily and consumed in a single pass, preventing memory bloat and ensuring predictable iteration order.
- **Strict Dataclass Outputs**: All contracts use `@dataclass(frozen=True)` to guarantee immutability and prevent accidental state corruption during pipeline execution.
- **Win32 Safety**: File descriptors returned by low-level OS calls are explicitly closed immediately after use. All I/O operations use context managers to prevent `[WinError 32] PermissionError` on Windows environments.
- **Graceful Exception Handling**: The validation harness isolates parser crashes, capturing stack traces and error messages without terminating the audit process.

## Requirements

- Python 3.8+
- No external packages

## License

MIT License. See LICENSE for details.