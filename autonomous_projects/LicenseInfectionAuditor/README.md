# LicenseInfectionAuditor

## Overview
The `LicenseInfectionAuditor` is a high-performance, memory-efficient auditing tool designed to scan JSONL streams for copyleft license signatures. 

## The Agentic Gap
As AI-driven code generation becomes ubiquitous, a critical legal vulnerability has emerged: "GPL Infection." Large Language Models (LLMs) frequently regurgitate copyleft licenses (such as the GNU General Public License) within proprietary code generation logs. If undetected, integrating this code can legally compel an organization to open-source its proprietary software. This tool bridges the agentic gap by automatically and reliably detecting these license violations in massive LLM interaction logs before they reach production.

## Architecture
The system is built on three core architectural pillars:
* **Memory-Mapped I/O:** Utilizes memory mapping to handle massive JSONL log files efficiently, avoiding the memory overhead of loading entire files into RAM. It includes explicit win32 empty-file crash guards to ensure cross-platform stability.
* **Single-Pass O(N) Scanning:** Implements a pure O(N) algorithmic scanning engine that processes the JSONL stream in a single pass, detecting GPL signatures with minimal computational overhead.
* **Strict Dependency Injection:** Designed for rigorous Test-Driven Development (TDD). Components are decoupled using strict dependency injection, allowing comprehensive validation using `tmp_path` and `io.StringIO` without relying on fragile mocks.

## How it Works
1. **Safe I/O Wrapper:** The auditor first opens the target JSONL file using a memory-mapped I/O wrapper. On Windows, it explicitly guards against zero-byte file crashes. Furthermore, it ensures that any file descriptors (such as those returned by `tempfile.mkstemp()` during testing or temporary processing) are closed immediately via `os.close(fd)` to prevent `[WinError 32] PermissionError` on deletion.
2. **Core Scanning Engine:** The engine iterates through the memory-mapped file line by line. It applies a highly optimized, single-pass O(N) search algorithm to detect predefined GPL signature patterns within the JSON payloads.
3. **CLI Orchestrator:** The command-line interface parses user arguments, initializes the I/O wrapper and scanning engine via dependency injection, and outputs a structured JSON report detailing any detected infections.

## Usage

### Running the CLI
To audit a JSONL log file for GPL infections, run the CLI orchestrator and pass the path to your log file:

```bash
python cli.py <logfile.jsonl>
```

The tool will output a JSON report to standard output containing the scan results, including the line numbers and specific GPL signatures detected.

### Running Tests
The project features a strict TDD suite that validates all logic without the use of mocks. To run the comprehensive test suite, execute:

```bash
pytest
```

## Development Milestones
* **M1:** Core scanning engine (O(N) GPL signature detection).
* **M2:** Safe I/O wrapper (Memory-mapped file I/O with win32 guards).
* **M3:** CLI integration (Argument parsing and JSON reporting).
* **M4:** Comprehensive TDD validation (Strict DI, `tmp_path`, and `io.StringIO` testing).