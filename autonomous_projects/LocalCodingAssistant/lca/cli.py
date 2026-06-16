```python
"""
lca.cli
=======

Command‑line interface for the Local Coding Assistant (LCA).

The module defines a top‑level ``click`` group ``lca`` with two sub‑commands:

* ``explain`` – Produce a plain‑English explanation of the supplied code.
* ``complete`` – Generate a continuation for the supplied code.

Both commands share a common set of options that can override values from
``config.yaml`` (located next to the package root).  The configuration file
has the following optional keys:

* ``model`` – Path to the LLM binary (e.g. ``models/ggml‑model‑q4_0.bin``).
* ``max_tokens`` – Maximum number of tokens to generate.
* ``temperature`` – Sampling temperature.

The commands instantiate :class:`lca.llm.LLMWrapper` with the resolved
settings and forward a handcrafted prompt to the LLM.  The LLM response is
written to standard output.

Error handling includes:

* Missing configuration file – falls back to built‑in defaults.
* Missing model file – prints a clear error message and exits with a non‑zero
  status code.
* Any unexpected exception – prints a concise traceback for debugging.

The module is deliberately self‑contained and relies only on the standard
library plus the third‑party ``click`` and ``pyyaml`` packages, which are
declared as runtime dependencies of the project.
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Any, Dict

import click
import yaml

from .llm import LLMWrapper

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #


def load_config() -> Dict[str, Any]:
    """
    Load configuration from ``config.yaml`` located at the repository root.

    Returns
    -------
    dict
        Configuration dictionary. Missing keys are simply omitted; callers
        provide defaults.
    """
    config_path = Path(__file__).resolve().parents[1] / "config.yaml"
    if not config_path.is_file():
        # No configuration file – return empty dict and let defaults apply.
        return {}
    try:
        with config_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as exc:
        click.echo(
            f"Warning: Failed to read configuration file '{config_path}': {exc}",
            err=True,
        )
        return {}


def resolve_option(
    cli_value: Any, config_key: str, config: Dict[str, Any], default: Any
) -> Any:
    """
    Resolve a setting value by priority:

    1. CLI option (if not ``None``)
    2. Configuration file entry (if present)
    3. Provided default.

    Parameters
    ----------
    cli_value
        Value supplied via the command line (or ``None``).
    config_key
        Key to look up in the configuration dictionary.
    config
        The loaded configuration dictionary.
    default
        Fallback value if neither CLI nor config provides a value.

    Returns
    -------
    The resolved value.
    """
    if cli_value is not None:
        return cli_value
    return config.get(config_key, default)


def instantiate_llm(
    model_path: Path, max_tokens: int, temperature: float
) -> LLMWrapper:
    """
    Create an :class:`LLMWrapper` instance after performing basic validation.

    Parameters
    ----------
    model_path
        Path to the compiled LLM binary.
    max_tokens
        Maximum tokens for generation.
    temperature
        Sampling temperature.

    Returns
    -------
    LLMWrapper
        Ready‑to‑use wrapper.

    Raises
    ------
    click.ClickException
        If the model file does not exist.
    """
    if not model_path.is_file():
        raise click.ClickException(
            f"Model file not found: '{model_path}'. Please provide a valid '--model' path."
        )
    return LLMWrapper(
        model_path=str(model_path),
        max_tokens=max_tokens,
        temperature=temperature,
    )


def handle_error(exc: Exception) -> None:
    """
    Print a user‑friendly error message and exit with a non‑zero status.

    Parameters
    ----------
    exc
        The exception that was caught.
    """
    click.echo(f"Error: {exc}", err=True)
    # In a production tool we might want a full traceback only when a debug flag is set.
    if isinstance(exc, click.ClickException):
        sys.exit(1)
    else:
        traceback.print_exc()
        sys.exit(1)


# --------------------------------------------------------------------------- #
# Click command group
# --------------------------------------------------------------------------- #


@click.group()
def lca() -> None:
    """
    Local Coding Assistant (LCA) – a privacy‑preserving, local LLM helper.

    Use the sub‑commands ``explain`` and ``complete`` to interact with the model.
    """
    pass


# --------------------------------------------------------------------------- #
# Sub‑commands
# --------------------------------------------------------------------------- #


@lca.command()
@click.argument("code", type=str)
@click.option(
    "--model",
    type=click.Path(exists=False, dir_okay=False, resolve_path=True),
    help="Path to the LLM binary. Overrides config.yaml.",
)
@click.option(
    "--max-tokens",
    type=int,
    help="Maximum number of tokens to generate. Overrides config.yaml.",
)
@click.option(
    "--temp",
    "temperature",
    type=float,
    help="Sampling temperature. Overrides config.yaml.",
)
def explain(
    code: str,
    model: str | None,
    max_tokens: int | None,
    temperature: float | None,
) -> None:
    """
    Explain the supplied CODE in plain English.

    The CODE argument is taken as a raw string; quoting is recommended when
    passing multi‑line snippets via the shell.
    """
    try:
        cfg = load_config()
        resolved_model = resolve_option(
            model, "model", cfg, default="models/ggml-model-q4_0.bin"
        )
        resolved_max = resolve_option(max_tokens, "max_tokens", cfg, default=256)
        resolved_temp = resolve_option(temperature, "temperature", cfg, default=0.7)

        model_path = Path(resolved_model).expanduser().resolve()
        llm = instantiate_llm(model_path, resolved_max, resolved_temp)

        prompt = (
            "Explain the following code in plain English:\n\n"
            f"{code}\n\nExplanation:"
        )
        response = llm.generate(prompt)
        click.echo(response.strip())
    except Exception as exc:
        handle_error(exc)


@lca.command()
@click.argument("code", type=str)
@click.option(
    "--model",
    type=click.Path(exists=False, dir_okay=False, resolve_path=True),
    help="Path to the LLM binary. Overrides config.yaml.",
)
@click.option(
    "--max-tokens",
    type=int,
    help="Maximum number of tokens to generate. Overrides config.yaml.",
)
@click.option(
    "--temp",
    "temperature",
    type=float,
    help="Sampling temperature. Overrides config.yaml.",
)
def complete(
    code: str,
    model: str | None,
    max_tokens: int | None,
    temperature: float | None,
) -> None:
    """
    Generate a continuation for the supplied CODE.

    The CODE argument is taken as a raw string; quoting is recommended when
    passing multi‑line snippets via the shell.
    """
    try:
        cfg = load_config()
        resolved_model = resolve_option(
            model, "model", cfg, default="models/ggml-model-q4_0.bin"
        )
        resolved_max = resolve_option(max_tokens, "max_tokens", cfg, default=256)
        resolved_temp = resolve_option(temperature, "temperature", cfg, default=0.7)

        model_path = Path(resolved_model).expanduser().resolve()
        llm = instantiate_llm(model_path, resolved_max, resolved_temp)

        prompt = (
            "Complete the following Python code:\n\n"
            f"{code}\n\nCompletion:"
        )
        response = llm.generate(prompt)
        click.echo(response.strip())
    except Exception as exc:
        handle_error(exc)


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    lca()
```