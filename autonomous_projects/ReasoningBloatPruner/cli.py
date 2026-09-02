import sys
import os
import mmap
import argparse
import pathlib
import typing
import pipeline
import models


def parse_args(argv: typing.Optional[typing.List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments for the ReasoningBloatPruner CLI."""
    parser = argparse.ArgumentParser(
        description="Prune repetitive reasoning steps from agent inference trace logs."
    )
    parser.add_argument("input_pos", nargs="?", default=None, help="Path to the input JSONL trace file (positional).")
    parser.add_argument("--input", dest="input_flag", default=None, help="Path to the input JSONL trace file.")
    parser.add_argument("--output", default=None, help="Path to the output pruned JSONL file.")
    parser.add_argument("--window", type=int, default=3, help="Rolling window size for bloat detection.")
    parser.add_argument("--threshold", type=float, default=0.65, help="Similarity threshold for flagging bloat.")
    args = parser.parse_args(argv)
    input_path = args.input_flag or args.input_pos
    if not input_path:
        parser.error("the following arguments are required: input (positional or --input)")
    if not args.output:
        base = pathlib.Path(input_path)
        args.output = str(base.with_suffix(".pruned" + base.suffix))
    args.input = input_path
    return args


def main() -> int:
    """Execute the CLI entry point for trace pruning."""
    args = parse_args()
    input_path = args.input
    output_path = args.output

    if not pathlib.Path(input_path).is_file():
        print(f"Error: Input file '{input_path}' not found.")
        return 1

    output_dir = pathlib.Path(output_path).parent
    if output_dir and not output_dir.exists():
        print(f"Error: Output directory '{output_dir}' does not exist.")
        return 1

    try:
        if os.path.getsize(input_path) == 0:
            print(f"Warning: Input file '{input_path}' is empty. Skipping processing.")
            return 0
    except OSError as exc:
        print(f"Error: Cannot access input file metadata: {exc}")
        return 1

    config = {"window_size": args.window, "threshold": args.threshold}
    out_file = open(output_path, "w", encoding="utf-8")
    writer = lambda line: out_file.write(line + "\n")

    try:
        fh = open(input_path, "rb")
        try:
            mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
            line_iter = (ln.decode("utf-8", errors="replace") for ln in iter(mm.readline, b""))
        except mmap.error:
            fh.close()
            fh = open(input_path, "r", encoding="utf-8", errors="replace")
            line_iter = (ln for ln in fh)

        report = pipeline.run_pruning_pipeline(line_iter, writer, config)
        print(f"Processing complete. Original tokens: {report.original_tokens}")
        print(f"Tokens saved: {report.tokens_saved}")
        print(f"Compression ratio: {report.compression_ratio:.2%}")
        return 0
    except (FileNotFoundError, PermissionError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1
    finally:
        out_file.close()
        try:
            if "mm" in locals():
                mm.close()
            if "fh" in locals() and not fh.closed:
                fh.close()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())