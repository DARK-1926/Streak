# SlopFilterAgent

SlopFilterAgent is a high-performance, memory-efficient data pipeline designed to detect and filter AI-generated "slop" from large CSV datasets. By leveraging pure mathematical heuristics and robust software engineering principles, it provides a scalable solution for dataset curation.

## Architecture

The project is structured around a modular, decoupled architecture that separates mathematical analysis, data parsing, orchestration, and I/O operations:

*   **`heuristics.py`**: Contains pure mathematical functions for text analysis. It is completely isolated from I/O operations, making it highly testable and deterministic.
*   **`csv_processor.py`**: Handles the parsing and formatting of CSV data. It relies on Dependency Injection (DI) to accept generic text streams rather than concrete file paths.
*   **`agent.py`**: The orchestration layer that coordinates the filtering pipeline. It applies heuristic thresholds to the parsed data streams and yields filtered results.
*   **`main.py`**: The CLI entry point. It bridges the gap between the filesystem and the core logic, utilizing memory-mapped I/O (`mmap`) for optimal performance on large files.
*   **`test_main.py`**: A comprehensive test suite validating the entire pipeline, from pure unit tests to integration tests.

## How it Works

### 1. Heuristic Analysis: Entropy and Repetition
To distinguish between human-written text and AI-generated slop, SlopFilterAgent relies on two primary mathematical indicators:

*   **Shannon Entropy**: This metric measures the information density and unpredictability of a string. AI models often produce text with a narrower, more predictable token distribution compared to human writing. By calculating the Shannon entropy of character or word distributions, the agent can flag text that falls below a certain randomness threshold, indicating potential synthetic origin.
*   **Repetition Ratios**: LLMs are prone to repeating specific phrases, n-grams, or structural patterns, especially when generating long-form content. The repetition heuristic calculates the ratio of unique n-grams to total n-grams. A low ratio indicates high redundancy, a common hallmark of AI slop.

### 2. Dependency Injection for Testability
To ensure the core logic remains pure and easily testable, `csv_processor.py` and `agent.py` are designed using Dependency Injection. Instead of accepting file paths and opening files internally, these modules accept objects inheriting from `io.TextIOBase`. 

This strategy allows the production code to process actual files while the test suite can inject `io.StringIO` objects containing synthetic data. This eliminates the need for complex filesystem mocks and ensures tests run rapidly and reliably in memory.

### 3. Memory Efficiency via `mmap`
When dealing with massive CSV datasets, loading the entire file into RAM is inefficient and can lead to out-of-memory errors. The CLI entry point (`main.py`) solves this by utilizing Python's `mmap` module. 

Memory mapping allows the operating system to map the file directly into virtual memory. The application can then interact with the file as if it were a mutable string or byte array, but the OS handles paging data in and out of physical RAM as needed. This enables SlopFilterAgent to process gigabytes of data with a minimal memory footprint.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd SlopFilterAgent
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To filter a CSV file, execute the `main.py` script via the command line. The script exposes a `process_file` function that handles the memory-mapped I/O and passes the stream to the orchestration agent.

```bash
python main.py --input dataset.csv --output filtered_dataset.csv --entropy-threshold 3.5 --repetition-threshold 0.2
```

### Arguments
*   `--input`: Path to the source CSV file.
*   `--output`: Path where the filtered CSV will be saved.
*   `--entropy-threshold`: Minimum Shannon entropy required to keep a row (default: 3.5).
*   `--repetition-threshold`: Maximum allowed repetition ratio (default: 0.2).

## Testing Strategy

The project employs a rigorous testing strategy defined in `test_main.py`, utilizing `pytest`.

1.  **Pure Function Validation**: The mathematical logic in `heuristics.py` is tested using standard inputs and expected outputs to guarantee accuracy without side effects.
2.  **Stream Injection**: CSV parsing and agent orchestration are tested by injecting `io.StringIO` streams populated with synthetic 'slop' and 'human' data. This validates the filtering logic without touching the disk.
3.  **Integration Testing**: An end-to-end integration test verifies the `mmap` implementation. It creates a temporary file, memory-maps it, and runs it through the full pipeline.

### Running Tests

Execute the test suite using pytest:

```bash
pytest test_main.py -v
```

*Note on Cross-Platform Compatibility*: The integration tests strictly adhere to best practices for temporary file handling. On Windows, file descriptors returned by `tempfile.mkstemp()` are immediately closed (e.g., `os.close(fd)`) before the file is accessed by `mmap` or deleted. This prevents `[WinError 32] PermissionError` exceptions during test teardown.