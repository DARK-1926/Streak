# SpikeGuardAgent

SpikeGuardAgent is a high-performance, memory-safe log analysis tool designed to monitor Large Language Model (LLM) interactions. It specializes in identifying AI sycophancy loops and anomalous billing spikes in real-time or batch log streams. By leveraging O(N) pure functions and a robust I/O layer, SpikeGuardAgent processes massive log files efficiently without exhausting system memory.

## How it Works

SpikeGuardAgent solves complex behavioral and financial anomalies in LLM deployments through deterministic, stateless algorithms:

1. **Solving AI Sycophancy Loops:** LLMs can sometimes fall into infinite agreement loops, repeatedly validating user prompts without providing new information. SpikeGuardAgent utilizes an O(N) sequence loop detection algorithm. By maintaining a rolling hash of interaction payloads, the pure function identifies repeating conversational cycles in a single pass, flagging them as sycophancy anomalies.
2. **Solving Billing Spikes:** Unexpected surges in token generation or API calls can lead to massive financial losses. The system employs an O(N) sliding-window frequency spike detection algorithm. It tracks token usage and request frequencies over configurable time windows, instantly detecting and reporting statistical deviations that indicate billing spikes.

Both algorithms are implemented as pure, stateless functions, ensuring predictable outputs, easy testability, and thread safety.

## Architecture

The project is structured into three primary modules, adhering to strict separation of concerns:

* **Core Algorithms (`sentinel_core.py`):** Contains the O(N) pure functions for sequence loop detection and sliding-window frequency analysis. These functions accept iterables and yield anomaly reports without performing any I/O operations.
* **Safe I/O Layer (`sentinel_io.py`):** Implements a robust generator for streaming log lines using memory mapping (`mmap`). It includes strict win32 safeguards against empty files and features a regex-based timestamp extractor to normalize log entries.
* **CLI Wiring (`main.py`):** The entry point that parses command-line arguments, wires the I/O generator into the core algorithms using a memory-safe two-pass approach, and outputs a structured JSON anomaly report.

## Key Design Strategies

### Dependency Injection Strategy

To ensure deterministic validation and complete testability, SpikeGuardAgent relies on a strict Dependency Injection strategy. Core algorithms do not accept file paths; instead, they accept generic `Iterable[str]` streams. 

This design allows the testing suite (`test_main.py`) to inject synthetic `io.StringIO` streams directly into the core logic. By avoiding `unittest.mock`, the tests validate the actual parsing and algorithmic behavior against realistic data structures, ensuring high confidence in production deployments.

### Two-Pass Memory-Safe Execution Model

Processing multi-gigabyte log files requires careful memory management. The CLI wiring utilizes a two-pass memory-safe execution model:

1. **Pass One (Metadata Extraction):** The I/O generator streams the file via `mmap`, using regex to extract and validate timestamps. This pass filters out malformed lines and establishes the temporal boundaries of the log without loading the payload into memory.
2. **Pass Two (Algorithmic Analysis):** The validated stream is passed to the O(N) pure functions. The sliding window and sequence detectors process the data incrementally, maintaining only the minimal state required for the current window. 

This approach guarantees a flat memory footprint regardless of the input file size.

### Win32 `mmap` Safety Checks

Cross-platform file handling introduces specific edge cases, particularly on Windows. The Safe I/O Layer implements rigorous win32 `mmap` safety checks:

* **Empty File Safeguards:** Windows `mmap` throws an exception when attempting to map a 0-byte file. The I/O layer explicitly checks file sizes before initialization, gracefully bypassing empty logs.
* **File Descriptor Management:** When creating temporary files for testing or intermediate processing, Windows strictly locks file descriptors. The system ensures that file descriptors returned by `tempfile.mkstemp()` are closed immediately to prevent `[WinError 32] PermissionError` upon deletion.

```python
import os
import tempfile
from typing import Tuple

def create_safe_temp_file() -> Tuple[int, str]:
    """
    Create a temporary file and immediately close the file descriptor.
    
    Returns:
        Tuple[int, str]: The file descriptor (closed) and the file path.
    """
    fd, path = tempfile.mkstemp()
    try:
        # On Windows, always close file descriptors returned by 
        # tempfile.mkstemp() immediately to prevent [WinError 32] 
        # PermissionError on deletion.
        os.close(fd)
    except OSError as e:
        print(f"Failed to close file descriptor: {e}")
    return fd, path
```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd SpikeGuardAgent
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the CLI tool against a log file to generate a JSON anomaly report:

```bash
python main.py --input logs/llm_interactions.log --output report.json --window-size 60
```

**Arguments:**
* `--input`: Path to the LLM interaction log file.
* `--output`: Path to save the JSON anomaly report.
* `--window-size`: Time window in seconds for billing spike detection.

## Testing

SpikeGuardAgent utilizes `pytest` for deterministic validation. The test suite strictly avoids `unittest.mock`, relying instead on synthetic `io.StringIO` streams and `pytest`'s built-in `tmp_path` fixture for real file I/O testing.

To run the test suite, execute the following command from the project root:

```bash
pytest test_main.py -v
```

This will validate the O(N) core algorithms, the win32 `mmap` safety checks, and the two-pass execution model against a variety of synthetic edge cases.