```python
"""
api.py
-------

Flask HTTP API for the LocalCodingAssistant project.

Provides:
- POST /complete : Generate code completions using the singleton ModelLoader.
- GET  /health   : Simple health check endpoint.

The module exports the Flask ``app`` instance for external import and can be run
directly as a development server.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from flask import Flask, jsonify, request

# The ModelLoader is expected to be defined in the same package.
# Import lazily to avoid heavy initialization at import time.
try:
    from .model_loader import ModelLoader  # type: ignore
except Exception as exc:  # pragma: no cover
    # If the import fails we still want the module to be importable so that
    # the health endpoint can be queried. The error will be surfaced when
    # a request tries to use the model.
    ModelLoader = None  # type: ignore
    logging.getLogger(__name__).warning(
        "ModelLoader could not be imported: %s", exc
    )

# --------------------------------------------------------------------------- #
# Flask application setup
# --------------------------------------------------------------------------- #

app = Flask(__name__)

# Configure a basic logger for the module
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


# --------------------------------------------------------------------------- #
# Helper utilities
# --------------------------------------------------------------------------- #

def _get_model_loader() -> "ModelLoader":
    """
    Retrieve the singleton ModelLoader instance.

    Raises:
        RuntimeError: If the ModelLoader could not be imported or instantiated.
    """
    if ModelLoader is None:
        raise RuntimeError("ModelLoader is unavailable.")
    return ModelLoader.get_instance()


def _validate_complete_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the incoming JSON payload for the /complete endpoint.

    Expected keys:
        - prompt (str): The text prompt to complete.
        - max_tokens (int, optional): Maximum number of tokens to generate.

    Returns a sanitized dictionary with defaults applied.

    Raises:
        ValueError: If validation fails.
    """
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a JSON object.")

    if "prompt" not in payload:
        raise ValueError("Missing required field: 'prompt'.")

    prompt = payload["prompt"]
    if not isinstance(prompt, str):
        raise ValueError("'prompt' must be a string.")

    max_tokens = payload.get("max_tokens", 128)
    if not isinstance(max_tokens, int) or max_tokens <= 0:
        raise ValueError("'max_tokens' must be a positive integer.")

    return {"prompt": prompt, "max_tokens": max_tokens}


# --------------------------------------------------------------------------- #
# Route definitions
# --------------------------------------------------------------------------- #

@app.route("/complete", methods=["POST"])
def complete() -> Any:
    """
    Generate a completion for the supplied prompt.

    Expected JSON body:
        {
            "prompt": "...",
            "max_tokens": 128
        }

    Returns:
        JSON response with the generated completion:
        {
            "completion": "..."
        }

    Errors:
        - 400: Invalid request payload.
        - 500: Internal server error while generating the completion.
    """
    try:
        payload = request.get_json(force=True)
        logger.debug("Received /complete payload: %s", payload)
        data = _validate_complete_payload(payload)
    except Exception as exc:
        logger.warning("Invalid request payload: %s", exc)
        return jsonify({"error": str(exc)}), 400

    try:
        model = _get_model_loader()
        logger.info("Generating completion for prompt of length %d", len(data["prompt"]))
        completion = model.generate(
            prompt=data["prompt"],
            max_tokens=data["max_tokens"]
        )
        logger.debug("Generated completion: %s", completion)
        return jsonify({"completion": completion})
    except Exception as exc:
        logger.exception("Error during generation")
        return jsonify({"error": f"Generation failed: {str(exc)}"}), 500


@app.route("/health", methods=["GET"])
def health() -> Any:
    """
    Simple health check endpoint.

    Returns:
        JSON response indicating service status.
    """
    return jsonify({"status": "ok"})


# --------------------------------------------------------------------------- #
# Application entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Running directly for development / debugging purposes.
    # In production, a WSGI server (e.g., gunicorn) should import ``app``.
    app.run(host="0.0.0.0", port=5000, debug=False)
```