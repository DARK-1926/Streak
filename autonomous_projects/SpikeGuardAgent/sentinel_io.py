import io
import mmap
import os
import re
import datetime
from typing import Iterable, Union


def stream_log_lines(source: Union[str, io.TextIOBase]) -> Iterable[str]:
    """
    Streams lines from a file path or a TextIOBase object.
    
    Uses memory mapping (mmap) for efficient file reading. Includes strict 
    win32 safeguards to prevent ValueError on empty files.
    
    Args:
        source: A string representing the file path, or an io.TextIOBase stream.
        
    Yields:
        Decoded UTF-8 string lines from the source.
    """
    if isinstance(source, io.TextIOBase):
        yield from source
        return
        
    if not isinstance(source, str):
        raise TypeError("source must be a filepath string or io.TextIOBase")
        
    if os.path.getsize(source) == 0:
        return
        
    with open(source, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for raw_line in iter(mm.readline, b""):
                yield raw_line.decode('utf-8', errors='ignore')


def extract_timestamps(
    lines: Iterable[str], 
    regex_pattern: str = r'\[(.*?)\]'
) -> Iterable[float]:
    """
    Extracts and parses timestamps from an iterable of log lines.
    
    Searches each line for a timestamp matching the provided regex pattern, 
    parses it as an ISO 8601 formatted string, and yields the POSIX timestamp.
    
    Args:
        lines: An iterable of string lines to process.
        regex_pattern: A regex pattern with a capture group for the timestamp.
        
    Yields:
        Float POSIX timestamps.
    """
    pattern = re.compile(regex_pattern)
    
    for line in lines:
        match = pattern.search(line)
        if match:
            try:
                dt = datetime.datetime.fromisoformat(match.group(1))
                yield dt.timestamp()
            except ValueError:
                continue