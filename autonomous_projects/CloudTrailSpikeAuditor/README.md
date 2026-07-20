# CloudTrailSpikeAuditor

Detect AWS billing anomalies caused by runaway infrastructure provisioning without requiring cloud API access or heavy machine learning. CloudTrailSpikeAuditor processes massive CloudTrail JSONL logs locally, efficiently, and safely.

## How it Works

The architecture is divided into three primary components designed for high performance, strict testability, and cross-platform safety:

* **Memory-Mapped I/O (`io_engine.py`)**: Safely streams lines from massive JSONL files using Python's `mmap` module to avoid loading entire files into memory. It includes specialized guards for Windows (win32) environments to handle empty files gracefully, preventing `mmap` initialization crashes. Furthermore, any file descriptors returned by operations like `tempfile.mkstemp()` during testing or temporary file creation are immediately closed via `os.close(fd)` to prevent `[WinError 32] PermissionError` upon file deletion.
* **Event Aggregation (`sentinel_core.py`)**: Employs pure functions to parse JSON lines and aggregate critical provisioning events (e.g., `RunInstances`, `CreateVolume`, `CreateSubnet`). It processes the event stream in a strict single pass, avoiding memory duplication tools like `itertools.tee`. The module is built around Dependency Injection, allowing seamless testing with raw string arrays rather than relying on the file system for unit tests.
* **CLI Wiring (`main.py`)**: Connects the memory-mapped I/O engine and the core processing logic into a streamlined command-line interface, handling argument parsing and exception management gracefully.

## Installation

Ensure you have Python 3.8+ installed, then install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the auditor against a CloudTrail JSONL log file to detect provisioning spikes:

```bash
python main.py <logfile.jsonl>
```

## Testing

The project follows a strict Test-Driven Development (TDD) strategy. Tests are written using `pytest` and rely on actual file I/O via `tmp_path` for the I/O engine, and Dependency Injection for the core logic. No mocks are used in the test suite.

To run the test suite:

```bash
pytest
```

To run tests with verbose output:

```bash
pytest -v