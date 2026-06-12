# AI Front‑End Linter

A tiny **CLI** utility to quickly spot common problems in AI‑generated HTML/CSS snippets.

## Features
- Detect `<img>` tags missing an `alt` attribute.
- Find duplicate `id` attributes.
- Count usage of inline `style` attributes.
- Warn about deprecated tags (`<font>`, `<center>`, `<marquee>`).
- Works with local files **or** remote URLs (via `--url`).
- Optional JSON output for machine‑readable pipelines (`--json`).

## Installation
The script relies only on the Python standard library and the `requests` package.
```bash
pip install requests
```

## Usage
```bash
python main.py path/to/file.html          # lint a local file
python main.py https://example.com/page.html --url   # lint a remote page
python main.py file.html --json          # JSON output
```

## Example Output
```
Missing alt attributes on <img>: 2
Duplicate id attributes: header(2), nav(2)
Inline style attributes: 3
Deprecated tags (font, center, marquee): 1
```

## Testing
Run the bundled tests to ensure core logic works:
```bash
python run_tests.py
```

## Limitations
- Not a full HTML validator – it checks only the heuristics listed above.
- Relies on Python's built‑in `HTMLParser`, which may miss some malformed edge cases.
- Only detects a small set of deprecated tags; can be extended in `FrontEndLinter.deprecated_set`.
