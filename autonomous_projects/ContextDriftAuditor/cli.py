import sys
import os
import mmap
import json
import contextlib
from typing import List, Generator

import context_drift


def safe_mmap_generator(filepath: str) -> Generator[str, None, None]:
    """
    Safely generate lines from a file using memory mapping.
    
    This function provides a low-memory mechanism for reading massive 
    repository files. It includes a strict guard against empty files 
    to prevent crashes on Windows (win32) systems.
    
    Args:
        filepath: The absolute or relative path to the target file.
        
    Yields:
        str: Decoded UTF-8 lines from the file, stripped of byte encoding.
    """
    try:
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            return
    except OSError as e:
        print(f"Warning: Could not access file '{filepath}': {e}", file=sys.stderr)
        return

    with open(filepath, 'rb') as f:
        # contextlib.closing ensures the mmap object is properly closed, 
        # satisfying strict resource management requirements.
        with contextlib.closing(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)) as mm:
            yield from (line.decode('utf-8') for line in iter(mm.readline, b''))


def main(argv: List[str]) -> int:
    """
    Main entry point for the ContextDriftAuditor CLI.
    
    Orchestrates the parsing of JSONL manifests and knowledge bases,
    executes the O(N) drift detection, and outputs a deterministic 
    JSON report to standard output.
    
    Args:
        argv: A list of command line arguments, typically sys.argv.
              Expected format: [script_name, manifest_path, knowledge_path]
              
    Returns:
        int: 0 on successful execution, 1 on any encountered error.
    """
    if len(argv) != 3:
        print("Usage: cli.py <manifest_path> <knowledge_path>", file=sys.stderr)
        return 1

    manifest_path = argv[1]
    knowledge_path = argv[2]

    if not os.path.exists(manifest_path):
        print(f"Error: Manifest file not found: {manifest_path}", file=sys.stderr)
        return 1

    if not os.path.exists(knowledge_path):
        print(f"Error: Knowledge base file not found: {knowledge_path}", file=sys.stderr)
        return 1

    try:
        manifest_gen = safe_mmap_generator(manifest_path)
        knowledge_gen = safe_mmap_generator(knowledge_path)
        
        # Execute the core O(N) drift detection and slop scoring pipeline
        report = context_drift.audit_context_drift(manifest_gen, knowledge_gen)
        
        # Output the final deterministic report as formatted JSON
        print(json.dumps(report, indent=2))
        return 0
        
    except Exception as e:
        print(f"Critical Error during audit execution: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))