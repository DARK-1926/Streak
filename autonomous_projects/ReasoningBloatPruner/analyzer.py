import collections
from typing import Iterable, List

from models import TraceEntry, BloatSegment, CompressionReport


def detect_bloat(entries: Iterable[TraceEntry], window_size: int = 3, threshold: float = 0.65) -> List[BloatSegment]:
    """Detect repetitive reasoning spans using rolling shingle similarity.
    
    Materializes the iterable, computes word 3-gram sets, and tracks consecutive
    Jaccard similarities against a threshold to identify bloat segments.
    """
    entries_list = list(entries)
    if len(entries_list) < 2:
        return []

    def get_shingles(text: str) -> set:
        words = text.lower().split()
        if len(words) < 3:
            # For texts with fewer than 3 words, return a unique identifier based on the content
            return {(text.lower(),)}
        return {tuple(words[i:i+3]) for i in range(len(words) - 2)}

    segments: List[BloatSegment] = []
    prev_shingles = get_shingles(entries_list[0].content)
    streak = 0
    seg_start = 0
    in_segment = False
    sim_sum = 0.0

    for i in range(1, len(entries_list)):
        try:
            curr_shingles = get_shingles(entries_list[i].content)
            if not prev_shingles and not curr_shingles:
                sim = 1.0
            else:
                union = prev_shingles | curr_shingles
                sim = len(prev_shingles & curr_shingles) / len(union) if union else 0.0
        except Exception:
            sim = 0.0

        if sim >= threshold:
            streak += 1
            sim_sum += sim
            if streak >= window_size and not in_segment:
                in_segment = True
                seg_start = i - streak
        else:
            if in_segment:
                avg_sim = sim_sum / streak if streak > 0 else threshold
                segments.append(BloatSegment(
                    start_index=seg_start,
                    end_index=i - 1,
                    score=min(max(avg_sim, 0.0), 1.0)
                ))
                in_segment = False
            streak = 0
            sim_sum = 0.0
        prev_shingles = curr_shingles

    if in_segment:
        avg_sim = sim_sum / streak if streak > 0 else threshold
        segments.append(BloatSegment(
            start_index=seg_start,
            end_index=len(entries_list) - 1,
            score=min(max(avg_sim, 0.0), 1.0)
        ))

    return segments


def compress_trace(entries: List[TraceEntry], segments: List[BloatSegment]) -> CompressionReport:
    """Collapse flagged spans into summary entries and calculate token savings.
    
    Iterates through entries by index, replacing indices covered by bloat segments
    with a single summarized TraceEntry. Computes exact token metrics.
    """
    original_tokens = sum(e.tokens for e in entries)
    compressed: List[TraceEntry] = []
    sorted_segs = sorted(segments, key=lambda s: s.start_index)
    seg_ptr = 0
    i = 0
    segments_pruned = 0

    while i < len(entries):
        if seg_ptr < len(sorted_segs) and sorted_segs[seg_ptr].start_index <= i <= sorted_segs[seg_ptr].end_index:
            seg = sorted_segs[seg_ptr]
            span = entries[seg.start_index : seg.end_index + 1]
            span_tokens = sum(e.tokens for e in span)
            try:
                compressed.append(TraceEntry(
                    id=segments_pruned,
                    content=f"[Pruned {len(span)} repetitive reasoning steps]",
                    tokens=5
                ))
            except (ValueError, TypeError):
                compressed.extend(span)
            segments_pruned += 1
            i = seg.end_index + 1
            seg_ptr += 1
        else:
            compressed.append(entries[i])
            i += 1

    # Calculate tokens saved as the total tokens in pruned segments
    saved_tokens = sum(sum(e.tokens for e in entries[s.start_index:s.end_index+1]) for s in segments)
    return CompressionReport(
        original_tokens=original_tokens,
        saved_tokens=saved_tokens,
        segments_pruned=segments_pruned,
        pruned_entries=compressed
    )