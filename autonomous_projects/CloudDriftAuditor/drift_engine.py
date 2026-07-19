"""
drift_engine.py

Core mathematical engine for CloudDriftAuditor.
Performs single-pass drift detection comparing IEEE 754 float accumulation 
against exact decimal.Decimal accumulation.
"""

import csv
from decimal import Decimal, InvalidOperation
from typing import Iterable, List, NamedTuple


class AuditReport(NamedTuple):
    """
    Represents the final report of a billing audit stream.
    
    Attributes:
        total_float: The accumulated total using IEEE 754 floating-point arithmetic.
        total_decimal: The accumulated total using exact decimal arithmetic.
        drift: The absolute difference between the float and decimal accumulations.
        max_charge: The highest single charge encountered in the stream.
        anomalies: A list of string descriptions for charges exceeding the spike threshold.
    """
    total_float: float
    total_decimal: Decimal
    drift: Decimal
    max_charge: Decimal
    anomalies: List[str]


def audit_stream(
    lines: Iterable[str], 
    spike_threshold: Decimal = Decimal('10000.00')
) -> AuditReport:
    """
    Performs a strict single-pass audit over an iterable of CSV lines.
    
    Parses each line for timestamp, service, and cost. Accumulates the cost
    using both float and Decimal representations to detect precision drift.
    Identifies anomalous spikes based on the provided threshold.
    
    Args:
        lines: An iterable of strings representing CSV rows.
        spike_threshold: The decimal threshold above which a charge is flagged as an anomaly.
        
    Returns:
        An AuditReport containing the accumulated totals, drift, max charge, and anomalies.
    """
    total_float: float = 0.0
    total_decimal: Decimal = Decimal('0.0')
    max_charge: Decimal = Decimal('0.0')
    anomalies: List[str] = []
    
    reader = csv.reader(lines)
    
    for row in reader:
        if len(row) < 3:
            continue
            
        timestamp, service, cost_str = row[0], row[1], row[2]
        
        if cost_str.strip().lower() == 'cost':
            continue
            
        try:
            clean_cost_str = cost_str.strip()
            cost_decimal = Decimal(clean_cost_str)
            cost_float = float(clean_cost_str)
        except (InvalidOperation, ValueError, ArithmeticError):
            continue
            
        total_float += cost_float
        total_decimal += cost_decimal
        
        if cost_decimal > max_charge:
            max_charge = cost_decimal
            
        if cost_decimal > spike_threshold:
            anomalies.append(f'SPIKE: {service.strip()} charged {cost_decimal}')
            
    drift = abs(Decimal(str(total_float)) - total_decimal)
    
    return AuditReport(
        total_float=total_float,
        total_decimal=total_decimal,
        drift=drift,
        max_charge=max_charge,
        anomalies=anomalies
    )