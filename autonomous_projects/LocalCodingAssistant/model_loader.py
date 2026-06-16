```python
"""
model_loader.py

Singleton wrapper for lazy loading of a quantized LLM and its tokenizer.
The implementation caches the model and tokenizer at module level so that
multiple instantiations of :class:`ModelLoader` across requests share the same
objects, avoiding costly re‑initialisation.

The default model is a GPTQ‑quantized Mistral 7B instruction tuned checkpoint.
It is loaded with ``torch.float16`` precision and an automatic device map,
allowing seamless fallback to CPU when a GPU is unavailable.

Typical usage::

    from model_loader import ModelLoader

    loader = ModelLoader()
    response = loader.generate("Write a Python function that adds two numbers.")
"""

from __future__ import annotations

import threading
import logging
from typing import Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

# --------------------------------------------------------------------------- #
# Module‑level caches – these survive across multiple ModelLoader instances.
# --------------------------------------------------------------------------- #
_model: Optional[AutoModelForCausalLM] = None
_tokenizer: Optional[AutoTokenizer] = None
_load_lock = threading.Lock()

# --------------------------------------------------------------------------- #
# Helper utilities
# --------------------------------------------------------------------------- #
_logger = logging.getLogger(__name__)
if not _logger.handlers:
    # Configure a very basic console logger if the host application hasn't.
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)


def _load_model_and_tokenizer(model_name: str) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """
    Load the model and tokenizer, handling common error scenarios.

    Parameters
    ----------
    model_name: str
        HuggingFace model identifier.

    Returns
    -------
    tuple[AutoModelForCausalLM, AutoTokenizer]
        The loaded model and tokenizer.

    Raises
    ------
    RuntimeError
        If the model or tokenizer cannot be loaded (e.g., missing files,
        incompatible torch version, or insufficient hardware).
    """
    global _model, _tokenizer

    try:
        _logger.info("Loading tokenizer for model '%s'...", model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load tokenizer for model '{model_name}'. Ensure the model name is correct "
            f"and that the repository contains a tokenizer configuration."
        ) from exc

    try:
        _logger.info(
            "Loading model '%s' with dtype=torch.float16 and device_map='auto'...", model_name
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load model '{model_name}'. This may be due to missing files, "
            f"incompatible quantization format, or insufficient hardware resources."
        ) from exc

    # Optional: set a default generation config to avoid repetitive arguments.
    model.generation_config = GenerationConfig(
        do_sample=True,
        temperature=0.7,
        top_p=0.95,
        repetition_penalty=1.0,
        pad_token_id=tokenizer.eos_token_id,
    )

    _model = model
    _tokenizer = tokenizer
    _logger.info("Model and tokenizer loaded successfully.")
    return model, tokenizer


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
class ModelLoader:
    """
    Singleton class responsible for lazy loading a quantized LLM and providing a
    simple ``generate`` interface.

    The class is deliberately lightweight; all heavy objects are stored as
    module‑level globals.  Instantiating the class multiple times does **not**
    trigger additional loads – the first instantiation performs the load,
    guarded by a thread‑safe lock.
    """

    _instance: Optional["ModelLoader"] = None
    _instance_lock = threading.Lock()

    def __new__(cls, model_name: str = "mistralai/Mistral-7B-Instruct-v0.2-GPTQ"):
        # Ensure a true singleton across the process.
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    _logger.debug("Creating a new ModelLoader singleton instance.")
                    cls._instance = super().__new__(cls)
                    cls._instance._model_name = model_name
        return cls._instance

    def __init__(self, model_name: str = "mistralai/Mistral-7B-Instruct-v0.2-GPTQ"):
        # ``__init__`` may be called multiple times due to the singleton pattern;
        # guard against re‑initialisation.
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._model_name = model_name

        # Lazy load – actual loading happens on first generate call.
        _logger.debug("ModelLoader initialized with model_name='%s'.", self._model_name)

    # --------------------------------------------------------------------- #
    # Private helpers
    # --------------------------------------------------------------------- #
    def _ensure_model(self) -> None:
        """
        Ensure that the global model and tokenizer are loaded.
        This method is thread‑safe and idempotent.
        """
        global _model, _tokenizer

        if _model is not None and _tokenizer is not None:
            _logger.debug("Model and tokenizer already loaded; skipping reload.")
            return

        _logger.debug("Acquiring load lock to initialize model/tokenizer.")
        with _load_lock:
            # Double‑check after acquiring the lock.
            if _model is None or _tokenizer is None:
                _logger.info("Model not loaded yet; invoking loader.")
                _load_model_and_tokenizer(self._model_name)
            else:
                _logger.debug("Model loaded by another thread while waiting for lock.")

    # --------------------------------------------------------------------- #
    # Public generation method
    # --------------------------------------------------------------------- #
    def generate(self, prompt: str, max_new_tokens: int = 128) -> str:
        """
        Generate a continuation for ``prompt`` using the loaded LLM.

        Parameters
        ----------
        prompt: str
            The input text to which the model should respond.
        max_new_tokens: int, optional
            Upper bound on the number of tokens to generate (default: 128).

        Returns
        -------
        str
            The generated text **without** the original prompt.

        Raises
        ------
        RuntimeError
            If generation fails due to model loading issues or runtime errors.
        """
        self._ensure_model()

        if _model is None or _tokenizer is None:
            raise RuntimeError("Model or tokenizer failed to load; cannot generate text.")

        try:
            _logger.debug("Encoding prompt for generation.")
            inputs = _tokenizer(prompt, return_tensors="pt")
            inputs = {k: v.to(_model.device) for k, v in inputs.items()}

            _logger.debug(
                "Running generation (max_new_tokens=%d) on device %s.",
                max_new_tokens,
                _model.device,
            )
            output_ids = _model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                **(_model.generation_config.to_dict() if hasattr(_model, "generation_config") else {}),
            )
            generated_text = _tokenizer.decode(output_ids[0], skip_special_tokens=True)

            # Strip the original prompt – some models repeat it verbatim.
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt) :].lstrip()

            _logger.debug("Generation completed successfully.")
            return generated_text
        except Exception as exc:
            _logger.exception("An error occurred during text generation.")
            raise RuntimeError("Failed to generate text with the loaded model.") from exc


__all__ = ["ModelLoader"]
```