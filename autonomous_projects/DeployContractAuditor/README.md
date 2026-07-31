# DeployContractAuditor

## The Problem

Large Language Models (LLMs) acting as autonomous agents often drift from their intended execution paths. When provided with deployment contracts or instruction files like `claude.md`, they may skip critical validation steps, execute actions out of order, or perform unauthorized operations. This non-deterministic behavior poses severe risks in CI/CD pipelines and production deployments, where strict adherence to sequential protocols is mandatory.

## Architecture

DeployContractAuditor solves this via a high-performance, mmap-backed single-pass state machine. It ingests agent execution logs and strictly validates them against a predefined sequential contract. By utilizing memory-mapped file I/O, it handles massive log files efficiently without loading them entirely into memory, while remaining hardened against malformed JSON and Windows-specific empty-file crashes.

## How it Works

The auditor operates through a strict, five-phase pipeline:

1. **Strict JSON Schema Definition**: Agent logs must conform to a predefined schema containing `action`, `status`, and `timestamp`. Any deviation is immediately flagged.
2. **Memory-Mapped Log Parser**: A robust parser reads the log file using `mmap`. It yields parsed dictionaries line-by-line, gracefully handling malformed JSON and bypassing Win32 empty-file access violations.
3. **Single-Pass State Machine**: A pure function consumes the parsed log stream alongside a 'contract' (a list of required sequential actions). It flags any out-of-order or unlisted actions as unauthorized and accumulates compliance metrics in a single O(n) pass.
4. **CLI Wrapper**: A command-line interface orchestrates file paths, handles system error codes, and generates human-readable compliance reports.
5. **Comprehensive Testing**: A `unittest` suite verifies the state machine with synthetic in-memory streams, the parser with temporary files, and the CLI via `subprocess`, ensuring zero reliance on `unittest.mock`.

## Sample Formats

### JSONL Log Format
Agent execution logs must be formatted as JSON Lines (JSONL):

```json
{"timestamp": "2023-10-27T10:00:00Z", "action": "checkout_code", "status": "success"}
{"timestamp": "2023-10-27T10:01:00Z", "action": "run_tests", "status": "success"}
{"timestamp": "2023-10-27T10:05:00Z", "action": "build_image", "status": "success"}
```

### Contract List
The deployment contract is a simple JSON array defining the exact sequential actions required:

```json
[
  "checkout_code",
  "run_tests",
  "build_image",
  "push_registry",
  "deploy_staging"
]
```

## Usage

### Running the CLI

To audit an agent's execution log against a deployment contract, use the CLI wrapper:

```bash
python -m deploy_contract_auditor --log agent_execution.jsonl --contract deployment_contract.json
```

The CLI will output a compliance report and exit with code `0` if fully compliant, or `1` if unauthorized or out-of-order actions are detected.

### Running the Tests

The project includes a comprehensive test suite that avoids `unittest.mock` in favor of synthetic streams and real subprocess calls.

```bash
python -m unittest discover tests
```

## Development Guidelines

All Python code in this project strictly adheres to PEP 8. Functions are kept under 50 lines, utilize type hints, and include descriptive docstrings. 

When writing tests that interact with the file system, special care is taken to prevent `[WinError 32] PermissionError` on Windows by immediately closing file descriptors returned by `tempfile.mkstemp()`.

### Example: Safe Temporary File Creation

```python
import os
import tempfile
from typing import List, Dict, Any, Iterator

def setup_test_environment(content: str) -> str:
    """
    Creates a temporary log file for testing.
    
    Args:
        content: The string content to write to the file.
        
    Returns:
        The path to the created temporary file.
    """
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    # Immediately close the file descriptor to prevent WinError 32 on Windows
    os.close(fd)
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        os.remove(path)
        raise e
        
    return path

def evaluate_contract(
    log_stream: Iterator[Dict[str, Any]], 
    contract: List[str]
) -> Dict[str, Any]:
    """
    Pure state-machine function that consumes the log stream and a contract.
    
    Args:
        log_stream: Iterator yielding parsed log dictionaries.
        contract: List of required sequential actions.
        
    Returns:
        Dictionary containing compliance metrics and unauthorized actions.
    """
    metrics: Dict[str, Any] = {"compliant": True, "unauthorized": []}
    expected_idx = 0
    
    for entry in log_stream:
        action = entry.get("action")
        if expected_idx < len(contract) and action == contract[expected_idx]:
            expected_idx += 1
        else:
            metrics["compliant"] = False
            metrics["unauthorized"].append(action)
            
    return metrics