import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from typing import List

from models import TraceEntry, BloatSegment, CompressionReport
from parser import parse_trace_lines
from analyzer import detect_bloat, compress_trace
from pipeline import run_pruning_pipeline


class TestReasoningBloatPruner(unittest.TestCase):
    """Strict unit test suite for the ReasoningBloatPruner pipeline."""

    def test_parser_resilience(self) -> None:
        """Feed mixed valid/invalid lines and assert only valid TraceEntries yield."""
        lines: List[str] = [
            '{"id": 1, "content": "Valid step one", "tokens": 10}',
            'definitely not json',
            '{"id": 2, "content": "Missing tokens key"}',
            '',
            '{"id": 3, "content": "Valid step two", "tokens": 15}'
        ]
        entries: List[TraceEntry] = list(parse_trace_lines(lines))
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].id, 1)
        self.assertEqual(entries[0].content, "Valid step one")
        self.assertEqual(entries[0].tokens, 10)
        self.assertEqual(entries[1].id, 3)
        self.assertEqual(entries[1].tokens, 15)

    def test_bloat_detection_accuracy(self) -> None:
        """Create synthetic loop and assert detector returns exact span and score."""
        unique_start = TraceEntry(id=0, content="Initial reasoning step.", tokens=5)
        repetitive_content = "Circular logic detected in loop iteration."
        reps: List[TraceEntry] = [
            TraceEntry(id=i, content=repetitive_content, tokens=8) for i in range(1, 6)
        ]
        unique_end = TraceEntry(id=6, content="Final conclusion step.", tokens=6)
        entries: List[TraceEntry] = [unique_start] + reps + [unique_end]

        segments: List[BloatSegment] = detect_bloat(entries, threshold=0.7)
        self.assertEqual(len(segments), 1)
        seg: BloatSegment = segments[0]
        self.assertEqual(seg.start_index, 1)
        self.assertEqual(seg.end_index, 5)
        self.assertGreaterEqual(seg.score, 0.7)

    def test_compression_math(self) -> None:
        """Pass entries and segment to compressor and verify exact token savings."""
        entries: List[TraceEntry] = [
            TraceEntry(id=0, content="Start", tokens=5),
            TraceEntry(id=1, content="Loop A", tokens=10),
            TraceEntry(id=2, content="Loop A", tokens=10),
            TraceEntry(id=3, content="Loop A", tokens=10),
            TraceEntry(id=4, content="Loop A", tokens=10),
            TraceEntry(id=5, content="Loop A", tokens=10),
            TraceEntry(id=6, content="End", tokens=5)
        ]
        segments: List[BloatSegment] = [BloatSegment(start_index=1, end_index=5, score=0.95)]
        report: CompressionReport = compress_trace(entries, segments)

        expected_saved: int = sum(e.tokens for e in entries[1:6])
        self.assertEqual(report.segments_pruned, 1)
        self.assertEqual(report.saved_tokens, expected_saved)
        self.assertEqual(len(report.pruned_entries), len(entries) - 4)

    def test_pipeline_integration(self) -> None:
        """Run end-to-end pipeline with StringIO and verify JSONL output and report."""
        input_lines: List[str] = [
            '{"id": 0, "content": "Init", "tokens": 5}',
            '{"id": 1, "content": "Repeat", "tokens": 8}',
            '{"id": 2, "content": "Repeat", "tokens": 8}',
            '{"id": 3, "content": "Repeat", "tokens": 8}',
            '{"id": 4, "content": "Repeat", "tokens": 8}',
            '{"id": 5, "content": "Repeat", "tokens": 8}',
            '{"id": 6, "content": "Done", "tokens": 5}',
            'invalid json line'
        ]
        output_buffer: io.StringIO = io.StringIO()
        report: CompressionReport = run_pruning_pipeline(
            input_lines, output_buffer, {"threshold": 0.7}
        )

        output_buffer.seek(0)
        raw_output: str = output_buffer.getvalue().strip()
        self.assertTrue(len(raw_output) > 0)
        output_lines: List[str] = raw_output.splitlines()
        for line in output_lines:
            parsed: dict = json.loads(line)
            self.assertIn("content", parsed)

        self.assertEqual(report.segments_pruned, 1)
        self.assertEqual(report.saved_tokens, 40)

    def test_cli_exit_codes(self) -> None:
        """Invoke cli.py via subprocess with --help and empty file, assert exit 0."""
        help_result: subprocess.CompletedProcess = subprocess.run(
            [sys.executable, "cli.py", "--help"],
            capture_output=True, text=True
        )
        self.assertEqual(help_result.returncode, 0)

        fd: int
        temp_path: str
        fd, temp_path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write("")
            run_result: subprocess.CompletedProcess = subprocess.run(
                [sys.executable, "cli.py", temp_path],
                capture_output=True, text=True
            )
            self.assertEqual(run_result.returncode, 0)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()