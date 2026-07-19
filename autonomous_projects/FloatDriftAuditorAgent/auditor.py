"""
Pure functional core logic for the FloatDriftAuditorAgent.

This module provides the mathematical core for detecting billing drift
by comparing IEEE 754 floating-point accumulation against exact base-10
decimal accumulation. It operates entirely in-memory with no I/O side effects.
"""

from decimal import Decimal
from typing import Iterable, Tuple

from models import DriftReport


def parse_cost(line: str) -> tuple[float, Decimal] | None:
    """
    Parses a single CSV line to extract the transaction cost.
    
    Strips whitespace, ignores empty lines or headers (e.g., lines starting 
    with 'tx_id'). Splits the line by comma and takes the last element as 
    the cost value.
    
    Args:
        line: A string representing a single line from a CSV file.
        
    Returns:
        A tuple containing the cost as a float and as a Decimal, 
        or None if the line is invalid, empty, a header, or cannot be parsed.
    """
    stripped = line.strip()
    
    # Ignore empty lines and standard headers
    if not stripped or stripped.lower().startswith('tx_id'):
        return None
        
    try:
        parts = stripped.split(',')
        cost_str = parts[-1].strip()
        return float(cost_str), Decimal(cost_str)
    except ValueError:
        return None


def audit_stream(lines: Iterable[str]) -> DriftReport:
    """
    Audits a stream of transaction lines to detect floating-point drift.
    
    Iterates through the provided lines, parsing each for a cost value. 
    Accumulates the total using both standard IEEE 754 floating-point 
    arithmetic and exact base-10 decimal arithmetic.
    
    Args:
        lines: An iterable of strings, where each string is a CSV line.
        
    Returns:
        A DriftReport containing the float total, decimal total, 
        the calculated divergence, and the count of valid transactions.
    """
    sum_f = 0.0
    sum_d = Decimal('0.0')
    count = 0
    
    for line in lines:
        parsed = parse_cost(line)
        if parsed is not None:
            f_val, d_val = parsed
            sum_f += f_val
            sum_d += d_val
            count += 1
            
    divergence = float(Decimal(str(sum_f)) - sum_d)
    
    return DriftReport(sum_f, sum_d, divergence, count)