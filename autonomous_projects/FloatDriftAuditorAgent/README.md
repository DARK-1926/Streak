# FloatDriftAuditorAgent

FloatDriftAuditorAgent is a high-performance billing drift auditor designed to detect, quantify, and report financial discrepancies caused by floating-point arithmetic inaccuracies in large-scale transaction processing systems. 

## The AWS $1.7B Float Drift Problem

In high-frequency billing environments, processing millions of transactions per second using standard IEEE 754 floating-point arithmetic (`float` in Python) introduces microscopic rounding errors. For example, `0.1 + 0.2` evaluates to `0.30000000000000004`. While negligible in isolation, when aggregated over billions of micro-transactions—such as those seen in AWS-scale cloud billing—these errors compound into massive financial discrepancies, potentially resulting in millions or even billions of dollars in unaccounted "drift."

FloatDriftAuditorAgent solves this problem by strictly enforcing base-10 exact arithmetic using Python's built-in `decimal` module. By ingesting transaction data as raw strings and parsing them directly into `Decimal` objects, the system entirely bypasses binary floating-point representation, ensuring absolute mathematical precision.

## Architecture Overview

The project is built upon a strict Spec Roadmap divided into four distinct milestones:

### Milestone 1: Pure Data Models and Interface Contracts
The foundation relies on strict typing and immutable data structures. Interfaces define the contracts for data ingestion, processing, and reporting, ensuring that the core logic remains decoupled from external I/O operations.

### Milestone 2: Pure Functional Core Logic
The mathematical core is implemented as a set of pure functions. It accepts an iterable of strings (representing transaction amounts) and an expected total, returning the exact drift. This functional approach guarantees deterministic outputs for given inputs, making the math logic trivial to test and verify.

### Milestone 3: Memory-Mapped File I/O with Win32 Guards
To handle massive billing logs without exhausting RAM, the system utilizes memory-mapped file I/O (`mmap`). This allows the application to process multi-gigabyte files with zero-copy efficiency. Specialized guards are implemented to handle OS-specific edge cases, particularly on Windows.

### Milestone 4: Comprehensive Testing Strategy
Testing is executed using `pytest` and `tmp_path`. The strategy strictly forbids mocking core logic. Instead:
*   **Pure Math Logic:** Validated using in-memory lists of strings.
*   **I/O and mmap Safety:** Validated using physical temporary files to ensure real-world OS interactions (like file locking and memory mapping) behave correctly.

## How it Works

1.  **Ingestion:** The system reads billing logs line-by-line. To prevent premature float conversion, data is kept as raw strings (e.g., `"10.99"`) for as long as possible.
2.  **Parsing:** Strings are passed directly into `decimal.Decimal()`. This ensures the exact base-10 value is preserved in memory.
3.  **Accumulation:** The `Decimal` values are summed using a pure functional reducer.
4.  **Drift Detection:** The accumulated `Decimal` total is subtracted from the expected `Decimal` total. Any non-zero result indicates a drift, which is then logged and flagged for audit.

## Key Technical Strategies

### Dependency Injection for Testability

To ensure the core logic remains pure and testable without mocking, FloatDriftAuditorAgent relies heavily on Dependency Injection. The core auditor does not know how to read files; it only knows how to process an `Iterable[str]`. 

```python
from decimal import Decimal
from typing import Iterable

def calculate_drift(transactions: Iterable[str], expected_total: str) -> Decimal:
    """
    Calculate the drift between accumulated transactions and the expected total.
    
    Args:
        transactions: An iterable of string representations of transaction amounts.
        expected_total: The string representation of the expected total.
        
    Returns:
        A Decimal representing the exact financial drift.
    """
    actual_total = sum((Decimal(tx) for tx in transactions), Decimal('0.00'))
    return actual_total - Decimal(expected_total)
```

By injecting the data source, we can test the math with simple Python lists, and inject a file-reader generator for integration tests.

### The `mmap` Strategy for Performance

Reading multi-gigabyte billing logs using standard `readlines()` can cause memory spikes. FloatDriftAuditorAgent uses `mmap` to map the file directly into virtual memory, allowing the OS to handle paging efficiently.

```python
import mmap
import os
from typing import Generator

def read_large_log(file_path: str) -> Generator[str, None, None]:
    """
    Safely read a file using mmap for zero-copy performance.
    
    Args:
        file_path: Path to the billing log file.
        
    Yields:
        Decoded string lines from the file.
    """
    # Win32 empty-file guard: mmap throws ValueError on 0-byte files
    if os.path.getsize(file_path) == 0:
        return 
        
    with open(file_path, "r+b") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for line in iter(mm.readline, b""):
                yield line.decode('utf-8').strip()
```

### Win32 Empty-File Guard and File Descriptor Management

Windows handles file locking and memory mapping differently than POSIX systems. Two critical guards are implemented:

1.  **Empty-File Guard:** Calling `mmap.mmap()` on a 0-byte file raises a `ValueError` on Windows. The `read_large_log` function explicitly checks `os.path.getsize()` and returns early if the file is empty.
2.  **File Descriptor Closure:** When creating temporary files for testing using `tempfile.mkstemp()`, Windows locks the file as long as the file descriptor is open. Attempting to delete or `mmap` this file without closing the descriptor results in a `[WinError 32] PermissionError`.

```python
import os
import tempfile

def create_temp_log() -> str:
    """
    Create a temporary file, properly closing the descriptor on Windows.
    
    Returns:
        The path to the newly created temporary file.
    """
    fd, path = tempfile.mkstemp()
    # CRITICAL: Close the file descriptor immediately to prevent 
    # [WinError 32] PermissionError on Windows during deletion or mmap.
    os.close(fd) 
    return path
```

## Testing Strategy

Tests are written using `pytest` and leverage the `tmp_path` fixture for safe, isolated file system operations.

*   **Unit Tests:** Focus on `calculate_drift`. We pass lists like `["0.1", "0.2"]` and assert the result against `Decimal("0.3")`. No file I/O is involved.
*   **Integration Tests:** Focus on `read_large_log`. We use `create_temp_log()` to generate a physical file, write binary data to it, and assert that the generator yields the correct strings. We also test the Win32 empty-file guard by passing an empty temporary file and ensuring no exceptions are raised.