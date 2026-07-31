"""
Log parser module for DeployContractAuditor.

This module provides a memory-mapped log parser that safely handles large log files,
malformed JSON entries, and Windows-specific empty-file crashes.
"""

import json
import mmap
import os
from typing import Any, Dict, Iterable


def parse_log_stream(file_path: str) -> Iterable[Dict[str, Any]]:
    """
    Parse a log file using memory mapping and yield parsed JSON dictionaries.
    
    This function implements a safe, memory-efficient parser that:
    - Handles empty files on Windows (avoids mmap crash)
    - Uses memory mapping for efficient large file processing
    - Gracefully handles malformed JSON and encoding errors
    - Properly manages file resources
    
    Args:
        file_path: Path to the log file to parse
        
    Yields:
        Parsed JSON dictionaries from the log file
    """
    # Check if file is empty to avoid Windows mmap crash
    if os.path.getsize(file_path) == 0:
        return
    
    with open(file_path, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
            for line in iter(mmapped_file.readline, b""):
                line = line.decode('utf-8').strip()
                
                if not line:
                    continue
                
                try:
                    parsed_line = json.loads(line)
                    yield parsed_line
                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping malformed JSON line: {line[:100]}... Error: {e}", 
                          file=__import__('sys').stderr)
                    continue
                except UnicodeDecodeError as e:
                    print(f"Warning: Skipping line with invalid UTF-8 encoding: {line[:100]}... Error: {e}", 
                          file=__import__('sys').stderr)
                    continue