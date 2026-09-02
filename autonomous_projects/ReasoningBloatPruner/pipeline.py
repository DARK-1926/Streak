import json
import typing
import parser
import analyzer
import models
from dataclasses import asdict


def run_pruning_pipeline(
    line_source: typing.Iterable[str],
    output_writer: typing.Callable[[str], None],
    config: dict
) -> models.CompressionReport:
    """Execute the full trace pruning pipeline with dependency injection.

    Streams raw lines through the parser, detects bloat segments, compresses
    the trace, and writes pruned entries to the provided output writer.

    Args:
        line_source: Iterable of raw JSONL strings.
        output_writer: Callable that accepts a single JSON string per entry.
        config: Dictionary containing 'window_size' and 'threshold' keys.

    Returns:
        CompressionReport containing metrics and pruned entries.
    """
    window_size = int(config.get("window_size", 3))
    threshold = float(config.get("threshold", 0.65))

    parsed_entries: typing.List[models.TraceEntry] = list(
        parser.parse_trace_lines(line_source)
    )

    bloat_segments = analyzer.detect_bloat(
        entries=parsed_entries,
        window_size=window_size,
        threshold=threshold
    )

    report: models.CompressionReport = analyzer.compress_trace(
        entries=parsed_entries,
        segments=bloat_segments
    )

    for entry in report.pruned_entries:
        try:
            json_str = json.dumps(asdict(entry))
            output_writer.write(json_str + "\n")
        except (TypeError, ValueError, AttributeError):
            continue

    return report