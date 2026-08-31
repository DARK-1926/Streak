# TokenDriftAuditor

## Overview

TokenDriftAuditor solves silent token burn in agentic workflows by performing offline single-pass log auditing. It detects inefficiencies like prompt duplication, unbounded context growth, and retry storms that silently drain budgets. The tool processes JSONL log files containing LLM interaction records and generates structured reports highlighting cost drift and optimization opportunities.

## How it Works

The auditor operates in a single pass through the log stream, maintaining running totals and state without requiring multiple iterations. It computes SHA256 hashes of prompts to detect duplication, tracks session context growth to identify runaway conversations, and monitors retry patterns to catch error storms. Cost calculations use configurable per-token rates to estimate financial impact.

## Architecture

The system follows a pure functional core with dependency injection design:
- **Pure Core**: `core.py` contains stateless functions for parsing and auditing
- **Dependency Injection**: Functions accept iterables rather than file paths for testability  
- **Win32-Safe CLI**: Memory-mapped I/O with size checks prevents platform-specific crashes
- **Deterministic Models**: Dataclasses ensure consistent serialization and testing

## Usage

```bash
python cli.py --input logs.jsonl --cost-rate 0.01 --output report.json
```

Required input format: JSONL with fields `session_id`, `prompt_tokens`, `completion_tokens`, `prompt_text`, `status`.

## Testing

Run the complete test suite with:
```bash
python test_main.py
```

Tests validate mathematical correctness of cost calculations, edge cases (empty logs, malformed JSON), and exact report field structures using in-memory iterables.

## Design Decisions

- **Single-Pass Processing**: Avoids `itertools.tee` memory issues by tracking state incrementally
- **Mock-Free Testing**: Pure function injection enables 100% coverage without I/O mocks
- **Win32 Safety**: File size validation prevents mmap crashes on Windows platforms
- **Stdlib Only**: Zero external dependencies for maximum portability across environments

## Interface Contracts

**core.py**:
- `parse_log_line(str) -> Optional[dict]`: Validates and normalizes JSON log entries
- `run_audit_stream(Iterable[dict], float) -> AuditReport`: Processes events and returns findings

**cli.py**:
- `stream_jsonl_file(str) -> Iterable[dict]`: Provides memory-efficient file streaming
- `main() -> None`: Command-line entry point with argument parsing