# LocalCodingAssistant
A minimal, privacy‑first coding assistant that runs a quantized LLM locally and exposes autocomplete, documentation lookup, and refactor suggestions through a tiny HTTP API.

## Quick Start

```bash
# 1. Install Python (>=3.9) and git
sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip git   # Debian/Ubuntu
# or use your OS package manager / pyenv

# 2. Clone the repository
git clone https://github.com/yourname/LocalCodingAssistant.git
cd LocalCodingAssistant

# 3. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Download a quantized model (example using GGUF format)
#    Adjust the URL to the model you prefer.
mkdir -p models
curl -L -o models/phi-2-q4.gguf https://huggingface.co/quantized/phi-2/resolve/main/phi-2-q4.gguf

# 6. Run the server
python -m api

# 7. Test with curl
curl -X POST http://127.0.0.1:8000/v1/completions \
     -H "Content-Type: application/json" \
     -d '{"prompt":"def hello_world():", "max_tokens": 64}'
```

You should receive a JSON response with the generated completion.

## How it Works
The assistant loads a **quantized GGUF** model into memory using `model_loader.py`. The model is wrapped in a lightweight inference class that exposes a `generate` method. `api.py` creates a FastAPI server with three endpoints:

| Endpoint | Purpose |
|----------|---------|
| `/v1/completions` | Autocomplete / code generation |
| `/v1/doclookup`   | Retrieve doc‑strings for a given symbol |
| `/v1/refactor`    | Simple refactor suggestions (e.g., rename, extract method) |

Requests are forwarded to the model instance, and the results are returned as JSON. The server runs on CPU by default; if a compatible GPU is detected, the underlying `torch` backend will automatically use it.

## Architecture Overview

```
LocalCodingAssistant/
│
├─ model_loader.py   # Loads the quantized model, provides a singleton Model class
├─ api.py            # FastAPI app, defines HTTP endpoints
├─ cli.py            # Optional command‑line interface for quick testing
├─ requirements.txt  # Python dependencies
└─ README.md
```

* **model_loader.py** – Handles lazy loading, device selection, and tokenization. Exposes `Model.get_instance()` to retrieve the shared model object.
* **api.py** – Starts the FastAPI server (`uvicorn api:app`). Each endpoint validates input with Pydantic models and calls `Model.generate`.
* **cli.py** – Simple REPL for local experimentation without HTTP overhead.

## Extending the Assistant

### Adding New Endpoints
1. Open `api.py`.
2. Define a new Pydantic request/response model.
3. Add a FastAPI route decorator (`@app.post("/v1/your_endpoint")`).
4. Call the appropriate method on `Model.get_instance()` or implement custom logic.
5. Update `cli.py` if you want a command‑line shortcut.

### Swapping the Model
1. Replace the file in `models/` with another quantized GGUF (or any format supported by `torch`/`transformers`).
2. Edit `model_loader.py`:
   * Change `MODEL_PATH` constant.
   * Adjust `torch_dtype` or `device_map` if needed.
3. Restart the server – the new model will be loaded automatically.

## License
MIT License – see the `LICENSE` file for details.