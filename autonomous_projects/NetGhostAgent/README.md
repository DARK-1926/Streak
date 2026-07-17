# NetGhostAgent

NetGhostAgent is a specialized network analysis tool designed to solve the "Router ARP/NAT contradict" problem. By deterministically parsing local syslog exports, it identifies "ghost clients"—devices that exhibit NAT translation activity without corresponding active DHCP leases or ARP table entries.

## How it Works

The system is built on a decoupled, highly testable architecture designed for performance and reliability:

*   **Pure Functional Core:** The core logic is split into the `parser` and `engine` modules, which operate entirely on iterables and primitives without side effects. The parser uses strict, compiled regular expressions to extract DHCP, ARP, and NAT events from raw syslog text. The engine acts as a chronological state machine, processing these events to detect state contradictions (e.g., NAT translations for IPs lacking active DHCP leases or ARP entries).
*   **Memory-Mapped I/O:** The `cli` module is completely decoupled from the core logic. It utilizes `mmap` for memory-efficient file reading, allowing it to stream parsed events into the engine without loading massive log files entirely into RAM. It includes explicit safeguards for handling empty files and ensures file descriptors are properly managed to prevent OS-level locking issues (such as `[WinError 32]` on win32).
*   **Strict TDD Validation:** The entire pipeline is validated by a comprehensive test suite. Tests inject raw strings and event lists to assert exact anomaly outputs, and utilize temporary filesystem fixtures to validate I/O and memory-mapping safety without relying on external mocks.

## Setup

To set up the development environment, follow these steps:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   * On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   * On Windows (win32):
     ```cmd
     venv\Scripts\activate
     ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the CLI tool against a syslog export file to detect anomalies:

```bash
python cli.py --logfile router.log
```

The tool will process the log file and output any detected ghost client anomalies as formatted JSON to standard output.

## Testing

Execute the strict TDD suite to validate the parser, engine, and CLI edge cases:

```bash
pytest test_main.py