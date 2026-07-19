"""
io_handler.py

Robust I/O handler for CloudDriftAuditor.
Utilizes memory-mapped files for efficient, single-pass reading of billing data,
with explicit guards to prevent Win32 crashes on empty files.
"""

import mmap
import os
from typing import Iterable


def stream_billing_file(filepath: str) -> Iterable[str]:
    """
    Streams lines from a billing file using memory mapping.

    Opens the specified file in binary read mode and creates a read-only
    memory map. Yields decoded, stripped lines one by one. Includes a
    critical guard for Windows environments to prevent ValueError when
    attempting to memory-map an empty file.

    Args:
        filepath: The path to the billing CSV file.

    Yields:
        Decoded and stripped string lines from the file.

    Raises:
        FileNotFoundError: If the specified filepath does not exist.
        PermissionError: If the file cannot be read due to permissions.
        OSError: If an underlying OS error occurs during file operations.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Billing file not found: {filepath}")

    # CRITICAL WIN32 GUARD: mmap raises ValueError on Windows for 0-byte files
    if os.path.getsize(filepath) == 0:
        return

    try:
        with open(filepath, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                for raw_line in iter(mm.readline, b""):
                    yield raw_line.decode('utf-8').strip()
    except PermissionError as e:
        raise PermissionError(f"Permission denied reading file: {filepath}") from e
    except OSError as e:
        raise OSError(f"OS error occurred while reading file: {filepath}") from e