"""
I/O streaming logic for AgentSwarmLoopAuditor.

Provides memory-mapped file streaming for reading JSONL logs efficiently
without loading the entire file into RAM, hardened for Windows semantics.
"""

import mmap
import os
from typing import Iterable


def stream_jsonl(filepath: str) -> Iterable[str]:
    """
    Streams lines from a JSONL file using memory mapping.
    
    Uses os.path.getsize to guard against win32 mmap empty-file crashes.
    If size > 0, opens the file in 'rb' mode, creates a read-only memory map,
    and yields decoded lines.
    
    Args:
        filepath: The path to the JSONL file to stream.
        
    Yields:
        Decoded string lines from the file.
    """
    try:
        size = os.path.getsize(filepath)
    except OSError:
        return
        
    if size == 0:
        return
        
    try:
        with open(filepath, 'rb') as f:
            try:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    for line in iter(mm.readline, b''):
                        yield line.decode('utf-8')
            except ValueError:
                # Handle ValueError for empty files gracefully
                return
    except OSError:
        return