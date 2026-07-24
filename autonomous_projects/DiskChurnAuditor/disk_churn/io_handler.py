import mmap
import os
from typing import Generator


def stream_log_file(filepath: str) -> Generator[str, None, None]:
    """
    Streams a JSONL log file line by line using memory mapping.
    
    Safely handles empty files to prevent Windows mmap crashes and 
    ensures strict resource cleanup via context managers.
    
    Args:
        filepath: The path to the JSONL log file.
        
    Yields:
        Decoded UTF-8 strings representing each line in the file.
        
    Raises:
        FileNotFoundError: If the specified filepath does not exist.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Log file not found: {filepath}")
        
    if os.path.getsize(filepath) == 0:
        return
        
    with open(filepath, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for line in iter(mm.readline, b""):
                yield line.decode('utf-8').replace('\r\n', '\n')