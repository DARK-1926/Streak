"""
CLI module for DeployContractAuditor.

This module provides the command-line interface for the deployment contract auditor.
It accepts log file path and contract specification, then performs the audit.
"""

import argparse
import json
import os
import sys
from typing import List

from contract_auditor import audit_deployment
from log_parser import parse_log_stream


def main() -> None:
    """
    Main entry point for the DeployContractAuditor CLI.
    
    Parses command-line arguments, validates inputs, performs the audit,
    and outputs results or exits with appropriate error codes.
    """
    parser = argparse.ArgumentParser(
        description="Audit deployment logs against a predefined contract."
    )
    parser.add_argument(
        "--log-file",
        required=True,
        help="Path to the JSONL log file to audit"
    )
    parser.add_argument(
        "--contract",
        required=True,
        help="Comma-separated string of required sequential steps (e.g., 'lint,test,build,deploy')"
    )
    
    args = parser.parse_args()
    
    # Validate that the log file exists
    if not os.path.exists(args.log_file):
        print(f"Error: Log file does not exist: {args.log_file}", file=sys.stderr)
        sys.exit(1)
    
    # Parse the contract string into a list
    contract: List[str] = [step.strip() for step in args.contract.split(',') if step.strip()]
    
    try:
        # Parse the log stream
        log_stream = parse_log_stream(args.log_file)
        
        # Perform the audit
        audit_results = audit_deployment(log_stream, contract)
        
        # Print the results as formatted JSON
        print(json.dumps(audit_results, indent=2))
        
        # Exit with code 2 if not compliant
        if not audit_results['is_compliant']:
            sys.exit(2)
            
    except Exception as e:
        print(f"Error during audit: {str(e)}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()