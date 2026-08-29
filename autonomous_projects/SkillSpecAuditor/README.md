# SkillSpecAuditor

A lightweight, repo-local manifest compiler and validator for deterministic agent toolchaining.

## The Agentic Gap Solved

Modern AI agents struggle with fragmented tool descriptions, unpredictable I/O chaining, and heavy runtime dependencies. Protocols like MCP (Model Context Protocol) attempt to standardize tool communication but introduce complex server architectures, network overhead, and external service dependencies. SkillSpecAuditor bridges this gap by providing a zero-dependency, file-local manifest system. It enforces strict schema validation, deterministic stdout-to-stdin routing, and safe execution, enabling reliable, reproducible agent toolchains without external services, network calls, or runtime ambiguity.

## Architecture Overview

SkillSpecAuditor is built around four isolated, pure-Python modules that communicate via strict data contracts. The architecture separates pure logic from side-effects, ensuring testability, safety, and deterministic behavior.

### Core Modules & Interface Contracts

- **`skill_spec.py`**  
  Pure data models and parsing/validation logic. Handles JSON manifest ingestion, schema enforcement, and contract verification. Contains zero file I/O and zero network calls.  
  **Contract:**  
  `parse_manifest(raw_json: str) -> List[SkillDef]`  
  `validate_contract(skill: SkillDef) -> bool`  
  Guarantees immutable `SkillDef` objects and raises `ValueError` on schema violations or missing required fields.

- **`router.py`**  
  Deterministic I/O chain resolution and compatibility verification. Matches `stdout_expect` to `stdin_expect` with strict manifest-order tie-breaking and cycle detection. Pure logic with zero side-effects.  
  **Contract:**  
  `resolve_chain(skills: List[SkillDef], entrypoint: str) -> List[SkillDef]`  
  `verify_chain_compatibility(chain: List[SkillDef]) -> bool`  
  Guarantees acyclic, I/O-compatible chains or raises `ValueError` on missing entrypoints, broken links, or cycles.

- **`executor.py`**  
  Dependency-injected execution engine. Runs skills safely, captures I/O, and validates exit codes against allowed lists. Isolates all subprocess side-effects behind an injected runner callable.  
  **Contract:**  
  `execute_skill(skill: SkillDef, payload: str, runner: Callable[[List[str], str], Tuple[int, str, str]]) -> ExecutionResult`  
  `subprocess_runner(cmd: List[str], payload: str) -> Tuple[int, str, str]`  
  Guarantees safe execution, strict exit code validation, and structured `ExecutionResult` objects.

- **`cli.py`**  
  Orchestrator and entry point. Handles safe file I/O, stdin payload ingestion, argument parsing, and structured JSON reporting. Wires the pure modules together for production use.  
  **Contract:**  
  `main() -> None`  
  `_parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace`  
  `_load_manifest(path: str) -> str`  
  `_validate_skills(skills: List[SkillDef]) -> None`  
  `_format_dry_run(chain: List[SkillDef]) -> dict`  
  `_execute_chain(chain: List[SkillDef], initial_payload: str, runner: Callable) -> List[ExecutionResult]`  
  `_print_report(report: dict) -> None`  
  Guarantees safe file handling, stdin consumption, and machine-readable JSON stdout.

## How it Works

1. **Manifest Ingestion:** The CLI reads a local JSON manifest containing skill definitions. Each skill declares its executable command, expected stdin format, expected stdout format, and allowed POSIX exit codes.
2. **Schema & Contract Validation:** `skill_spec.py` parses the raw JSON into immutable `SkillDef` objects. It enforces required fields, validates types, and verifies that I/O contracts are logically sound before any execution planning occurs.
3. **Deterministic Chain Routing:** Given an `--entrypoint`, `router.py` traverses the skill list. It matches the current skill's `stdout_expect` to the next skill's `stdin_expect`. If multiple skills match, it selects the first one in manifest order (deterministic tie-breaking). It halts gracefully on terminal nodes (`None` stdout) or raises immediately on cycles.
4. **Safe Execution:** The resolved chain is passed to `executor.py`. Each skill runs sequentially. The stdout of step N becomes the stdin payload for step N+1. Exit codes are strictly checked against the skill's `allowed_exit_codes`. Any failure halts the chain immediately with a structured error report.
5. **Structured Reporting:** The CLI outputs a machine-readable JSON report detailing the chain plan, execution results, intermediate payloads, and final status. This enables seamless integration with higher-level agent orchestrators and CI/CD pipelines.

## Dependency Injection & Mock-Free Testing

SkillSpecAuditor avoids traditional mocking frameworks by using explicit Dependency Injection. The `execute_skill` function accepts a `runner` callable with the signature `Callable[[List[str], str], Tuple[int, str, str]]`. 

In production, `subprocess_runner` is injected to handle actual process execution. In tests, pure Python functions like `fake_runner` or `failing_runner` are injected. This eliminates mock patching, guarantees deterministic in-memory test execution, and ensures zero file/network side-effects during validation. The entire test suite runs isolated, validating parsing, contract matching, chain routing, CLI wiring, and full chain execution deterministically.

## Usage Examples

Plan a chain without executing (dry-run):
```
python cli.py --manifest skills.json --entrypoint fetch_data --dry-run
```

Execute a chain with a piped stdin payload:
```
echo '{"id":1}' | python cli.py --manifest skills.json --entrypoint fetch_data
```

The CLI will output a structured JSON report to stdout containing the execution plan, step-by-step results, captured I/O, and final chain status.

## Running Tests

Execute the pure unit test suite:
```
python test_main.py
```

All tests import actual modules and use injected runners. They validate parsing, contract matching, chain routing, CLI dry-run wiring, and full chain execution deterministically. The suite runs entirely in-memory with zero file or network side-effects.

## Key Features

- **Zero Dependencies:** Built entirely on the Python standard library. No `pip install` required. Runs anywhere Python 3.8+ is available.
- **Win32 Safety:** Strict file descriptor handling, safe subprocess management, and explicit resource cleanup prevent `[WinError 32] PermissionError` and handle Windows-specific execution quirks gracefully.
- **Deterministic Routing:** Manifest-order tie-breaking and explicit cycle detection guarantee reproducible chain resolution across all environments and runs.
- **Spec-Driven Validation:** Strict JSON schema enforcement and I/O contract verification catch configuration errors before runtime, reducing agent hallucination and toolchain failures.
- **Structured JSON Reporting:** Machine-readable output designed for programmatic consumption by agent frameworks, CI systems, and audit logs.
- **Pure Core Logic:** All routing, parsing, and validation functions are side-effect free, enabling reliable reasoning, easy debugging, and formal verification of chain behavior.