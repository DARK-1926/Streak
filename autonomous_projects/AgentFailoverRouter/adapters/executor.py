from typing import Callable, Tuple, Dict, Any, List
import time
from core.models import CallRecord, FailoverPolicy, RoutingDecision
from core.router import evaluate_route
from core.recovery import snapshot_context, restore_context


def execute_with_failover(
    target_runner: Callable[[Dict[str, Any]], Dict[str, Any]],
    fallback_runner: Callable[[Dict[str, Any]], Dict[str, Any]],
    context: Dict[str, Any],
    policy: FailoverPolicy
) -> Tuple[Dict[str, Any], CallRecord]:
    """
    Executes a target callable with automatic failover to a fallback based on policy.

    This function isolates side effects by:
      - Snapshotting the initial context state.
      - Attempting execution with the target runner.
      - Measuring latency and capturing success/failure.
      - Evaluating failover conditions using call history.
      - Restoring context state before invoking fallback if needed.

    Args:
        target_runner: Primary callable to execute; accepts context dict, returns result dict.
        fallback_runner: Secondary callable used on failover; same signature as target_runner.
        context: Mutable context dictionary passed to runners; may be modified during execution.
        policy: Failover policy defining thresholds and fallback target.

    Returns:
        A tuple containing:
          - The result dictionary from either target or fallback runner.
          - A CallRecord representing the final executed call (either target or fallback).

    Raises:
        SystemExit or KeyboardInterrupt are re-raised immediately.
        All other exceptions are caught and converted into failure CallRecords.
    """
    # Snapshot initial context for potential restoration
    context_snapshot = snapshot_context(context)
    session_history: List[CallRecord] = []
    current_target = "primary"

    # Attempt primary execution
    start_time = time.perf_counter()
    try:
        result = target_runner(context)
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        record = CallRecord(
            target=current_target,
            success=True,
            latency_ms=latency_ms,
            error_code=None,
            timestamp=time.time()
        )
        session_history.append(record)
        return result, record

    except (SystemExit, KeyboardInterrupt):
        raise

    except Exception as e:
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        error_code = type(e).__name__
        record = CallRecord(
            target=current_target,
            success=False,
            latency_ms=latency_ms,
            error_code=error_code,
            timestamp=time.time()
        )
        session_history.append(record)

        # Evaluate whether failover is needed
        routing_decision: RoutingDecision = evaluate_route(
            history=session_history,
            policy=policy,
            current_target=current_target
        )

        if routing_decision.should_failover:
            # Restore original context state before fallback
            restored_context = restore_context(context_snapshot)
            # Merge any changes that might have occurred in context during target execution?
            # According to recovery design, we restore to snapshot and then apply diff if needed,
            # but here we simply restore to pre-execution state as per problem statement.
            fallback_start = time.perf_counter()
            try:
                result = fallback_runner(restored_context)
                # Return the original failed record to indicate that failover was triggered
                # due to primary failure, even though fallback succeeded
                return result, record

            except (SystemExit, KeyboardInterrupt):
                raise

            except Exception as e:
                fallback_latency = (time.perf_counter() - fallback_start) * 1000.0
                fallback_error_code = type(e).__name__
                fallback_record = CallRecord(
                    target=policy.fallback_target,
                    success=False,
                    latency_ms=fallback_latency,
                    error_code=fallback_error_code,
                    timestamp=time.time()
            )
            return {}, fallback_record

    # If no failover, return empty result and original failure record
    return {}, record