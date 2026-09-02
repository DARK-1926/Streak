# ReasoningBloatPruner

A deterministic, zero-dependency pipeline for detecting and compressing repetitive reasoning steps in agentic inference trace logs. Designed to prevent context window exhaustion and eliminate token waste.

## Problem Statement

Agentic AI systems frequently generate verbose inference logs containing circular or repetitive reasoning steps. This "reasoning bloat" rapidly consumes limited context windows, increases inference latency, and inflates token costs. ReasoningBloatPruner identifies these redundant spans, collapses them into concise summaries, and preserves logical flow while maximizing token efficiency.

## Architecture

The project follows a strict, modular pipeline architecture with frozen dataclasses and pure functions:

- `models.py`: Core data structures (`TraceEntry`, `BloatSegment`, `CompressionReport`) with strict `__post_init__` validation constraints.
- `parser.py`: Resilient JSONL stream parser (`parse_trace_lines`) that safely handles malformed JSON, missing keys, and type mismatches without crashing.
- `analyzer.py`: Single-pass bloat detection (`detect_bloat`) using rolling word-shingle hashing and Jaccard similarity, plus a trace compressor (`compress_trace`) that calculates exact token savings.
- `pipeline.py`: Dependency-injected orchestration layer (`run_pruning_pipeline`) connecting parsing, analysis, and output streaming.
- `cli.py`: Production-ready command-line interface with memory-mapped file streaming, explicit byte decoding, and safe resource cleanup.
- `test_main.py`: Comprehensive, zero-mock test suite validating pure functions, exact dataclass states, and end-to-end CLI execution.

## How it Works

1. **Ingestion & Parsing**: Raw JSONL lines are streamed and parsed into validated `TraceEntry` objects. The parser uses safe dictionary lookups and type checking, silently skipping empty lines, malformed JSON, or invalid payloads to guarantee pipeline resilience.
2. **Bloat Detection**: The analyzer materializes the trace and computes word 3-gram (shingle) sets for each step. It calculates the Jaccard similarity between consecutive steps. When similarity exceeds a configurable threshold across a rolling window, a `BloatSegment` is flagged with precise start/end indices and a normalized redundancy score.
3. **Compression & Summarization**: Flagged segments are collapsed into single summary entries. The compressor reconstructs the trace, preserves non-bloat steps, and computes exact token savings metrics by comparing original vs. pruned token counts.
4. **Output Streaming**: Pruned entries are serialized back to JSONL and streamed to the output destination. A `CompressionReport` is returned containing the pruned entries, original token count, pruned token count, and exact savings percentage.

## Usage

```bash
python cli.py --input trace.jsonl --output pruned.jsonl --window 3 --threshold 0.65
```

**CLI Arguments:**
- `--input` (required): Path to the input JSONL trace file.
- `--output` (required): Path to the output pruned JSONL file.
- `--window` (default: 3): Rolling window size for consecutive similarity matching.
- `--threshold` (default: 0.65): Jaccard similarity threshold (0.0 to 1.0) for flagging bloat.

Exit codes: `0` for success/empty input, `1` for file/path errors or processing failures.

## Design Decisions

- **Single-Pass Rolling Shingle Detection**: Uses word-level n-grams and Jaccard similarity for O(N) detection without heavy NLP dependencies. Ensures deterministic, reproducible results across runs.
- **Dependency Injection (DI)**: The pipeline accepts iterables for input and callables for output. This eliminates filesystem coupling during unit tests and enables pure function validation with in-memory data.
- **Win32-Safe Memory Mapping**: The CLI uses `mmap` for efficient large-file streaming with explicit UTF-8 decoding and error replacement. File handles and memory maps are explicitly closed to prevent Windows permission locks (`[WinError 32]`) during cleanup.
- **Strict Data Validation**: Frozen dataclasses with post-initialization guards ensure data integrity throughout the pipeline. Invalid states fail fast at ingestion rather than propagating silent corruption.

## Testing Strategy

- **Pure Functions & Zero Mocks**: All core logic operates on in-memory iterables. Tests assert exact dataclass states and mathematical correctness of token savings without patching or mocking.
- **Resilience Verification**: Parser tests feed mixed valid/invalid JSONL to guarantee graceful degradation and correct yield counts.
- **Synthetic Loop Detection**: Analyzer tests construct deliberate repetitive sequences to verify precise index tracking, threshold behavior, and segment boundary accuracy.
- **End-to-End CLI Validation**: Subprocess execution validates argument parsing, exit codes, and actual file I/O. Tests verify that the CLI correctly handles missing files, empty inputs, and successful pruning runs.

## Requirements

- Python 3.8+
- Standard library only (no external dependencies)