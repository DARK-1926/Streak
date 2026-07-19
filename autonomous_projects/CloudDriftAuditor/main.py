"""
main.py

CLI orchestrator for CloudDriftAuditor.
Wires the robust I/O handler to the mathematical drift detection engine.
"""

import argparse
import sys
from decimal import Decimal

from drift_engine import audit_stream
from io_handler import stream_billing_file


def main() -> int:
    """
    Parses command-line arguments, orchestrates the billing audit, 
    and prints the resulting report.
    
    Returns:
        int: Exit status code (0 for success, 1 for anomalies or errors).
    """
    parser = argparse.ArgumentParser(
        description="CloudDriftAuditor: Detect floating-point billing anomalies."
    )
    parser.add_argument(
        "filepath", 
        type=str, 
        help="Path to the billing CSV file to audit."
    )
    
    args = parser.parse_args()

    try:
        lines = stream_billing_file(args.filepath)
        report = audit_stream(lines)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except PermissionError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return 1

    print("=== CloudDriftAuditor Report ===")
    print(f"Total Float:   {report.total_float}")
    print(f"Total Decimal: {report.total_decimal}")
    print(f"Drift Amount:  {report.drift}")
    print(f"Max Charge:    {report.max_charge}")
    
    if report.anomalies:
        print("\nAnomalies Detected:")
        for anomaly in report.anomalies:
            print(f"  - {anomaly}")
    else:
        print("\nAnomalies: None")

    if report.anomalies or report.drift > Decimal('0.01'):
        print("\n[ALERT] Drift or anomalies exceed acceptable thresholds.")
        return 1
        
    print("\n[OK] Billing audit passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())