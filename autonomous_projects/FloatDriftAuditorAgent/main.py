"""
CLI and I/O layer for the FloatDriftAuditorAgent.

This module provides the entry point for the application, handling 
memory-mapped file I/O to efficiently process large transaction logs 
while guarding against platform-specific edge cases like empty files on Windows.
"""

import os
import sys
import mmap
from decimal import Decimal

import auditor
import models


def process_file(filepath: str) -> models.DriftReport:
    """
    Processes a transaction file using memory-mapped I/O to detect billing drift.
    
    Includes a specific guard against empty files to prevent crashes on Windows 
    (Win32) when attempting to memory-map a zero-byte file.
    
    Args:
        filepath: The path to the CSV file to be audited.
        
    Returns:
        A DriftReport containing the audit results.
        
    Raises:
        FileNotFoundError: If the specified filepath does not exist.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"The file '{filepath}' does not exist.")
        
    if os.path.getsize(filepath) == 0:
        return models.DriftReport(0.0, Decimal('0'), Decimal('0'), 0)
        
    with open(filepath, 'rb') as f:
        m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        try:
            lines = (line.decode('utf-8').strip() for line in iter(m.readline, b''))
            report = auditor.audit_stream(lines)
        finally:
            m.close()
            
    return report


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python main.py <filepath>")
        sys.exit(1)
        
    target_filepath = sys.argv[1]
    
    try:
        drift_report = process_file(target_filepath)
        print(drift_report)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)