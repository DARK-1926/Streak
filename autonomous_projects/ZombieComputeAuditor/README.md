# ZombieComputeAuditor

## The Problem

In distributed AI and cloud computing environments, autonomous agents are frequently provisioned to execute complex workloads. However, due to network partitions, deadlocks, unhandled exceptions, or software bugs, some agents enter a "zombie" state. These zombie agents continue to consume expensive cloud compute resources and energy without producing any meaningful task completions. 

Left unchecked, zombie agents lead to severe cloud cost overruns and unnecessary energy waste. **ZombieComputeAuditor** is a specialized tool designed to parse agent telemetry logs, identify these anomalies, and flag them for immediate termination.

## Architecture

ZombieComputeAuditor is built on a foundation of robust, decoupled software engineering principles:

*   **Decoupled Pure Logic vs. I/O:** The system strictly separates business logic from file system operations. The core module (`zombie_auditor.py`) consists entirely of pure functions responsible for parsing and data aggregation. It has no side effects and no knowledge of the file system. The CLI module (`cli.py`) handles all I/O, injecting a line generator into the core logic. This separation ensures the core logic is highly testable and resilient.
*   **Memory-Mapped I/O:** To handle massive, gigabyte-sized JSONL log files without exhausting system RAM, the CLI utilizes memory-mapped file reading (`mmap`) wrapped in context managers. This guarantees safe resource handling and optimal performance.
*   **Win32 Safety Features:** Cross-platform reliability is critical. The system includes explicit guards for empty files on Windows environments, which would otherwise cause `mmap` to throw an exception. Furthermore, during testing and temporary file generation, the architecture strictly enforces closing file descriptors returned by `tempfile.mkstemp()` (e.g., via `os.close(fd)`) immediately. This prevents `[WinError 32] PermissionError` when attempting to delete temporary files on Windows.

## How it Works

The auditing process follows a streamlined, single-pass data pipeline:

1.  **Ingestion:** The CLI opens the target JSONL log file using a memory-mapped context manager.
2.  **Streaming:** Lines are yielded one by one from the memory map as a generator, ensuring a minimal memory footprint regardless of file size.
3.  **Parsing & Aggregation:** The pure function in `zombie_auditor.py` consumes the generator. It attempts to parse each line as JSON. Malformed or incomplete records are gracefully ignored to prevent pipeline crashes. For valid records, it aggregates the total compute cost and task completion count per `agent_id` in a single pass.
4.  **Anomaly Detection:** Once the file is fully processed, the system evaluates the aggregated data against configurable thresholds (e.g., flagging any agent with a compute cost > $X and task completions == 0).
5.  **Reporting:** Agents identified as zombies are outputted to the console, allowing infrastructure teams to take corrective action.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ZombieComputeAuditor
   ```

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

To audit a log file, run the CLI and pass the path to your JSONL log file as an argument:

```bash
python cli.py <logfile>
```

**Example:**
```bash
python cli.py logs/agent_telemetry_20231024.jsonl
```

The CLI will process the file and output a list of zombie `agent_id`s that exceed the configured compute thresholds without completing tasks.

## Testing

ZombieComputeAuditor employs a strict Test-Driven Development (TDD) suite to validate anomaly detection, resilience against malformed/incomplete logs, and safe CLI file processing.

To run the test suite, execute the following command from the project root:

```bash
pytest
```

The test suite utilizes `tmp_path` for safe, isolated file system testing, adhering to the Win32 safety protocols regarding file descriptor management.