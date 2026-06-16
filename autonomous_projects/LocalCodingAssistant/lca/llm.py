"""llm.py - Lightweight wrapper for llama.cpp binary.

This module provides a simple Python interface to invoke a local LLM
binary (e.g., the `llama.cpp` executable) with a prompt and retrieve the
generated text. It is deliberately minimal: only the standard library
is used, and the wrapper handles command construction, execution,
timeout handling, and error reporting.

Typical usage::

    from lca.llm import LLMWrapper, LLMError

    wrapper = LLMWrapper(
        model_path="models/llama-7b.ggmlv3.q4_0.bin",
        binary_path="/usr/local/bin/llama.cpp",
        max_tokens=128,
        temperature=0.7,
    )

    try:
        response = wrapper.query("Explain the quicksort algorithm.")
        print(response)
    except LLMError as exc:
        print(f"LLM invocation failed: {exc}")

The wrapper is intentionally synchronous and blocks until the binary
finishes or the configured timeout (30 seconds) expires.
"""

import subprocess
import shlex
from typing import List


class LLMError(RuntimeError):
    """Exception raised when the LLM binary fails or times out."""

    def __init__(self, message: str, returncode: int | None = None):
        super().__init__(message)
        self.returncode = returncode


class LLMWrapper:
    """
    A thin Python wrapper around a llama.cpp binary.

    Parameters
    ----------
    model_path: str
        Filesystem path to the GGML model file.
    binary_path: str
        Path to the compiled llama.cpp executable.
    max_tokens: int, default 128
        Maximum number of tokens the model may generate.
    temperature: float, default 0.7
        Sampling temperature; higher values produce more diverse output.
    """

    def __init__(
        self,
        model_path: str,
        binary_path: str,
        max_tokens: int = 128,
        temperature: float = 0.7,
    ) -> None:
        self.model_path = model_path
        self.binary_path = binary_path
        self.max_tokens = max_tokens
        self.temperature = temperature

    def _run(self, prompt: str) -> str:
        """
        Execute the LLM binary with the supplied prompt.

        The command constructed mirrors the typical llama.cpp CLI:

        ``[binary_path, '-m', model_path, '--prompt', prompt,
        '--temp', str(temperature), '--n_predict', str(max_tokens)]``

        Returns
        -------
        str
            The trimmed standard output from the binary.

        Raises
        ------
        LLMError
            If the subprocess exits with a non‑zero status or exceeds the
            30‑second timeout.
        """
        # Build the command list safely; shlex.quote is used for logging only.
        cmd: List[str] = [
            self.binary_path,
            "-m",
            self.model_path,
            "--prompt",
            prompt,
            "--temp",
            str(self.temperature),
            "--n_predict",
            str(self.max_tokens),
        ]

        # Debug representation (not printed in production, but kept for
        # potential future logging extensions).
        _ = " ".join(shlex.quote(part) for part in cmd)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise LLMError(
                f"LLM invocation timed out after 30 seconds: {exc}",
                returncode=None,
            ) from exc
        except OSError as exc:
            raise LLMError(f"Failed to start LLM binary: {exc}", returncode=None) from exc

        if result.returncode != 0:
            raise LLMError(
                f"LLM binary exited with non‑zero status {result.returncode}: {result.stderr.strip()}",
                returncode=result.returncode,
            )

        return result.stdout.strip()

    def query(self, prompt: str) -> str:
        """
        Public API to send a prompt to the LLM and obtain a response.

        Parameters
        ----------
        prompt: str
            The text prompt to feed into the model.

        Returns
        -------
        str
            The model's generated completion.

        Raises
        ------
        LLMError
            Propagated from the underlying `_run` method.
        """
        return self._run(prompt)```python
    async def arun(self, prompt: str) -> str:
        """
        Asynchronously run the model on the given prompt.

        Parameters
        ----------
        prompt : str
            The text prompt to feed into the model.

        Returns
        -------
        str
            The model's generated completion.

        Raises
        ------
        LLMError
            Propagated from the underlying ``_arun`` method.
        """
        return await self._arun(prompt)

    def __call__(self, prompt: str) -> str:
        """
        Syntactic sugar to allow the LLM instance to be called directly.

        Parameters
        ----------
        prompt : str
            The text prompt.

        Returns
        -------
        str
            The model's generated completion.
        """
        return self.run(prompt)

    async def __acall__(self, prompt: str) -> str:
        """
        Asynchronous call operator.

        Parameters
        ----------
        prompt : str
            The text prompt.

        Returns
        -------
        str
            The model's generated completion.
        """
        return await self.arun(prompt)


class OpenAIChatLLM(LLM):
    """
    Concrete implementation of :class:`LLM` that wraps OpenAI's ChatCompletion API.
    """

    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        **client_kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        model : str, optional
            Identifier of the OpenAI model to use, by default ``"gpt-3.5-turbo"``.
        temperature : float, optional
            Sampling temperature, by default ``0.7``.
        max_tokens : int, optional
            Maximum number of tokens to generate. If ``None``, the API default is used.
        api_key : str, optional
            OpenAI API key. If omitted, the library will fall back to environment variables.
        client_kwargs : dict
            Additional keyword arguments passed to ``openai.ChatCompletion``.
        """
        try:
            import openai
        except ImportError as exc:
            raise ImportError(
                "OpenAI package is required for OpenAIChatLLM. Install it via "
                "`pip install openai`."
            ) from exc

        self._openai = openai
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key
        self.client_kwargs = client_kwargs

        if self.api_key:
            self._openai.api_key = self.api_key

    def _run(self, prompt: str) -> str:
        """
        Synchronous request to OpenAI's ChatCompletion endpoint.

        Parameters
        ----------
        prompt : str
            The user message to send.

        Returns
        -------
        str
            The assistant's reply.

        Raises
        ------
        LLMError
            If the request fails or the response format is unexpected.
        """
        try:
            response = self._openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **self.client_kwargs,
            )
            # The API returns a list of choices; we take the first.
            choice = response.choices[0]
            return choice.message["content"]
        except Exception as exc:
            raise LLMError(f"OpenAIChatLLM failed: {exc}") from exc

    async def _arun(self, prompt: str) -> str:
        """
        Asynchronous request to OpenAI's ChatCompletion endpoint.

        Parameters
        ----------
        prompt : str
            The user message to send.

        Returns
        -------
        str
            The assistant's reply.

        Raises
        ------
        LLMError
            If the request fails or the response format is unexpected.
        """
        # OpenAI's Python SDK does not provide native async methods.
        # We therefore run the synchronous call in a thread pool.
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._run, prompt)


class DummyLLM(LLM):
    """
    A minimal in‑memory LLM used for testing and documentation examples.
    It simply echoes the prompt with a configurable prefix.
    """

    def __init__(self, prefix: str = "Echo: ") -> None:
        """
        Parameters
        ----------
        prefix : str, optional
            Text to prepend to the echoed prompt.
        """
        self.prefix = prefix

    def _run(self, prompt: str) -> str:
        return f"{self.prefix}{prompt}"

    async def _arun(self, prompt: str) -> str:
        # No I/O here, but keep the async signature for compatibility.
        return self._run(prompt)


# ----------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------


def load_llm_from_config(config: Mapping[str, Any]) -> LLM:
    """
    Factory that instantiates an :class:`LLM` subclass based on a configuration mapping.

    The configuration must contain a ``type`` key indicating which concrete class to use.
    Supported types are ``"openai_chat"`` and ``"dummy"``.

    Parameters
    ----------
    config : Mapping[str, Any]
        Configuration dictionary.

    Returns
    -------
    LLM
        An instantiated LLM object.

    Raises
    ------
    ValueError
        If the ``type`` is unknown or required parameters are missing.
    """
    llm_type = config.get("type")
    if llm_type == "openai_chat":
        return OpenAIChatLLM(
            model=config.get("model", "gpt-3.5-turbo"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens"),
            api_key=config.get("api_key"),
            **config.get("client_kwargs", {}),
        )
    elif llm_type == "dummy":
        return DummyLLM(prefix=config.get("prefix", "Echo: "))
    else:
        raise ValueError(f"Unsupported LLM type: {llm_type!r}")


# ----------------------------------------------------------------------
# Exported symbols
# ----------------------------------------------------------------------
__all__ = [
    "LLM",
    "LLMError",
    "OpenAIChatLLM",
    "DummyLLM",
    "load_llm_from_config",
]