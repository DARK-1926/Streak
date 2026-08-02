# ScrapeDefianceAuditor

## The Problem

Web crawlers and AI training bots, such as Amazonbot, are notorious for aggressive and deceptive scraping practices. A common pattern involves these bots requesting the `robots.txt` file—ostensibly to check crawling permissions—only to immediately proceed to scrape the exact paths explicitly marked as `Disallow`. 

This behavior wastes server resources, violates site policies, and compromises private data. Identifying these bad actors manually in massive, gigabyte-sized access logs is practically impossible. ScrapeDefianceAuditor was built to automatically detect and report this specific "scrape defiance" behavior.

## The Solution

ScrapeDefianceAuditor is a pure Python, zero-dependency CLI tool engineered to audit web server access logs against `robots.txt` rules. It pinpoints the exact IP addresses and User-Agents that fetch your rules but willfully ignore them.

## Architecture & Technical Constraints Solved

The tool is designed with strict performance and reliability constraints in mind:

*   **Zero External Dependencies:** Built entirely on the Python Standard Library. No `pip install` required beyond a standard Python 3.x environment.
*   **Win32-Safe Memory-Mapped File Processing:** Handles massive log files efficiently using `mmap` to avoid loading entire files into RAM. It includes specific safeguards for Windows environments, such as checking for empty files before mapping to prevent `mmap` exceptions, and ensuring file descriptors are managed correctly to avoid `[WinError 32] PermissionError` locks.
*   **Single-Pass O(N) State Accumulation:** Avoids memory traps by processing log lines in a single streaming pass. It maintains a lightweight, highly optimized state machine to track IP behavior over time without storing the entire log history in memory.
*   **Strict Dependency Injection:** The core auditing logic (`auditor.py`) is completely decoupled from file I/O. Functions accept generic iterables and return pure data structures, allowing for rigorous, fast unit testing using pure in-memory lists.

## How it Works

The auditor operates using a single-pass state machine that correlates IP behavior across the log stream:

1.  **Rule Compilation:** The tool first parses the provided `robots.txt` file. It extracts all `Disallow` directives and compiles them into optimized regular expressions anchored to the start of the path.
2.  **State Tracking:** As it streams through the access log (Combined Log Format), it monitors requests. If an IP address requests `/robots.txt`, it is flagged in the state machine's internal dictionary as "aware" of the crawling rules.
3.  **Defiance Detection:** For every subsequent request in the log, the tool checks if the requesting IP is flagged as "aware". If it is, the requested path is tested against the compiled `Disallow` regex patterns.
4.  **Reporting:** If an "aware" IP requests a disallowed path, the tool records the infraction. It captures the offending IP, the User-Agent, the timestamp, and the specific disallowed path accessed. 
5.  **Output:** After the single pass is complete, the tool outputs a structured JSON report detailing all defiant actors and their infractions.

## Project Structure

*   `auditor.py`: Contains pure functions for parsing `robots.txt` rules, parsing Combined Log Format lines, and the core O(N) state machine logic.
*   `cli.py`: The command-line interface. Handles argument parsing, win32-safe `mmap` file I/O, and JSON output formatting.
*   `test_main.py`: Comprehensive test suite using `unittest`. Tests core logic with in-memory lists and validates the CLI via `subprocess` integration tests.
*   `requirements.txt`: Empty (Standard Library only).
*   `.gitignore`: Standard Python ignores.

## Usage

Ensure you have Python 3.8+ installed. Run the CLI by providing the path to your access log and your `robots.txt` file:

```bash
python cli.py <path_to_access.log> <path_to_robots.txt>
```

### Example

```bash
python cli.py /var/log/nginx/access.log ./public/robots.txt
```

### Output

The tool will print a JSON object to `stdout` mapping offending IPs to their details and infractions:

```json
{
    "192.168.1.100": {
        "user_agent": "Amazonbot/0.1",
        "infractions": [
            "/private/data",
            "/admin/settings"
        ]
    }
}
```

## Testing

Run the test suite using the standard `unittest` module:

```bash
python -m unittest test_main.py
```

The tests utilize temporary files and strict file descriptor management to ensure they run cleanly across both POSIX and Windows environments.