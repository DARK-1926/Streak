# CloudDriftAuditor

CloudDriftAuditor is a strict, agentic billing anomaly detector designed to identify and prevent financial discrepancies caused by floating-point arithmetic inaccuracies. 

Historically, "float divergence" has plagued large-scale financial systems, where the cumulative effect of IEEE 754 floating-point rounding errors can lead to catastrophic discrepancies. This phenomenon is famously echoed in the AWS $1.7B billing error, where minute precision losses compounded into massive financial anomalies. CloudDriftAuditor solves this problem by performing a highly optimized, single-pass scan of billing CSVs, mathematically validating every transaction to ensure absolute precision.

## How it Works

CloudDriftAuditor operates on a zero-trust mathematical model. Instead of relying on standard floating-point accumulation, the system processes billing data in a single pass, simultaneously calculating the running total using two distinct methods:

1. **IEEE 754 Float Accumulation:** The standard, hardware-accelerated floating-point calculation used by most legacy billing systems.
2. **Exact Decimal Accumulation:** A strict, arbitrary-precision calculation utilizing Python's `decimal.Decimal` module.

By comparing the final accumulated values of these two methods at the end of the single-pass scan, CloudDriftAuditor can instantly detect "drift"—the exact point and magnitude where floating-point inaccuracies begin to corrupt financial data. If the delta between the float accumulation and the decimal accumulation exceeds a defined epsilon, an anomaly is flagged.

## Architecture

The project is built on a strict Spec Roadmap, divided into isolated, highly cohesive modules:

*   **`drift_engine.py` (Milestone 1):** The mathematical core of the auditor. It contains pure functions responsible for parsing numerical strings and performing the dual-accumulation logic. It compares IEEE 754 float accumulation against exact `decimal.Decimal` accumulation without side effects.
*   **`io_handler.py` (Milestone 2):** A robust I/O subsystem designed for high performance and cross-platform safety. It utilizes memory-mapped I/O (`mmap`) to process large CSV files efficiently. It includes explicit `os.path.getsize` guards to prevent zero-byte mapping crashes on Win32 systems, yielding safely decoded lines to the engine.
*   **`main.py` (Milestone 3):** The CLI orchestrator. It wires the memory-mapped I/O handler to the drift engine, providing a clean command-line interface for users to audit their billing files.
*   **`test_drift_engine.py` (Milestone 4):** A strict Test-Driven Development (TDD) suite. It validates the engine using `io.StringIO` and `pytest`'s `tmp_path` fixture to ensure zero mock usage, absolute mathematical accuracy, and Win32 file-locking safety.

## Installation

1. Clone the repository.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the CLI

To audit a billing CSV file for float divergence, use the CLI orchestrator:

```bash
python main.py <file.csv>
```

The auditor will perform a single-pass scan over the provided CSV and output a report detailing any mathematical drift detected between standard float accumulation and exact decimal accumulation.

### Running Tests

CloudDriftAuditor enforces strict TDD. To run the test suite and verify mathematical accuracy and Win32 safety, execute:

```bash
pytest
```

## Development Guidelines

Contributors must adhere to the following strict engineering standards:

*   **Type Hints:** Use type hints for all function signatures.
*   **Documentation:** Write comprehensive docstrings for all public classes and methods.
*   **Complexity:** Keep functions strictly under 50 lines.
*   **Error Handling:** Handle exceptions gracefully; do not let raw stack traces leak to the CLI.
*   **PEP 8:** Follow PEP 8 guidelines for all Python code.
*   **Win32 Safety:** On Windows, always close file descriptors returned by `tempfile.mkstemp()` (e.g., `os.close(fd)`) immediately. Failing to do so will result in `[WinError 32] PermissionError` when attempting to delete temporary test files.
*   **Zero Mocks:** Tests must validate actual behavior using `io.StringIO` and `tmp_path`. Mocking mathematical operations or I/O boundaries is strictly prohibited.