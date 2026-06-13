# hn_summary

**hn_summary** is a tiny, zero‑dependency Python library that turns a raw Hacker News‑style feed into a readable summary. It:

- Parses the *Problem* / *Text* blocks you often copy‑paste from HN threads.
- Detects a few useful tags (AI, design, startup, etc.) using simple keyword heuristics.
- Groups posts by their primary tag and prints a concise markdown summary.

The project ships with a full pytest suite and a Windows batch script (`setup_and_test.bat`) that creates an isolated virtual environment, installs the only required package (`pytest`), and runs the tests.

## Usage
```python
from hn_summary.parser import parse_raw_feed, summarize_posts

raw = """Problem: Ask HN: How are thinking efforts implemented?\nText: Claude and ChatGPT ..."""
posts = parse_raw_feed(raw)
print(summarize_posts(posts))
```

## Development
Run the provided batch file:
```
setup_and_test.bat
```
It will report *All tests passed* if everything works.
