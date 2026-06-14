# Prompt Leak Analyzer

Detects and removes the *prompt‑leak* comments that LLM agents sometimes embed in generated source files.

## Installation
```bash
pip install .
```

## Usage
```python
from prompt_leak_analyzer.detector import detect, strip

code = """def foo():\n    # Prompt: use defaults\n    return 1\n"""

print(detect(code))   # [(2, '    # Prompt: use defaults')]
print(strip(code))    # clean code without the comment
```

## Testing
```bash
python -m unittest discover -v
```
