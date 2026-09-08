from typing import Iterable
from core.models import CallRecord, FailoverPolicy, RouterState, RoutingDecision


def update_state(state: RouterState, record: CallRecord, window_size: int = 50) -> RouterState:
    """
    Returns a new RouterState with updated metrics based on the given CallRecord.

    Increments total_calls, increments total_failures if the call was not successful,
    and appends the call's latency to rolling_latencies (capped at window_size entries for memory safety).
    """
    total_calls = state.total_calls + 1
    total_failures = state.total_failures + (0 if record.success else 1)
    new_rolling_latencies = (state.rolling_latencies + [record.latency_ms])[-window_size:]
    return RouterState(
        total_calls=total_calls,
        total_failures=total_failures,
        rolling_latencies=new_rolling_latencies,
        current_target=state.current_target
    )


def evaluate_route(history: Iterable[CallRecord], policy: FailoverPolicy, current_target: str) -> RoutingDecision:
    """
    Evaluates routing decision based on call history and failover policy.
    
    Performs a single-pass accumulation of call metrics, then checks whether failover conditions are met.
    Failover is triggered if:
      - error_rate >= policy.error_rate_threshold, OR
      - average latency >= policy.latency_threshold_ms, OR
      - total failures exceed policy.max_retries.
      
    Returns a RoutingDecision indicating the target to route to and whether failover occurred.
    """
    state = RouterState(
        total_calls=0,
        total_failures=0,
        rolling_latencies=[],
        current_target=current_target
    )

    for record in history:
        state = update_state(state, record)

    error_rate = state.total_failures / max(state.total_calls, 1)
    avg_latency = sum(state.rolling_latencies) / max(len(state.rolling_latencies), 1)

    should_failover = (
        error_rate >= policy.error_rate_threshold or
        avg_latency >= policy.latency_threshold_ms or
        state.total_failures > policy.max_retries
    )

    if should_failover:
        reason_parts = []
        if error_rate >= policy.error_rate_threshold:
            reason_parts.append(f"error_rate={error_rate:.3f} >= {policy.error_rate_threshold}")
        if avg_latency >= policy.latency_threshold_ms:
            reason_parts.append(f"avg_latency={avg_latency:.2f}ms >= {policy.latency_threshold_ms}ms")
        if state.total_failures > policy.max_retries:
            reason_parts.append(f"failures={state.total_failures} > max_retries={policy.max_retries}")
        reason = "; ".join(reason_parts)
        route_to = policy.fallback_target
    else:
        reason = "within policy thresholds"
        route_to = current_target

    updated_state = RouterState(
        total_calls=state.total_calls,
        total_failures=state.total_failures,
        rolling_latencies=state.rolling_latencies,
        current_target=route_to
    )

    return RoutingDecision(
        route_to=route_to,
        should_failover=should_failover,
        reason=reason,
        updated_state=updated_state
    )