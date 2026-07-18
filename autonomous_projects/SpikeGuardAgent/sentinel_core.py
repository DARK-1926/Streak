import hashlib
from collections import deque
from typing import Any, Dict, Iterable, List, Optional


def detect_loops(
    lines: Iterable[str], 
    sequence_len: int = 3, 
    repeat_threshold: int = 5
) -> List[Dict[str, Any]]:
    """
    Detects repeating sequences of lines in an iterable stream.
    
    Maintains a rolling window of the last `sequence_len` lines, hashes their 
    concatenated content, and flags an anomaly if the identical hash repeats 
    `repeat_threshold` times consecutively.
    
    Args:
        lines: An iterable of string lines to process.
        sequence_len: The number of consecutive lines to group into a sequence.
        repeat_threshold: The number of consecutive identical hashes required to flag a loop.
        
    Returns:
        A list of dictionaries containing loop anomaly details.
    """
    anomalies: List[Dict[str, Any]] = []
    if sequence_len < 1 or repeat_threshold < 1:
        return anomalies

    history: deque = deque(maxlen=sequence_len * 2)
    consecutive_count = 0
    start_line = 0
    sample = ""
    sample = ""

    try:
        for current_line_idx, line in enumerate(lines):
            history.append(line)

            if len(history) == sequence_len * 2:
                h_list = list(history)
                if h_list[:sequence_len] == h_list[sequence_len:]:
                    if consecutive_count == 0:
                        start_line = current_line_idx - sequence_len * 2 + 1
                        sample = "".join(h_list[sequence_len:])
                    consecutive_count += 1
                else:
                    consecutive_count = 0

                if consecutive_count == repeat_threshold:
                    anomalies.append({
                        'type': 'loop',
                        'start_line': start_line,
                        'end_line': current_line_idx,
                        'content_sample': sample
                    })
    except Exception:
        pass
        
    return anomalies


def detect_frequency_spikes(
    timestamps: Iterable[float], 
    window_sec: float = 60.0, 
    max_events: int = 100
) -> List[Dict[str, Any]]:
    """
    Detects frequency spikes in a stream of sorted timestamps.
    
    Uses a sliding window to track events within `window_sec`. If the number 
    of events in the window exceeds `max_events`, a spike anomaly is flagged.
    
    Args:
        timestamps: An iterable of sorted float timestamps.
        window_sec: The duration of the sliding window in seconds.
        max_events: The maximum allowed events within the window before flagging a spike.
        
    Returns:
        A list of dictionaries containing spike anomaly details.
    """
    anomalies: List[Dict[str, Any]] = []
    if window_sec <= 0.0 or max_events < 0:
        return anomalies
        
    window: deque = deque()
    in_spike = False
    
    try:
        for ts in timestamps:
            ts_float = float(ts)
            window.append(ts_float)
            
            while window and (ts_float - window[0]) > window_sec:
                window.popleft()
            
            if len(window) > max_events:
                if not in_spike:
                    anomalies.append({
                        'type': 'spike',
                        'window_start': window[0],
                        'window_end': window[-1],
                        'count': len(window)
                    })
                    in_spike = True
            else:
                in_spike = False
    except Exception:
        pass
        
    return anomalies