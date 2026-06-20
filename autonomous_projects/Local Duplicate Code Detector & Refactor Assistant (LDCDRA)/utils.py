import os
import hashlib
import logging
import re

def read_file(path: str) -> str:
    """
    Read and return the contents of a file.

    Args:
        path (str): Path to the file.

    Returns:
        str: File contents as a string.

    Raises:
        IOError: If the file cannot be read.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        log(f"Failed to read file {path}: {e}", level="ERROR")
        raise

def write_file(path: str, content: str):
    """
    Write content to a file, creating any missing directories.

    Args:
        path (str): Path to the file.
        content (str): Content to write.

    Raises:
        IOError: If the file cannot be written.
    """
    try:
        ensure_dir(os.path.dirname(path))
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        log(f"Failed to write file {path}: {e}", level="ERROR")
        raise

def normalize_code(code: str) -> str:
    """
    Remove comments, strip whitespace, and collapse consecutive blank lines.

    Supports C/Java style block comments (/* ... */), line comments (// ...),
    and shell/Python style line comments (# ...).

    Args:
        code (str): Source code as a string.

    Returns:
        str: Normalized source code.
    """
    # Remove C-style block comments (non‑greedy across lines)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)

    lines = code.splitlines()
    normalized_lines = []
    blank_line_count = 0

    for line in lines:
        # Strip line comments
        line = re.sub(r'//.*', '', line)
        line = re.sub(r'#.*', '', line)
        line = line.strip()

        if line == '':
            blank_line_count += 1
            if blank_line_count == 1:
                normalized_lines.append('')
        else:
            blank_line_count = 0
            normalized_lines.append(line)

    return '\n'.join(normalized_lines)

def compute_hash(code: str) -> str:
    """
    Compute a SHA‑256 hash of the normalized code string.

    Args:
        code (str): Source code as a string.

    Returns:
        str: Hexadecimal SHA‑256 digest.
    """
    normalized = normalize_code(code)
    sha = hashlib.sha256()
    sha.update(normalized.encode('utf-8'))
    return sha.hexdigest()

def stream_file_lines(path: str):
    """
    Yield lines one by one from a file to avoid loading the entire file into memory.

    Args:
        path (str): Path to the file.

    Yields:
        str: Each line of the file, including the trailing newline.

    Raises:
        IOError: If the file cannot be opened.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                yield line
    except Exception as e:
        log(f"Failed to stream file {path}: {e}", level="ERROR")
        raise

def log(message: str, level: str = "INFO"):
    """
    Simple wrapper around Python's logging module.

    Ensures basic configuration on first call.

    Args:
        message (str): Log message.
        level (str): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    # Configure logging only once
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    getattr(logging, level.upper())(message)

def ensure_dir(path: str):
    """
    Create a directory if it does not exist.

    Args:
        path (str): Directory path.

    Raises:
        OSError: If the directory cannot be created.
    """
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        log(f"Failed to ensure directory {path}: {e}", level="ERROR")
        raise