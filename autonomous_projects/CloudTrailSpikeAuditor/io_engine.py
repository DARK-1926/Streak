import os
import mmap
from typing import Iterator


def stream_log_lines(file_path: str) -> Iterator[str]:
    """
    Safely streams lines from a JSONL file using memory mapping.

    Checks file size before mapping to prevent win32 empty-file crashes.
    Yields decoded UTF-8 strings line by line.

    Args:
        file_path: Path to the JSONL log file.

    Yields:
        str: Decoded UTF-8 string of each line.
        
    Raises:
        OSError: If the file cannot be accessed or its size cannot be determined.
    """
    try:
        file_size = os.path.getsize(file_path)
    except FileNotFoundError:
        raise
    except OSError as exc:
        raise OSError(f"Unable to access file '{file_path}': {exc}") from exc

    if file_size == 0:
        return

    with open(file_path, "rb") as file_obj:
        with mmap.mmap(file_obj.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for raw_line in iter(mm.readline, b""):
                yield raw_line.decode("utf-8")