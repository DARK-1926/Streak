# LocalCodingAssistant (LCA)

## Project description and motivation
LocalCodingAssistant is a tiny, modular Python CLI that runs a **local** LLM (e.g., llama.cpp) to give instant code completions and explanations.  
It keeps your code private, works offline, and fits on consumer hardware without any cloud dependencies.

## Quick start
```bash
# 1. Install Python 3.10+
# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate

# 3. Install the tiny wrapper (only stdlib is required)
pip install -e .

# 4. Download a small GGML model (e.g., llama-7B-q4_0.ggml)
wget https://huggingface.co/ggml-org/llama-7b/resolve/main/ggml-model-q4_0.bin -O models/llama.ggml

# 5. Run the CLI
lca explain "def foo(): pass"
```

## Usage examples
```bash
# Explain a snippet
lca explain "def foo(): pass"

# Get a completion
lca complete "for i in range(10):"
```

## How it Works
The CLI parses user commands and forwards the request to **LLMWrapper**, which builds a prompt and invokes the **llama.cpp** binary via `subprocess`. The binary streams the model’s output back to the wrapper, which prints it to the console.

## Architecture overview
```
CLI (lca) ──► LLMWrapper (Python) ──► llama.cpp binary
```
* **CLI** – `argparse` based entry point (`lca` command).  
* **LLMWrapper** – thin Python class handling prompt creation, model path configuration, and subprocess I/O.  
* **llama.cpp** – compiled C++ inference engine that runs the GGML model locally.

## Extending the tool
* **New commands** – add a function in `lca/commands.py` and register it in `lca/__main__.py`.  
* **Swap model** – place a different GGML file in `models/` and update `LLMWrapper.model_path` via the `--model` flag.

## License
MIT © 2024 LocalCodingAssistant contributors.

## Contributing
Feel free to open issues or submit pull requests. Keep the codebase under eight files and avoid external dependencies.