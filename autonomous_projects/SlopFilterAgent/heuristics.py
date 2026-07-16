import math
from collections import Counter


def calculate_shannon_entropy(text: str) -> float:
    """
    Calculate the Shannon entropy of characters in the given text.
    
    Shannon entropy measures the information density and unpredictability 
    of a string. A lower entropy indicates a more predictable, potentially 
    synthetic text distribution.
    
    Args:
        text: The input string to analyze.
        
    Returns:
        The Shannon entropy as a float. Returns 0.0 for empty strings.
    """
    if not text:
        return 0.0
        
    counts = Counter(text)
    length = len(text)
    entropy = 0.0
    
    for count in counts.values():
        probability = count / length
        if probability > 0:
            entropy -= probability * math.log2(probability)
            
    return entropy


def calculate_repetition_ratio(text: str) -> float:
    """
    Calculate the ratio of unique words to total words in the text.
    
    LLMs are prone to repeating specific phrases or structural patterns. 
    A lower ratio indicates higher repetition, which is a strong indicator 
    of AI-generated slop.
    
    Args:
        text: The input string to analyze.
        
    Returns:
        The ratio of unique words to total words as a float. 
        Returns 0.0 if the text contains no words.
    """
    words = text.split()
    if not words:
        return 0.0
        
    unique_words = set(words)
    return 1.0 - (len(unique_words) / len(words))


def is_likely_slop(text: str, entropy_threshold: float, repetition_threshold: float) -> bool:
    """
    Determine if the text is likely AI-generated 'slop' based on heuristic thresholds.
    
    The text is flagged as slop if its Shannon entropy falls below the 
    entropy threshold AND its repetition ratio falls below the repetition 
    threshold. Empty or whitespace-only strings are handled gracefully 
    and are not considered slop.
    
    Args:
        text: The input string to analyze.
        entropy_threshold: The maximum entropy value to be considered slop.
        repetition_threshold: The maximum repetition ratio to be considered slop.
        
    Returns:
        True if the text is likely slop, False otherwise.
    """
    if not text or not text.strip():
        return False
        
    try:
        entropy = calculate_shannon_entropy(text)
        repetition_ratio = calculate_repetition_ratio(text)
        
        return entropy < entropy_threshold and repetition_ratio > repetition_threshold
    except Exception:
        # Handle any unexpected mathematical or processing exceptions gracefully
        return False