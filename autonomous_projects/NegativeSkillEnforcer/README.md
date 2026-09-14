# NegativeSkillEnforcer

**Statically verify that agent skill modules enforce declared negative capabilities.**

Autonomous agents often claim ethical boundaries (e.g., "I won’t scrape social media"), but these claims are unverifiable and easily bypassed by prompt injection or code drift. **NegativeSkillEnforcer** solves this by providing a static analysis tool that proves—via Abstract Syntax Tree (AST) inspection—that an agent’s code *cannot* perform forbidden actions because it explicitly raises the required exception.

No runtime, no mocks, no ambiguity: if the function exists and raises the correct exception as specified, the agent is compliant. Otherwise, violations are reported with precision.

---

## Features

- ✅ **Zero dependencies**: Pure Python standard library.
- ✅ **Deterministic verification**: Uses AST parsing—no execution, no side effects.
- ✅ **Mock-free testing**: Unit tests use real source strings and dataclass equality.
- ✅ **Precise violation reporting**: Identifies missing functions and incorrect exceptions.
- ✅ **Simple contract model**: JSON spec maps function names to expected exception class names (e.g., `"PermissionError"`).
- ✅ **CLI-ready**: Validate any skill module against a spec from the command line.

---

## How It Works

1. **Define a negative skill spec** (`negative_skills.json`):  
   Declare which functions are *forbidden* and what exception they **must** raise:
   ```json
   {
     "forbidden_functions": {
       "scrape_twitter": "PermissionError",
       "access_private_data": "OSError"
     }
   }
   ```

2. **Implement the skill module** (`agent.py`):  
   Each forbidden function must exist and immediately raise the specified exception:
   ```python
   def scrape_twitter():
       raise PermissionError("Scraping social media is not permitted.")

   def access_private_data():
       raise OSError("Access to private data is restricted.")
   ```

3. **Run static enforcement**:  
   `NegativeSkillEnforcer` parses both files using the AST and verifies:
   - Every function in `forbidden_functions` is **defined** in the skill source.
   - Each defined function **raises exactly** the expected exception type via:
     - `raise PermissionError()` (call), or
     - `raise PermissionError` (bare name).  
     *(Attribute access like `raise errors.PermissionError` is **not supported**.)*

4. **Get a clear report**:  
   Violations are categorized as:
   - `missing_functions`: Declared but not implemented.
   - `incorrect_exceptions`: Implemented but raises wrong or no exception.

---

## Architecture

- **`spec.py`**: Loads and validates the negative skill specification (JSON → `NegativeSkillSpec`).
- **`ast_analyzer.py`**: Parses Python source into AST and checks exception-raising patterns.
- **`enforcer.py`**: Core logic that compares spec against skill source and generates `EnforcementReport`.
- **`cli.py`**: Command-line interface for end-to-end validation.

All components are pure functions with explicit inputs/outputs—no global state, no I/O in core logic.

---

## Usage

Install the package (editable mode recommended):

```bash
pip install -e .
```

Validate a skill module:

```bash
python -m negative_skill_enforcer.cli \
  --skill-file agent.py \
  --spec-file negative_skills.json
```

The CLI outputs a JSON report to stdout and exits with:
- `0` if **no violations**,
- `1` if input files are invalid/missing,
- `2` if **violations are found**.

Example output (on violation):
```json
{
  "missing_functions": ["scrape_instagram"],
  "incorrect_exceptions": ["scrape_twitter"]
}
```

---

## Limitations

- Only **top-level function definitions** are checked (no methods, nested functions).
- Exception names must be **simple identifiers** (e.g., `ValueError`), **not dotted paths** (e.g., `mylib.errors.CustomError`).
- The `raise` statement must be **directly in the function body** or within control flow (e.g., inside `try`/`if`)—but must still reference the bare exception name.

---

## Testing

The test suite (`tests/test_enforcer.py`) uses **real Python source strings** and asserts exact `EnforcementReport` contents. No mocks, no filesystem I/O—just deterministic unit tests.

Run tests with:
```bash
pytest
```

---

## Why This Matters

In an era of agentic AI, **trust must be verifiable**. NegativeSkillEnforcer provides a lightweight, auditable mechanism to ensure agents *structurally cannot* perform harmful actions—not just because they say so, but because their code enforces it at the language level.