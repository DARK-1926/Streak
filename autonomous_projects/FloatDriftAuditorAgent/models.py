"""
Pure data models and interface contracts for the FloatDriftAuditorAgent.

This module defines the immutable data structures used to represent
the results of billing drift audits, ensuring strict typing and 
predictable behavior across the application.
"""

from decimal import Decimal
from typing import NamedTuple


class DriftReport(NamedTuple):
    """
    Immutable data structure representing the results of a billing drift audit.
    
    This report encapsulates the comparison between standard IEEE 754 
    floating-point aggregation and exact base-10 decimal aggregation, 
    highlighting any financial discrepancies caused by float accumulation drift.
    
Attributes:
        float_total: The aggregated total calculated using standard binary
                     floating-point arithmetic.
        decimal_total: The aggregated total calculated using exact base-10
                       decimal arithmetic.
        divergence: The exact mathematical difference between the float total
                    and the decimal total (float_total - decimal_total).
        transaction_count: The total number of individual transactions
                           processed during the audit.
    """
    float_total: float
    decimal_total: Decimal
    divergence: float
    transaction_count: int