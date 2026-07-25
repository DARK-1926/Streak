import os
import mmap
from typing import Iterable


def yield_log_lines(filepath: str) -> Iterable[str]:
    """
    Safely yields lines from a log file using memory-mapped I/O.

    This generator provides a memory-efficient way to process large JSONL
    files. It includes an explicit guard against zero-byte files to prevent
    crashes on Windows (win32) when initializing the memory map.

    Args:
        filepath: The absolute or relative path to the target log file.

    Yields:
        str: Decoded, stripped, and non-empty lines from the file.
    """
    try:
        if os.path.getsize(filepath) == 0:
            return
    except OSError:
        return

    with open(filepath, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for line in iter(mm.readline, b""):
                decoded_line = line.decode('utf-8', errors='ignore').strip()
                if decoded_line:
                    yield decoded_line