# SpecPIIAuditor

**Detect potential PII leakage in agentic tool output schemas—before it ships.**

SpecPIIAuditor is a lightweight, zero-dependency static analyzer that checks whether your LLM agent's declared output schema could inadvertently expose personally identifiable information (PII). By scanning field names against a customizable policy of regex patterns, it helps you catch privacy risks early in development.

---

## 🚀 Quick Start

```bash
# Audit a tool spec against a PII policy
python src/spec_pii_auditor/cli.py \
  --tool-spec examples/user_tool.json \
  --pii-policy examples/pii_policy.json
```

Example output:
```json
{
  "is_compliant": false,
  "flagged_fields": ["user_email", "home_address"],
  "total_fields": 4
}
```

---

## 🔍 How It Works

SpecPIIAuditor performs **static analysis only**—it never executes your code or inspects runtime data. Instead, it:

1. **Loads** a tool specification (JSON) containing an `output_schema` (e.g., `{"email": "string", "name": "string"}`).
2. **Loads** a PII policy (JSON list of regex strings, e.g., `[".*email.*", ".*ssn.*", "(?i)phone"]`).
3. **Matches** each field name in the schema against every regex in the policy using `re.search`.
4. **Reports** compliance status, flagged fields, and total field count via a structured `PIIAuditReport`.

Key design principles:
- **Pure functions**: Core logic (`audit_tool_spec_for_pii`) has no side effects.
- **Case-sensitive by default**: Use `(?i)` in regex for case-insensitive matching.
- **Graceful degradation**: Malformed specs or missing `output_schema` are treated as empty (0 fields).
- **Safe I/O**: CLI validates file existence and non-zero size before reading (Win32-safe).

---

## 📁 Architecture

```
src/
├── spec_pii_auditor/
│   ├── __init__.py      # Package metadata
│   ├── core.py          # Pure analyzer + PIIAuditReport dataclass
│   └── cli.py           # File loading + argument parsing
tests/
├── test_core.py         # 100% coverage of audit logic
└── test_cli.py          # Full I/O and error handling tests
```

- **`core.py`**: Contains all business logic. Fully testable with plain dicts.
- **`cli.py`**: Handles filesystem I/O and CLI args. No external dependencies.

---

## 🛠️ Usage

### CLI Interface
```bash
usage: cli.py [-h] --tool-spec TOOL_SPEC --pii-policy PII_POLICY

Options:
  --tool-spec FILE      Path to tool spec JSON (must contain "output_schema")
  --pii-policy FILE     Path to PII policy JSON (list of regex strings)
```

### Policy Format (`pii_policy.json`)
```json
[
  ".*email.*",
  ".*ssn.*",
  ".*address.*",
  "(?i)phone.*"
]
```
> 💡 Regexes are applied as-is with `re.search`. Anchor with `^...$` if needed.

### Tool Spec Format (`tool.json`)
```json
{
  "name": "get_user_profile",
  "output_schema": {
    "user_email": "string",
    "display_name": "string",
    "home_address": "string"
  }
}
```

---

## ✅ Testing Strategy

- **100% unit test coverage** of core logic using real-world tool specs.
- **No mocking**: Tests pass raw dicts to pure functions and assert dataclass equality.
- **CLI robustness**: Validates edge cases (empty files, invalid JSON, missing keys).
- **Cross-platform**: Uses `pathlib` and avoids OS-specific assumptions.

Run tests with:
```bash
python -m pytest tests/ -v
```

---

## 🌐 Compatibility

- **Python**: 3.8+
- **OS**: Windows, macOS, Linux (Win32-safe file handling)
- **Dependencies**: None (stdlib only)

No `requirements.txt` needed—just clone and run!

---

## 📜 License

MIT License. See `LICENSE` for details.