from typing import List, Dict, Tuple
import re


def optimize_query(query: str) -> str:
    """
    Optimize a query by applying various optimization techniques including
    keyword normalization and redundant clause removal.
    
    Args:
        query (str): The input query string to optimize
        
    Returns:
        str: The optimized query string
    """
    if not isinstance(query, str):
        raise TypeError("Query must be a string")
    
    # Normalize keywords
    normalized_query = normalize_keyword(query)
    
    # Remove redundant clauses
    optimized_query = remove_redundant_clauses(normalized_query)
    
    return optimized_query


def get_optimization_stats(query: str) -> Dict[str, int]:
    """
    Get statistics about the optimization process applied to a query.
    
    Args:
        query (str): The input query string
        
    Returns:
        Dict[str, int]: Dictionary containing optimization statistics
    """
    if not isinstance(query, str):
        raise TypeError("Query must be a string")
    
    stats = {
        "original_length": len(query),
        "normalized_length": len(normalize_keyword(query)),
        "token_count": len(query.split()),
        "redundant_clauses_removed": 0
    }
    
    # Count redundant clauses
    clauses = re.split(r'[.!?]+', query)
    unique_clauses = set()
    redundant_count = 0
    
    for clause in clauses:
        clause = clause.strip()
        if clause and clause in unique_clauses:
            redundant_count += 1
        elif clause:
            unique_clauses.add(clause)
    
    stats["redundant_clauses_removed"] = redundant_count
    
    return stats


def normalize_keyword(query: str) -> str:
    """
    Normalize keywords in the query by converting to lowercase and removing extra whitespace.
    
    Args:
        query (str): The input query string
        
    Returns:
        str: The normalized query string
    """
    if not isinstance(query, str):
        raise TypeError("Query must be a string")
    
    # Convert to lowercase
    normalized = query.lower()
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Strip leading/trailing whitespace
    normalized = normalized.strip()
    
    return normalized


def remove_redundant_clauses(query: str) -> str:
    """
    Remove redundant clauses from the query by identifying repeated phrases.
    
    Args:
        query (str): The input query string
        
    Returns:
        str: The query with redundant clauses removed
    """
    if not isinstance(query, str):
        raise TypeError("Query must be a string")
    
    # Split into clauses based on sentence endings
    clauses = re.split(r'([.!?]+)', query)
    
    # Separate actual clauses from punctuation
    actual_clauses = []
    punctuations = []
    
    for i, part in enumerate(clauses):
        if i % 2 == 0 and part.strip():
            actual_clauses.append(part.strip())
        elif i % 2 == 1 and part.strip():
            punctuations.append(part)
    
    # Track seen clauses to identify duplicates
    seen_clauses = set()
    unique_clauses = []
    
    for clause in actual_clauses:
        # Normalize clause for comparison
        normalized_clause = normalize_keyword(clause)
        
        # If this normalized clause hasn't been seen before, keep it
        if normalized_clause not in seen_clauses:
            seen_clauses.add(normalized_clause)
            unique_clauses.append(clause)
        # Otherwise, skip it (it's redundant)
    
    # Reconstruct the query with unique clauses
    result_parts = []
    for i, clause in enumerate(unique_clauses):
        result_parts.append(clause)
        if i < len(unique_clauses) - 1:
            # Add back the punctuation between clauses
            result_parts.append(". ")
    
    return "".join(result_parts)