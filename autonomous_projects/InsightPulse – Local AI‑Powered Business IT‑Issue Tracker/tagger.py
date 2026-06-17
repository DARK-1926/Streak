import os
import sys
import logging
from typing import List

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

# Configure logging for the module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s - %(message)s")
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

# Global caches for model and tokenizer
_MODEL = None
_TOKENIZER = None
_DEVICE = None

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models")


def _load_model_and_tokenizer() -> None:
    """Load the transformer model and tokenizer into module‑level globals."""
    global _MODEL, _TOKENIZER, _DEVICE

    if _MODEL is not None and _TOKENIZER is not None:
        return  # Already loaded

    if not os.path.isdir(_MODEL_PATH):
        logger.error(f"Model directory not found at '{_MODEL_PATH}'.")
        raise FileNotFoundError(f"Model directory not found at '{_MODEL_PATH}'")

    # Determine device and dtype
    if torch.cuda.is_available():
        _DEVICE = torch.device("cuda")
        dtype = torch.float16
        logger.info("CUDA detected – loading model on GPU with float16.")
    else:
        _DEVICE = torch.device("cpu")
        dtype = torch.float32
        logger.info("CUDA not available – loading model on CPU.")

    try:
        _TOKENIZER = AutoTokenizer.from_pretrained(_MODEL_PATH)
        _MODEL = AutoModelForCausalLM.from_pretrained(
            _MODEL_PATH,
            torch_dtype=dtype,
            low_cpu_mem_usage=True,
        ).to(_DEVICE)
        _MODEL.eval()
        logger.info("Model and tokenizer loaded successfully.")
    except Exception as exc:
        logger.exception("Failed to load model or tokenizer.")
        raise RuntimeError("Could not load the transformer model.") from exc


_SYSTEM_PROMPT = (
    "You are an expert IT incident analyst. Extract up to five short keyword tags "
    "(lowercase, hyphenated if needed) that best describe the root cause and "
    "affected component of the following incident description. Return tags as a "
    "comma-separated list."
)


def _build_prompt(user_text: str) -> str:
    """Combine system prompt and user text into a single prompt for generation."""
    # Ensure there is a clear separation; using a newline is simple and works for most LLMs.
    return f"{_SYSTEM_PROMPT}\n\nIncident: {user_text.strip()}\nTags:"


def _postprocess(raw_output: str) -> str:
    """
    Clean the raw generation output.

    Steps:
    1. Take everything up to the first newline (model stop token).
    2. Strip whitespace.
    3. Lower‑case.
    4. Replace internal spaces with hyphens.
    5. Ensure tags are comma‑separated without trailing commas.
    """
    # Stop at first newline if present
    first_line = raw_output.split("\n", 1)[0]
    cleaned = first_line.strip().lower()
    # Replace spaces inside each tag with hyphens
    tags = [tag.strip().replace(" ", "-") for tag in cleaned.split(",") if tag.strip()]
    return ", ".join(tags)


def generate_tags(text: str) -> str:
    """
    Generate up to five keyword tags for an IT incident description.

    Parameters
    ----------
    text: str
        The raw incident description.

    Returns
    -------
    str
        A comma‑separated list of tags, or "unclassified" on failure.
    """
    if not isinstance(text, str) or not text.strip():
        logger.warning("Empty or non‑string input received; returning 'unclassified'.")
        return "unclassified"

    try:
        _load_model_and_tokenizer()
    except Exception:
        return "unclassified"

    prompt = _build_prompt(text)
    try:
        input_ids = _TOKENIZER.encode(prompt, return_tensors="pt").to(_DEVICE)

        # Generation configuration
        gen_cfg = GenerationConfig(
            max_new_tokens=30,
            temperature=0.2,
            do_sample=False,
            eos_token_id=_TOKENIZER.eos_token_id,
            pad_token_id=_TOKENIZER.pad_token_id,
        )

        with torch.no_grad():
            output_ids = _MODEL.generate(
                input_ids,
                generation_config=gen_cfg,
                # Stop generation when a newline appears; we handle it in post‑process.
                # Using `stopping_criteria` would require a custom class; newline handling
                # is simpler after generation.
            )
        # Decode only the newly generated portion
        generated_text = _TOKENIZER.decode(output_ids[0][input_ids.shape[-1] :], skip_special_tokens=True)
        tags = _postprocess(generated_text)
        return tags if tags else "unclassified"
    except Exception as exc:
        logger.exception("Tag generation failed.")
        return "unclassified"


if __name__ == "__main__":
    # Simple demo when the module is executed directly.
    sample_incident = (
        "Users report intermittent connectivity loss to the corporate VPN after the recent "
        "firewall firmware upgrade. The issue appears to affect the East Coast office more "
        "severely, with authentication timeouts observed in the logs."
    )
    print("Incident description:")
    print(sample_incident)
    print("\nGenerated tags:")
    print(generate_tags(sample_incident))