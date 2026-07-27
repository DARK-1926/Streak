# BatchingStarvationAuditor

A Spec-Driven Roadmap and auditing tool designed to solve the ML Inference 'Waiting Equation' problem.

## The Problem: The 'Waiting Equation'

In high-throughput machine learning inference servers, batching is utilized to maximize hardware utilization. However, these servers often suffer from the 'Waiting Equation': requests are held in a queue for too long while waiting for a batch to fill to its optimal size. This dynamic batching strategy can cause severe latency spikes for early-arriving requests, leading to timeouts and degraded user experience. BatchingStarvationAuditor identifies, audits, and quantifies these "starved" requests.

## Architecture

The project is built on a strict separation of concerns to ensure reliability and testability:

* **Pure Functional Core (`batching_auditor.py`)**: Contains the single-pass metric aggregation logic. It is completely decoupled from file I/O, making it highly testable, deterministic, and free from side effects.
* **Memory-Mapped I/O (`cli.py`)**: Handles the ingestion of large log files using robust memory-mapped file I/O. It includes specific guards for win32 environments to handle empty files gracefully, preventing `[WinError 32] PermissionError` and mapping exceptions.

## How it Works

1. **Event Schema**: The auditor processes JSONL (JSON Lines) log files where each line represents an inference event. The strict schema requires the following fields:
   * `request_id`: Unique identifier for the inference request.
   * `arrival_time`: Timestamp of when the request entered the queue.
   * `batch_id`: Identifier of the batch the request was assigned to.
   * `execution_time`: Time taken to process the batch.
   * `queue_wait_ms`: Total milliseconds the request waited in the queue before execution.

2. **Single-Pass Aggregation**: The core engine streams the parsed JSONL data and calculates critical metrics in a single pass to minimize memory overhead. It computes total requests, starved requests (those exceeding a defined wait threshold), maximum wait time, and average wait time.

3. **Decoupled Testing Strategy**: The testing suite (`test_main.py`) validates the system without relying on mocks. It feeds synthetic JSONL strings directly into the aggregator for unit testing the pure logic, and uses temporary files (`tmp_path`) to validate the memory-mapped I/O pipeline end-to-end.

## Installation

Ensure you have Python 3.8+ installed. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the CLI tool against a JSONL log file, specifying the starvation threshold in milliseconds:

```bash
python cli.py <logfile.jsonl> --threshold 50
```

## Testing

The project utilizes a strict TDD suite built with `pytest`. To run the tests and validate both the pure aggregation logic and the file I/O pipeline, execute:

```bash
pytest test_main.py