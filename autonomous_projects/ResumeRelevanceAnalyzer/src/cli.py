import argparse
import json
import mmap
import os
import sys
from typing import List, Dict, Any

from .parser import parse_document
from .scorer import compute_relevance


def read_lines_with_mmap(filepath: str) -> List[str]:
    """
    Read a file as a list of lines using memory mapping for efficiency.
    
    Falls back to regular file reading if mmap fails (e.g., on empty files or Windows).
    
    Args:
        filepath: Path to the file to read.
        
    Returns:
        List of lines from the file, with line endings stripped.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Check if file is empty to avoid mmap issues on Windows
            if os.path.getsize(filepath) == 0:
                return []
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                content = mm.read().decode('utf-8')
                return content.splitlines()
    except (OSError, ValueError):
        # Fallback to regular read in case mmap fails
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().splitlines()


def main(argv: List[str]) -> int:
    """
    Entry point for the Resume Relevance Analyzer CLI.
    
    Parses command-line arguments, validates input files, processes resume and job
    description, computes relevance score, and outputs JSON result.
    
    Args:
        argv: List of command-line arguments (excluding script name).
        
    Returns:
        0 on success, 1 on error.
    """
    parser = argparse.ArgumentParser(
        description="Analyze resume relevance against a job description."
    )
    parser.add_argument("resume", help="Path to the resume file")
    parser.add_argument("job_description", help="Path to the job description file")
    args = parser.parse_args(argv)

    try:
        # Validate that both files exist and are non-empty
        for filepath in [args.resume, args.job_description]:
            if not os.path.isfile(filepath):
                print(f"Error: File not found: {filepath}", file=sys.stderr)
                return 1
            if os.path.getsize(filepath) == 0:
                print(f"Error: File is empty: {filepath}", file=sys.stderr)
                return 1

        # Read and parse both documents
        resume_lines = read_lines_with_mmap(args.resume)
        job_lines = read_lines_with_mmap(args.job_description)

        resume_parsed = parse_document(resume_lines)
        job_parsed = parse_document(job_lines)

        # Compute relevance
        result = compute_relevance(resume_parsed, job_parsed)

        # Output JSON to stdout
        print(json.dumps(result, indent=2))
        return 0

    except (FileNotFoundError, ValueError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        # Catch-all for unexpected errors (e.g., encoding issues)
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))