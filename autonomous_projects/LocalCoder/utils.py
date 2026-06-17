import os
import time
from functools import wraps
from typing import Callable, Any

__all__ = [
    "read_file",
    "write_file",
    "measure_latency",
    "sanitize_prompt",
    "format_response",
]


def read_file(path: str) -> str:
    """
    Read the entire contents of a file and return it as a string.

    Parameters
    ----------
    path : str
        The filesystem path to the file to read.

    Returns
    -------
    str
        The content of the file.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    PermissionError
        If the file cannot be accessed due to permissions.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No such file: '{path}'")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    """
    Write a string to a file, creating any missing directories.

    Parameters
    ----------
    path : str
        The filesystem path where the content should be written.
    content : str
        The string to write to the file.

    Raises
    ------
    OSError
        If the file cannot be written due to filesystem errors.
    """
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def measure_latency(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that measures and prints the execution time of a function.

    The decorator prints the elapsed time in milliseconds to stdout.

    Parameters
    ----------
    func : Callable
        The function to wrap.

    Returns
    -------
    Callable
        The wrapped function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        elapsed_ms = (end - start) * 1000
        print(f"[Latency] {func.__name__} took {elapsed_ms:.2f} ms")
        return result
    return wrapper


def sanitize_prompt(prompt: str) -> str:
    """
    Clean a prompt string by removing newlines and collapsing multiple spaces.

    Parameters
    ----------
    prompt : str
        The raw prompt string.

    Returns
    -------
    str
        A sanitized prompt with single spaces and no leading/trailing whitespace.
    """
    # Replace newlines and tabs with a single space
    cleaned = " ".join(prompt.split())
    return cleaned.strip()


def format_response(response: str) -> str:
    """
    Prepare a code response for display or further processing.

    This function trims trailing whitespace, ensures the response is wrapped in a
    Markdown code block with a language hint if it looks like code, and removes
    any leading/trailing blank lines.

    Parameters
    ----------
    response : str
        The raw response string.

    Returns
    -------
    str
        The formatted response string.
    """
    # Strip trailing spaces and leading/trailing blank lines
    cleaned = "\n".join(line.rstrip() for line in response.strip().splitlines())
    # Detect if the response starts with typical code indicators
    code_indicators = ("def ", "class ", "import ", "return ", "if ", "for ", "while ", "try ", "except ")
    if any(cleaned.startswith(ind) for ind in code_indicators):
        # Wrap in a Python code block
        return f"```python\n{cleaned}\n```"
    # If not code, just return the cleaned text
    return cleaned