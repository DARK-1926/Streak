# AgentSpendDriftAuditor

A robust CLI tool designed to audit agent JSONL logs for AWS-style billing spikes and floating-point drift. Built with a focus on mathematical precision, cross-platform file I/O safety, and strict testing methodologies.

## Architecture

The system is built on a foundation of pure functions and robust, cross-platform file operations.

*   **Pure Mathematical Logic:** Cost accumulation and sliding-window spike detection are implemented as pure functions using Python's `decimal.Decimal` to prevent floating-point drift inherent in standard IEEE 754 floats.
*   **Robust File I/O:** Utilizes memory-mapped files (`mmap`) for high-performance reading of large JSONL logs, abstracted behind a safe orchestration layer.
*   **CLI Interface:** Wired via `argparse` for seamless command-line integration and argument parsing.
*   **Testing Strategy:** Employs `pytest` with a strict no-mock policy. File I/O is tested using actual filesystem operations via `tmp_path`, while mathematical logic is tested via in-memory string iterables using Dependency Injection.

## How it Works

### Two-Pass `mmap` Strategy
To efficiently process large JSONL files without loading them entirely into memory, the auditor uses a two-pass memory-mapped reading strategy:
1.  **Pass One (Validation & Mapping):** The system checks the file metadata and establishes the memory map. It validates the file structure and prepares the read-only view of the underlying data.
2.  **Pass Two (Iteration & Analysis):** The system iterates through the mapped memory line-by-line. It parses the JSON payloads and streams the extracted cost data into the pure mathematical functions for drift validation and spike detection.

### Win32 Empty-File Guard
Memory mapping an empty file (0 bytes) on Windows raises an `OSError`. The I/O layer includes an explicit guard that checks the file size via `os.path.getsize()` before invoking `mmap`. If the file is empty, it safely bypasses the mapping process and yields an empty iterable, ensuring cross-platform stability without crashing.

### Cross-Platform Access Flags
The `mmap` implementation strictly uses the `mmap.ACCESS_READ` flag. This ensures the file is opened in a read-only state at the OS level. This prevents accidental modifications to the audit logs and avoids permission conflicts across different operating systems (Linux, macOS, Windows).

### Dependency Injection for Pure Testing
To maintain a strict "no mocks" testing policy, the architecture relies on Dependency Injection. The core analysis engine accepts iterables of strings rather than direct file paths. 
*   **Math Testing:** In-memory lists of JSON strings are passed directly to the engine to validate `Decimal` accumulation and sliding-window algorithms in isolation.
*   **I/O Testing:** The `pytest` `tmp_path` fixture is used to write actual temporary files. These files are then processed by the `mmap` layer to verify real-world file handling, including the Win32 empty-file guard and file descriptor management.

## Code Quality & Standards

*   **Type Hinting:** All function signatures utilize strict type hints.
*   **Documentation:** Comprehensive docstrings are provided for all public classes and methods.
*   **Function Size:** Functions are strictly kept under 50 lines to ensure readability and maintainability.
*   **Exception Handling:** Exceptions are handled gracefully, particularly around file I/O operations.
*   **PEP 8:** All Python code adheres to PEP 8 guidelines.
*   **Windows Compatibility:** File descriptors returned by `tempfile.mkstemp()` are immediately closed (e.g., `os.close(fd)`) to prevent `[WinError 32] PermissionError` during deletion in test environments.

## Usage Instructions

### Prerequisites
*   Python 3.8+
*   `pytest` (for running tests)

### Installation
```bash
git clone <repository-url>
cd AgentSpendDriftAuditor
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running the CLI
```bash
python -m agent_spend_drift_auditor --file path/to/agent_logs.jsonl --window 10 --threshold 50.00
```

### Running Tests
```bash
pytest
```

## Spec Roadmap & Milestones

*   [x] **Milestone 1:** Drift math validation (Pure `Decimal` functions).
*   [x] **Milestone 2:** Spike detection algorithm (Sliding-window implementation).
*   [x] **Milestone 3:** Safe `mmap` orchestration (Two-pass strategy, Win32 guards, `ACCESS_READ`).
*   [x] **Milestone 4:** End-to-end CLI integration (`argparse` wiring and full system tests).