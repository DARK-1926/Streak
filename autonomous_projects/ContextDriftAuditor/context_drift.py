import json
import re
from typing import Any, Dict, Iterable, List, Optional, Set

SLOP_PHRASES: List[str] = [
    'delve', 
    'testament', 
    'tapestry', 
    'crucial', 
    'in conclusion', 
    'as an ai', 
    'foster'
]

SYMBOL_REGEX = re.compile(r'\b[A-Z][a-zA-Z0-9_]*\b')


def parse_manifest_entry(line: str) -> Optional[str]:
    """
    Parse a JSONL manifest entry.
    
    Args:
        line: A JSON string representing a manifest entry.
        
    Returns:
        The symbol string if the entry is of type 'code', otherwise None.
    """
    try:
        data = json.loads(line)
        if isinstance(data, dict) and data.get("type") == "code" and "symbol" in data:
            return str(data["symbol"])
    except (json.JSONDecodeError, TypeError, AttributeError):
        pass
    return None


def parse_knowledge_entry(line: str) -> Optional[Dict[str, Any]]:
    """
    Parse a JSONL knowledge base entry.
    
    Args:
        line: A JSON string representing a knowledge entry.
        
    Returns:
        A dictionary containing the entry data if valid, otherwise None.
    """
    try:
        data = json.loads(line)
        if isinstance(data, dict) and "id" in data and "text" in data and "author" in data:
            return data
    except (json.JSONDecodeError, TypeError, AttributeError):
        pass
    return None


def calculate_slop_score(text: str) -> float:
    """
    Calculate the 'slop score' of a given text based on known LLM filler phrases.
    
    Args:
        text: The documentation text to evaluate.
        
    Returns:
        A float between 0.0 and 1.0 representing the ratio of slop occurrences to total words.
    """
    if not text or not text.strip():
        return 0.0
        
    words = text.split()
    total_words = len(words)
    if total_words == 0:
        return 0.0
        
    text_lower = text.lower()
    slop_count = 0
    for phrase in SLOP_PHRASES:
        slop_count += text_lower.count(phrase)
        
    score = slop_count / total_words
    return min(score, 1.0)


def audit_context_drift(manifest_stream: Iterable[str], knowledge_stream: Iterable[str]) -> Dict[str, Any]:
    """
    Audit context drift between a code manifest and a knowledge base.
    
    Args:
        manifest_stream: An iterable of JSONL strings representing the code manifest.
        knowledge_stream: An iterable of JSONL strings representing the knowledge base.
        
    Returns:
        A summary dictionary containing drift and slop statistics.
    """
    valid_symbols: Set[str] = set()
    for line in manifest_stream:
        symbol = parse_manifest_entry(line)
        if symbol is not None:
            valid_symbols.add(symbol)
            
    total_docs = 0
    drifted_docs = 0
    high_slop_docs = 0
    orphaned_symbols: Set[str] = set()
    
    for line in knowledge_stream:
        entry = parse_knowledge_entry(line)
        if entry is None:
            continue
            
        total_docs += 1
        text = str(entry.get("text", ""))
        
        referenced_symbols = set(SYMBOL_REGEX.findall(text))
        has_drift = False
        for ref in referenced_symbols:
            if ref not in valid_symbols:
                orphaned_symbols.add(ref)
                has_drift = True
                
        if has_drift:
            drifted_docs += 1
            
        slop_score = calculate_slop_score(text)
        if slop_score > 0.05:
            high_slop_docs += 1
            
    return {
        'total_docs': total_docs,
        'drifted_docs': drifted_docs,
        'high_slop_docs': high_slop_docs,
        'orphaned_symbols': sorted(list(orphaned_symbols))
    }