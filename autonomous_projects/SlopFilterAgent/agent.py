"""
Orchestration logic for the SlopFilterAgent.

This module coordinates the filtering pipeline by applying heuristic 
thresholds to parsed data streams and yielding filtered results.
"""

from typing import Dict, List

import heuristics


def filter_high_signal_comments(
    comments: List[Dict[str, str]],
    text_key: str = "text",
    entropy_thresh: float = 3.5,
    rep_thresh: float = 0.4
) -> List[Dict[str, str]]:
    """
    Filter a list of comments to retain only those with high signal (not likely slop).
    
    Iterates through the provided comments and applies heuristic analysis 
    to the text found under the specified key. Comments identified as 
    'likely slop' are excluded from the returned list.
    
    Args:
        comments: A list of dictionaries representing the parsed CSV rows.
        text_key: The dictionary key containing the text to be analyzed.
        entropy_thresh: The minimum Shannon entropy threshold.
        rep_thresh: The minimum repetition ratio threshold.
        
    Returns:
        A new list of dictionaries containing only the high-signal comments.
        
    Raises:
        TypeError: If comments is not a list or text_key is not a string.
        KeyError: If the text_key is missing from any comment dictionary.
    """
    if not isinstance(comments, list):
        raise TypeError("comments must be a list of dictionaries.")
    if not isinstance(text_key, str):
        raise TypeError("text_key must be a string.")
        
    filtered_comments: List[Dict[str, str]] = []
    
    for comment in comments:
        if not isinstance(comment, dict):
            raise TypeError("Each item in comments must be a dictionary.")
            
        if text_key not in comment:
            raise KeyError(f"Required key '{text_key}' not found in comment.")
            
        text = comment[text_key]
        
        # Retain the comment if it is NOT likely slop
        if not heuristics.is_likely_slop(text, entropy_thresh, rep_thresh):
            filtered_comments.append(comment)
            
    return filtered_comments