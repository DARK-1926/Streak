# ContextDriftAuditor

ContextDriftAuditor is a high-performance, deterministic auditing tool designed to analyze codebases and documentation for structural alignment and semantic degradation. 

## The Problem

In modern software engineering, two critical issues degrade the quality of technical documentation and organizational knowledge:

1. **Organizational Knowledge Drift**: As codebases evolve, documentation often fails to keep pace. Symbols, functions, and architectural patterns declared in the code become disconnected from the knowledge base, leading to outdated, misleading, or incomplete documentation.
2. **LLM Slop**: The widespread adoption of Large Language Models for generating documentation has introduced "slop"—verbose, filler-heavy, and non-deterministic text. This obscures technical meaning, lowers the signal-to-noise ratio, and makes knowledge bases difficult to parse for both humans and automated systems.

ContextDriftAuditor solves these problems by mathematically quantifying drift and deterministically scoring LLM-generated filler.

## How it Works

ContextDriftAuditor processes JSONL (JSON Lines) manifests and knowledge bases through a highly optimized, multi-stage pipeline:

1. **Pure Data Parsing**: The system ingests JSONL streams using pure data structures, ensuring that parsing logic is entirely decoupled from side effects.
2. **O(N) Drift Detection**: The core engine maps declared code symbols against referenced symbols in the documentation text. By utilizing hash maps and single-pass algorithms, it achieves O(N) time complexity, instantly identifying missing, undocumented, or orphaned components even in massive repositories.
3. **Deterministic Slop Scoring**: To combat LLM verbosity, the auditor evaluates documentation text against a predefined, curated dictionary of known LLM filler phrases. It calculates a strict "slop score" for each document, flagging areas where AI-generated noise has degraded technical clarity.

## Architecture

The system is built on principles of robustness, performance, and strict cross-platform compatibility:

* **Pure Functions & Dependency Injection (DI)**: Core logic relies on pure functions and DI. This ensures zero side effects, predictable outputs, and seamless testability.
* **Low-Memory Processing**: The CLI utilizes `mmap` (memory-mapped file I/O) to process massive JSONL repositories. This allows the auditor to scan gigabytes of data without loading entire files into RAM.
* **Strict Win32 Guards**: Windows file-locking mechanisms often cause issues during temporary file creation and deletion. The architecture implements strict empty-file guards and ensures that file descriptors returned by `tempfile.mkstemp()` are immediately closed (e.g., via `os.close(fd)`) to prevent `[WinError 32] PermissionError` during teardown.

## Installation

Clone the repository and install the required dependencies. It is highly recommended to use a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Run the auditor by providing a manifest file and a knowledge base file in JSONL format:

```bash
python cli.py manifest.jsonl knowledge.jsonl
```

The CLI will output the drift analysis and slop scores directly to standard output.

### Running Tests

The project features a comprehensive Test-Driven Development (TDD) suite. It validates all edge cases, including empty streams, missing keys, high slop, zero drift, and CLI execution, utilizing in-memory streams and `tmp_path` fixtures.

Execute the test suite using `pytest`:

```bash
pytest
```

## Development Guidelines

Contributors must adhere to the following strict engineering standards:

* **Type Hinting**: Use type hints for all function signatures.
* **Documentation**: Write comprehensive docstrings for all public classes and methods.
* **Complexity**: Keep functions strictly under 50 lines.
* **Error Handling**: Handle exceptions gracefully; do not allow silent failures.
* **Style**: Follow PEP 8 guidelines for all Python code.
* **Windows Compatibility**: Always close file descriptors returned by `tempfile.mkstemp()` immediately to prevent permission errors on deletion.