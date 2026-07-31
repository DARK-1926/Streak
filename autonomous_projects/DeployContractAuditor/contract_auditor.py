"""
Contract auditor module for DeployContractAuditor.

This module provides the core state machine logic for auditing deployment logs
against a predefined contract of required sequential actions.
"""

from typing import Any, Dict, Iterable, List


def audit_deployment(log_stream: Iterable[Dict[str, Any]], contract: List[str]) -> Dict[str, Any]:
    """
    Audit a deployment log stream against a contract of required sequential actions.

    This pure state machine function processes the log stream in a single pass,
    tracking compliance with the contract and identifying unauthorized actions
    or missing required actions (amnesia events).

    Args:
        log_stream: An iterable of parsed log entries (dictionaries)
        contract: A list of required sequential action names

    Returns:
        A dictionary containing audit results with the following keys:
        - total_actions: Total number of actions processed
        - compliance_rate: Fraction of contract actions completed (0.0 to 1.0)
        - unauthorized_actions: List of actions not in the expected sequence
        - amnesia_events: List of required actions that were never performed
        - is_compliant: Boolean indicating if all required actions were performed
                       in the correct order with no unauthorized actions
    """
    log_entries = list(log_stream)
    log_actions = [entry.get('action', 'UNKNOWN') for entry in log_entries]

    contract_index = 0
    unauthorized_actions = []
    amnesia_events = []
    is_order_broken = False
    is_polluted = False
    total_actions = len(log_actions)
    processed_future_actions = []

    for i, action in enumerate(log_actions):

        if len(contract) == 0:
            continue

        if action not in contract:
            unauthorized_actions.append(action)
            is_polluted = True
            continue

        if is_order_broken:
            unauthorized_actions.append(action)
            continue

        if is_polluted:
            if contract_index < len(contract) and action == contract[contract_index]:
                continue
            unauthorized_actions.append(action)
            continue

        if contract_index >= len(contract):
            if action in contract:
                if not is_order_broken:
                    amnesia_events.extend(processed_future_actions)
                    unauthorized_actions.extend(processed_future_actions)
                unauthorized_actions.append(action)
                is_order_broken = True
            else:
                unauthorized_actions.append(action)
                is_polluted = True
            continue

        if action == contract[contract_index]:
            contract_index += 1
        else:
            # If the current action is not the expected one, check if it's a future contract action
            if action in contract[contract_index + 1:]:
                # Action is from the contract but we've skipped some steps
                # Add the skipped steps to amnesia_events
                next_index = contract.index(action, contract_index)
                for i in range(contract_index, next_index):
                    amnesia_events.append(contract[i])
                contract_index = next_index + 1
                processed_future_actions.append(action)
            else:
                # Action is either not in contract or is a repeated/previous contract action
                if action in contract:
                    # This is a contract action that's not in the right sequence (repeated or previous)
                    if not is_order_broken:
                        amnesia_events.extend(processed_future_actions)
                        unauthorized_actions.extend(processed_future_actions)
                    unauthorized_actions.append(action)
                    is_order_broken = True
                else:
                    # Action is not in contract at all
                    unauthorized_actions.append(action)
                    is_polluted = True
                    is_order_broken = True

    # After processing all log entries, check for any remaining required actions
    if contract_index < len(contract):
        for action in contract[contract_index:]:
            if action not in unauthorized_actions:
                amnesia_events.append(action)

    # Determine if the deployment is compliant
    is_compliant = len(unauthorized_actions) == 0 and len(amnesia_events) == 0

    # Calculate compliance rate
    if len(contract) > 0:
        compliance_rate = len([a for a in contract if a not in amnesia_events and a not in unauthorized_actions]) / len(contract)
    else:
        compliance_rate = 1.0

    return {
        'total_actions': total_actions,
        'compliance_rate': compliance_rate,
        'unauthorized_actions': unauthorized_actions,
        'amnesia_events': amnesia_events,
        'is_compliant': is_compliant
    }