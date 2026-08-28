# AgentSwarmLoopAuditor

AgentSwarmLoopAuditor is a high-performance, single-pass streaming tool designed to detect and report degenerate behaviors in autonomous AI agent swarms. By analyzing JSONL event logs in real-time, it identifies infinite tool-call loops and state thrashing, preventing massive token waste and stalled execution.

## The Agentic Gap

When autonomous agents operate in complex environments or juggle multiple concurrent sessions, they frequently fall into degenerate behavioral patterns. This phenomenon, known as the **Agentic Gap**, manifests in two primary ways:

1. **Infinite Tool-Call Loops:** An agent repeatedly invokes the exact same tool with the identical arguments, failing to recognize that the environment state has not changed or that the action is futile.
2. **A-B Thrashing (File-Edit Oscillation):** An agent enters a destructive oscillation between two states. For example, it writes a configuration file, reads it back, decides it needs a minor tweak, writes it again, reads it again, and loops indefinitely. 

These loops rapidly exhaust context windows, burn through API credits, and stall overall swarm progress. AgentSwarmLoopAuditor bridges this gap by providing a deterministic, low-overhead auditing layer that catches these patterns before they cause catastrophic resource drain.

## Architecture

The system is built upon four atomic milestones:

1. **Strict Data Models:** Pydantic-backed models for `AgentAction` and `LoopReport` ensure type safety and strict validation of incoming JSONL events.
2. **Win32-Safe Mmap Streaming:** A memory-mapped file streaming engine that reads JSONL logs without loading the entire file into RAM, specifically hardened for Windows file-locking semantics.
3. **Single-Pass Loop Detection:** A pure, stateless sliding-window algorithm that detects exact repetitions and alternating A-B patterns in a single pass.
4. **CLI & TDD Integration:** A command-line interface wired to the core engine, validated by a strict Test-Driven Development (TDD) suite utilizing in-memory injection and real tempfile I/O.

## How it Works

### Single-Pass Streaming Design
Traditional log analyzers load entire files into memory or use naive line-by-line reading which can be slow for massive agent logs. AgentSwarmLoopAuditor utilizes memory-mapped files (`mmap`) to stream JSONL data. This allows the OS to handle paging, keeping the memory footprint strictly bounded regardless of the log file size.

### Sliding Window Detection
The core detection logic is a pure function that maintains a bounded `collections.deque` (the sliding window). As each `AgentAction` is parsed from the stream:
1. The action is hashed into a deterministic signature (Tool Name + Sorted Arguments).
2. The signature is pushed to the window.
3. The window is analyzed for **Exact Loops** (e.g., A-A-A-A) by checking if all elements in the window share the same hash.
4. The window is analyzed for **Alternating Loops** (e.g., A-B-A-B) by checking if the even-indexed elements match and the odd-indexed elements match.

Because the logic is entirely pure and stateless (relying only on the injected window state), it is highly predictable and easily testable.

## Win32 Mmap Safety & Tempfile Handling

Memory mapping and temporary file handling on Windows require special care due to strict file locking mechanisms. If a file descriptor is left open, or if a file is actively memory-mapped, attempting to delete or modify the file will result in a `[WinError 32] PermissionError`.

To ensure cross-platform compatibility and graceful exception handling, all temporary file operations strictly close the file descriptor returned by `tempfile.mkstemp()` immediately on Windows.

```python
import os
import tempfile
from contextlib import contextmanager
from typing import Generator

@contextmanager
def safe_tempfile(suffix: str = ".jsonl") -> Generator[str, None, None]:
    """
    Context manager for cross-platform safe temporary files.
    
    Ensures that on Windows, the file descriptor from mkstemp is 
    closed immediately to avoid [WinError 32] PermissionError during
    subsequent deletion or memory mapping operations.
    
    Args:
        suffix: File extension for the temporary file.
        
    Yields:
        The absolute path to the created temporary file.
    """
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        # CRITICAL: Close fd immediately on Windows to prevent locking
        if os.name == 'nt':
            os.close(fd)
        yield path
    except Exception as e:
        # Gracefully handle and log exceptions during yield
        print(f"Error during tempfile usage: {e}")
        raise
    finally:
        # Ensure fd is closed on POSIX systems
        if os.name != 'nt':
            try:
                os.close(fd)
            except OSError:
                pass
        
        # Safely clean up the file
        if os.path.exists(path):
            try:
                os.remove(path)
            except PermissionError:
                pass
```

## Testing Strategy

The project enforces a strict, zero-mock testing philosophy to ensure deterministic validation:

* **Pure In-Memory Injection:** The sliding window detection logic is tested by injecting synthetic lists of `AgentAction` objects directly into the pure functions. This guarantees that the mathematical logic of loop detection is flawless.
* **Real Tempfile I/O:** The streaming and mmap layers are tested using actual file system operations via the `safe_tempfile` context manager. We do not mock `open()` or `mmap.mmap()`. This ensures that Win32 file-locking edge cases are caught during the test phase.
* **Deterministic Validation:** Tests assert exact matches on `LoopReport` outputs, verifying both the detection of loops and the precise calculation of wasted tokens.

## CLI Usage

AgentSwarmLoopAuditor provides a streamlined CLI for analyzing agent logs. You can pipe JSONL logs directly into the auditor or pass a file path.

### Piping from Standard Input
Stream logs directly from your agent orchestrator into the auditor:

```bash
cat agent_swarm_logs.jsonl | python -m agent_swarm_loop_auditor --stream stdin
```

### Analyzing a File with Custom Window Size
Analyze a static JSONL file, adjusting the sliding window to detect longer thrashing patterns:

```bash
python -m agent_swarm_loop_auditor --input logs/session_42.jsonl --window-size 12 --strict
```

### Output Format
The CLI outputs a structured JSON report to `stdout`, making it easy to integrate into CI/CD pipelines or monitoring dashboards:

```json
{
  "session_id": "session_42",
  "total_actions": 1402,
  "loops_detected": 3,
  "estimated_tokens_wasted": 45200,
  "reports": [
    {
      "type": "ALTERNATING_THRASH",
      "actions": ["write_file", "read_file"],
      "occurrences": 42,
      "start_line": 800,
      "end_line": 884
    }
  ]
}