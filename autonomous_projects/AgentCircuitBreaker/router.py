from typing import Dict, List, Union, Any

from models import CircuitState, RoutingDecision


def simulate_fallback_routing(
    states: Dict[str, CircuitState],
    policy: Union[List[str], Dict[str, List[str]]],
) -> Union[RoutingDecision, List[RoutingDecision]]:
    if isinstance(policy, list):
        providers = policy
        selected_provider = providers[-1]
        reason = f"{providers[0]} is OPEN"
        is_fallback = True
        for provider in providers:
            circuit = states.get(provider)
            current_state = circuit.state if circuit else "CLOSED"
            if current_state in ("CLOSED", "HALF-OPEN"):
                selected_provider = provider
                is_fallback = provider != providers[0]
                primary_state = states.get(providers[0]).state if states.get(providers[0]) else "CLOSED"
                reason = f"{providers[0]} is {primary_state}"
                break
        return RoutingDecision(task="default", provider=selected_provider, is_fallback=is_fallback, reason=reason)

    decisions: List[RoutingDecision] = []
    for task, providers in sorted(policy.items()):
        if not providers:
            continue
        selected_provider = providers[-1]
        reason = "ALL_OPEN_FORCE_FALLBACK"
        is_fallback = True
        for provider in providers:
            circuit = states.get(provider)
            current_state = circuit.state if circuit else "CLOSED"
            if current_state in ("CLOSED", "HALF-OPEN"):
                selected_provider = provider
                is_fallback = provider != providers[0]
                reason = "AVAILABLE"
                break
        decisions.append(RoutingDecision(task=task, provider=selected_provider, is_fallback=is_fallback, reason=reason))
    return decisions