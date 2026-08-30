# ToolchainContractAuditor

## Overview
Deterministic, pre-flight I/O contract validator for agentic toolchains. Bridges the critical gap between LLM-generated tool sequences and reliable execution by catching schema mismatches, type drift, missing tools, and circular dependencies before runtime. Designed for zero side-effects and strict predictability in automated agent pipelines.

## Architecture
- **Pure Functional Core:** All validation logic operates on immutable data structures. Functions like `check_type_drift` and `validate_io_compatibility` are stateless and deterministic.
- **Dependency Injection:** The CLI layer handles all I/O and wiring. Core modules (`contracts`, `parser`, `simulator`) accept explicit arguments and return structured data, enabling seamless testing and embedding.
- **Single-Pass Simulation:** `audit_toolchain` traverses chain links exactly once, maintaining O(n) complexity for cycle detection, missing tool resolution, and I/O validation.
- **Win32 Safety:** Explicit `path.stat().st_size == 0` guards and safe read patterns prevent `mmap`/permission crashes on Windows environments when handling empty or locked files.

## How it Works
1. **Parse:** Streams JSONL/JSON lines via `parse_contracts` and `parse_chain_links`. Malformed lines are skipped without halting execution.
2. **Registry Build:** Maps validated tool names to `ToolContract` dataclasses. Type strings are normalized to canonical Python types (`str`, `int`, `float`, `bool`, `list`, `dict`, `none`).
3. **Simulate:** Walks the execution chain linearly. Tracks visited nodes to detect circular dependencies and flags any tool referenced in the chain but absent from the registry.
4. **Validate:** For each valid link, compares the source tool's `output_schema` against the target tool's `input_schema`. Flags missing keys and type drift using strict normalization rules.
5. **Report:** Aggregates findings into an `AuditReport` dataclass and serializes it to JSON for stdout consumption by orchestrators or CI pipelines.

## Interface Contracts
| File | Responsibility |
|------|----------------|
| `contracts.py` | Type normalization, drift detection, I/O compatibility checks, registry building. |
| `parser.py` | Stateless, single-pass JSON/JSONL parsing for contracts and chain links. |
| `simulator.py` | Execution flow simulation, cycle detection, and `AuditReport` generation. |
| `cli.py` | Argument parsing, safe file I/O, dependency wiring, and JSON stdout output. |
| `test_main.py` | Comprehensive unit and integration tests using in-memory fixtures. |

## Usage

### CLI Flags
```bash
python cli.py --contracts <path_to_contracts.jsonl> --chain <path_to_chain.txt>
```

### Example Contract Format (JSONL)
```json
{"name": "fetch_data", "input_schema": {"url": "str"}, "output_schema": {"raw": "str", "status": "int"}}
{"name": "parse_json", "input_schema": {"raw": "str"}, "output_schema": {"data": "dict"}}
{"name": "summarize", "input_schema": {"data": "dict", "max_len": "int"}, "output_schema": {"summary": "str"}}
```

### Example Chain Format
Supports plain text arrows or JSON objects:
```text
fetch_data->parse_json
{"from": "parse_json", "to": "summarize"}
```

### Output
Returns exit code `0` on valid chains, `1` on failures. Outputs a structured JSON report to stdout:
```json
{
  "valid": false,
  "mismatches": [{"source": "parse_json", "target": "summarize", "error": "Missing key: 'max_len' required by target but not provided by source."}],
  "circular_deps": [],
  "missing_tools": []
}
```

## Testing Strategy
- **TDD & Zero Mocks:** Tests import actual modules and exercise pure functions using in-memory lists and dictionaries. No external state or mocking frameworks are used.
- **Exact Assertions:** Unit tests verify precise mismatch counts, drift flags, and circular dependency detection paths.
- **CLI Integration:** Tested via `subprocess` to validate exit codes, stdout JSON structure, and file I/O error handling under real execution conditions.
- **Run Tests:** `python -m unittest test_main.py -v`

## Lessons Learned
- **Avoided `itertools.tee`:** Hidden memory buffering in tee iterators breaks deterministic single-pass guarantees. Strict linear iteration enforces predictable memory usage.
- **Win32 `mmap` Guards:** Reading empty files on Windows can trigger permission/mmap crashes. Pre-checking `st_size == 0` bypasses the issue entirely.
- **Strict Error Handling:** Silent failures in agent pipelines cause cascading hallucinations. Malformed JSON is explicitly skipped, while structural contract violations produce precise, actionable error paths.
- **Type Alias Normalization:** LLMs frequently output inconsistent type names (`string` vs `str`, `integer` vs `int`). Canonical normalization prevents false-positive drift detection.