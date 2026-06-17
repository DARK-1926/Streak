import os
import re
from typing import Generator, Optional

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextIteratorStreamer,
)

# Global cache for the tokenizer and model to avoid reloading
_tokenizer: Optional[AutoTokenizer] = None
_model: Optional[AutoModelForCausalLM] = None

# Disallowed words for a simple safety filter
DISALLOWED_WORDS = {"kill", "bomb", "murder", "explosion", "weapon"}
REFUSAL_MESSAGE = (
    "I’m sorry, but I can’t comply with that request."
)

def load_model() -> AutoModelForCausalLM:
    """
    Load the causal language model from the local cache or download it if missing.

    The model is loaded with half‑precision weights (float16) and automatically
    mapped to available devices. The tokenizer is also loaded and cached globally.

    Returns:
        AutoModelForCausalLM: The loaded language model.
    """
    global _model, _tokenizer

    if _model is not None and _tokenizer is not None:
        return _model

    # Ensure the cache directory exists
    cache_dir = os.path.join(os.getcwd(), "model_cache")
    os.makedirs(cache_dir, exist_ok=True)

    # Load the tokenizer first to cache it globally
    _tokenizer = AutoTokenizer.from_pretrained(
        "meta-llama/Llama-2-7b-chat-hf",
        cache_dir=cache_dir,
        use_fast=True,
    )

    # Load the model with half precision and automatic device mapping
    _model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-2-7b-chat-hf",
        cache_dir=cache_dir,
        torch_dtype=torch.float16,
        device_map="auto",
    )

    return _model

def _safety_filter(prompt: str) -> bool:
    """
    Check if the prompt contains any disallowed words.

    Args:
        prompt (str): The user prompt.

    Returns:
        bool: True if the prompt is safe, False otherwise.
    """
    prompt_lower = prompt.lower()
    return any(word in prompt_lower for word in DISALLOWED_WORDS)

def generate(
    prompt: str,
    stream: bool = True,
    max_new_tokens: int = 256,
) -> Generator[str, None, None]:
    """
    Generate text from the loaded language model.

    Args:
        prompt (str): The input prompt to generate from.
        stream (bool, optional): If True, yields tokens as they are generated.
                                 If False, yields a single string containing the
                                 entire generated text. Defaults to True.
        max_new_tokens (int, optional): Maximum number of tokens to generate.
                                        Defaults to 256.

    Yields:
        str: Generated tokens or the full generated text.
    """
    # Ensure the model and tokenizer are loaded
    if _model is None or _tokenizer is None:
        load_model()

    # Safety filter
    if _safety_filter(prompt):
        def refusal_generator() -> Generator[str, None, None]:
            yield REFUSAL_MESSAGE
        return refusal_generator()

    # Encode the prompt
    input_ids = _tokenizer.encode(prompt, return_tensors="pt")
    input_ids = input_ids.to(_model.device)

    if stream:
        # Use TextIteratorStreamer for streaming output
        streamer = TextIteratorStreamer(
            _tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )
        # Generate in the same thread; the streamer yields tokens as they are produced
        _model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            streamer=streamer,
        )
        for token in streamer:
            yield token
    else:
        # Generate all tokens at once
        output_ids = _model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
        )
        # Decode the entire output
        decoded = _tokenizer.decode(
            output_ids[0],
            skip_special_tokens=True,
        )
        yield decoded

__all__ = ["load_model", "generate"]