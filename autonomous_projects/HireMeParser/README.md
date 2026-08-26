# HireMeParser

Parse "Who wants to be hired?" Hacker News posts into structured JSON.

HireMeParser extracts and validates key information from job-seeking posts on Hacker News' monthly "Who wants to be hired?" threads. It converts unstructured text into standardized JSON, saving recruiters and job seekers time by automating parsing and validation.

## Features

- **Strict schema validation**: Enforces required fields with precise format checks
- **Pure function parser**: Accepts string input, returns dictionary output—no side effects
- **CLI tool**: Read from stdin or file, output clean JSON
- **100% test coverage**: Validated against real HN post examples
- **Zero dependencies**: Pure Python, no external packages required
- **Cross-platform**: Fully compatible with Windows, macOS, and Linux

## Installation

```bash
git clone https://github.com/yourusername/hiremeparser.git
cd hiremeparser
pip install -e .
```

Requires Python 3.7+. Install in development mode to enable CLI usage.

## Usage

### From stdin

```bash
echo "Location: Berlin, Germany
Remote: Yes
Willing to relocate: No
Technologies: Python, Docker, AWS
Résumé: https://example.com/resume.pdf
Email: dev@example.com" | python -m hireme.cli
```

### From file

```bash
python -m hireme.cli --input post.txt
```

### Output

Both methods produce standardized JSON:

```json
{
  "location": "Berlin, Germany",
  "remote": "Yes",
  "willing_to_relocate": "No",
  "technologies": "Python, Docker, AWS",
  "resume_cv": "https://example.com/resume.pdf",
  "email": "dev@example.com"
}
```

## How it Works

HireMeParser uses a two-step process:

1. **Extraction**: Pre-compiled regex patterns locate each required field in the input text, regardless of case or minor formatting variations (e.g., "Resume", "Résumé", or "CV").
2. **Validation**: Each extracted value undergoes strict checks:
   - All six fields must be present (`Location`, `Remote`, `Willing to relocate`, `Technologies`, `Résumé/CV`, `Email`)
   - Email must conform to RFC5322-lite specification
   - No field may be empty after whitespace trimming
   - Input must be a string

The parser normalizes field names to snake_case keys (`willing_to_relocate`, `resume_cv`) for consistent JSON output. The CLI handles I/O operations while the core parser remains pure and testable.

## Testing

Run the full test suite with:

```bash
pytest test_hireme.py -v
```

Tests include:
- Valid and invalid post parsing
- Edge cases (extra whitespace, missing fields)
- CLI behavior with files and stdin
- Error handling for malformed inputs

All tests use real-world HN post examples—no mocks or stubs.

## Schema

| Field                | Key                  | Requirements                          |
|----------------------|----------------------|---------------------------------------|
| Location             | `location`           | Non-empty string                      |
| Remote               | `remote`             | Non-empty string                      |
| Willing to relocate  | `willing_to_relocate`| Non-empty string                      |
| Technologies         | `technologies`       | Comma-separated list, non-empty       |
| Résumé/CV            | `resume_cv`          | URL or path, non-empty                |
| Email                | `email`              | Valid email format per RFC5322-lite   |

## License

MIT License