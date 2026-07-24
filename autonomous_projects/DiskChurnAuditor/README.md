# DiskChurnAuditor

## Overview
DiskChurnAuditor is a high-performance telemetry analysis tool designed to track SSD wear caused by beta applications. By parsing JSONL telemetry logs, it identifies processes responsible for excessive disk writes and calculates write amplification metrics. This enables developers to pinpoint and optimize high-churn behaviors before they lead to premature hardware degradation.

## Architecture
The project is engineered for reliability, low memory overhead, and strict testability:
* **Pure Functions & DI**: Core logic is isolated into pure functions utilizing Dependency Injection, ensuring predictable behavior and effortless unit testing.
* **Low Memory Footprint**: To handle gigabytes of telemetry data without exhausting RAM, the I/O layer leverages memory-mapped files (`mmap`) paired with generator-based streaming.
* **Robustness**: Explicit file size checks and strict resource cleanup prevent platform-specific crashes (e.g., win32 empty file handling).

## How it Works
The application operates through a streamlined, four-stage pipeline:

1. **Safe I/O Layer**: The system opens the target JSONL log using a generator-based file streamer backed by `mmap`. It performs explicit `os.path.getsize` checks to safely bypass empty files and prevent Windows crashes, ensuring all file descriptors are strictly cleaned up.
2. **Core Aggregation Engine**: Data is fed into a pure, single-pass O(N) aggregation function. This engine calculates write amplification metrics per process, robustly handling missing keys or malformed JSON entries without interrupting the pipeline.
3. **CLI Orchestration**: An `argparse`-based command-line interface wires the Safe I/O Layer to the Core Engine. It catches file system errors gracefully and outputs a cleanly formatted report of the highest-churn processes.
4. **TDD Validation**: The entire codebase is verified through a strict Test-Driven Development suite. Using `pytest`, `tmp_path`, and `capsys`, the tests validate pure logic, I/O behavior, and CLI integration with zero reliance on mock objects.

## Installation

Clone the repository and set up a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

To analyze a telemetry log file and generate a churn report, run the CLI module:

```bash
python -m disk_churn.cli <logfile>
```

Replace `<logfile>` with the path to your JSONL telemetry data.

## Testing

The project includes a comprehensive test suite that requires no external mocking. Run the tests using `pytest`:

```bash
pytest
```

## Development Guidelines

Contributors must adhere to the following standards to maintain code quality and cross-platform compatibility:

* **Type Hinting**: Use type hints for all function signatures.
* **Documentation**: Write comprehensive docstrings for all public classes and methods.
* **Brevity**: Keep functions focused and under 50 lines.
* **Error Handling**: Handle exceptions gracefully, particularly in the I/O layer.
* **Style**: Follow PEP 8 guidelines for all Python code.
* **Windows Compatibility**: Always close file descriptors returned by `tempfile.mkstemp()` (e.g., `os.close(fd)`) immediately to prevent `[WinError 32] PermissionError` during file deletion in tests.