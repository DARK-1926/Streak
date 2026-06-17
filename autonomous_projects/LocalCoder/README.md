# LocalCoder

**LocalCoder** is a lightweight, modular local coding assistant that runs a small language model directly on consumer hardware. It lets developers write, refactor, and debug code entirely offline, preserving privacy and eliminating cloud costs.

---

## How it Works

LocalCoder uses a 1.3 B parameter, quantized transformer model that runs on CPU or GPU (Apple Silicon, NVIDIA, or integrated GPUs). The model is loaded with the Hugging Face 🤗 `transformers` library and executed via a minimal inference engine. All prompts, code generation, and refactoring requests are processed locally, with no network traffic required after the initial model download.

---

## Quick Start

1. **Prerequisites**  
   - Python 3.10+  
   - pip

2. **Clone the repo**  
   ```bash
   git clone https://github.com/yourusername/LocalCoder.git
   cd LocalCoder
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the model checkpoint**  
   ```bash
   wget https://example.com/models/localcoder-1.3b-quantized.bin -O models/localcoder.bin
   ```

5. **Run the assistant**  
   ```bash
   python main.py
   ```

---

## Basic Usage

Once the assistant is running, you can interact via the command line:

```text
> Generate a Python function that calculates factorial
```

```text
> Refactor the following code to use list comprehensions
```

```text
> Add docstring to this function
```

The assistant will return the requested code snippet, refactored code, or updated documentation.

---

## Adding Custom Plugins

1. **Create a plugin file** in the `plugins/` directory.  
   ```python
   # plugins/hello.py
   def greet(name: str) -> str:
       return f"Hello, {name}!"
   ```

2. **Register the plugin** by adding its name to `config.yaml`:
   ```yaml
   plugins:
     - hello
   ```

3. **Use it in a prompt**:
   ```text
   > Use the greet plugin to say hello to Alice
   ```

The assistant will import the plugin and make its functions available in the prompt context.

---

## Performance Notes

- **Inference speed**: ~200 ms per token on an Apple M1 Max (CPU+Neural Engine).  
- **Memory usage**: ~1 GB for the 1.3 B quantized model.  
- **CPU/GPU**: Works on macOS, Linux, and Windows with or without a discrete GPU.

---

## Contribution Guidelines

1. Fork the repository and create a feature branch.  
2. Write tests for new functionality.  
3. Ensure `flake8` and `black` formatting passes.  
4. Submit a pull request with a clear description of the changes.

---

## License

MIT License. See `LICENSE` for details.

---

Happy coding with LocalCoder!