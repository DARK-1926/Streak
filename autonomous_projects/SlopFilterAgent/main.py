"""
CLI entry point for the SlopFilterAgent.

This module bridges the filesystem and the core filtering logic, 
utilizing memory-mapped I/O for optimal performance on large datasets.
"""

import argparse
import io
import mmap
import os
import sys

import agent
import csv_processor


def process_file(
    input_path: str,
    output_path: str,
    text_column: str,
    entropy_thresh: float = 3.5,
    rep_thresh: float = 0.4
) -> None:
    """
    Process a CSV file to filter out low-signal comments using memory-mapped I/O.
    
    Args:
        input_path: Path to the input CSV file.
        output_path: Path to the output CSV file.
        text_column: The name of the column containing text to analyze.
        entropy_thresh: Minimum Shannon entropy threshold.
        rep_thresh: Minimum repetition ratio threshold.
        
    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If the input file is not a valid CSV or missing the text column.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    # Windows mmap fails on empty files; handle gracefully
    if os.path.getsize(input_path) == 0:
        with open(output_path, 'w', encoding='utf-8', newline='') as out_f:
            pass
        return

    with open(input_path, 'r', encoding='utf-8') as text_stream:
        parsed_data = csv_processor.parse_csv_content(text_stream, text_column)
                
    filtered_data = agent.filter_high_signal_comments(
        parsed_data, 
        text_column, 
        entropy_thresh, 
        rep_thresh
    )
    
    with open(output_path, 'w', encoding='utf-8', newline='') as out_f:
        csv_processor.format_csv_content(filtered_data, out_f)


def main() -> None:
    """
    CLI entry point for SlopFilterAgent.
    
    Parses command-line arguments and initiates the file processing pipeline.
    """
    parser = argparse.ArgumentParser(
        description="Filter AI-generated 'slop' from CSV datasets."
    )
    parser.add_argument(
        "--input", required=True, help="Path to the input CSV file."
    )
    parser.add_argument(
        "--output", required=True, help="Path to the output CSV file."
    )
    parser.add_argument(
        "--text-column", required=True, help="Name of the column containing text."
    )
    parser.add_argument(
        "--entropy", type=float, default=3.5, 
        help="Minimum Shannon entropy threshold (default: 3.5)."
    )
    parser.add_argument(
        "--repetition", type=float, default=0.4, 
        help="Minimum repetition ratio threshold (default: 0.4)."
    )
    
    args = parser.parse_args()
    
    try:
        process_file(
            input_path=args.input,
            output_path=args.output,
            text_column=args.text_column,
            entropy_thresh=args.entropy,
            rep_thresh=args.repetition
        )
        print(f"Successfully filtered dataset: {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()