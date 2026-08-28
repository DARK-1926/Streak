"""
Core logic for AgentSwarmLoopAuditor.

Provides pure functions for parsing agent actions and detecting degenerate
behavioral loops using a single-pass sliding window approach.
"""

import json
from typing import Optional, Iterable, Dict, List

from models import AgentAction, LoopReport


def parse_action(json_str: str) -> Optional[AgentAction]:
    """
    Parses a JSON string into an AgentAction.
    
    Catches json.JSONDecodeError, KeyError, ValueError, and TypeError,
    returning None on failure to ensure robust streaming.
    
    Args:
        json_str: A JSON-formatted string representing an agent action.
        
    Returns:
        An AgentAction instance if parsing and validation succeed, else None.
    """
    try:
        data = json.loads(json_str)
        return AgentAction(
            session_id=data["session_id"],
            tool_name=data["tool_name"],
            args_hash=data["args_hash"],
            tokens_used=data["tokens_used"]
        )
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        return None


def audit_sessions(actions: Iterable[AgentAction]) -> LoopReport:
    """
    Analyzes an iterable of AgentActions to detect infinite loops and thrashing.
    Analyzes an iterable of AgentActions to detect infinite loops and thrashing.

    Maintains a sliding window of the last 10 actions per session.
    Detects 'exact_loop' if the last 3 actions are identical.
    Detects 'thrashing' if the last 4 actions alternate (A-B-A-B).

    Args:
        actions: An iterable stream of AgentAction objects.

    Returns:
        A single LoopReport aggregating all detected loops across sessions.
    """
    reports: Dict[str, List[LoopReport]] = {}
    session_states: Dict[str, Dict] = {}

    for action in actions:
        sid = action.session_id
        if sid not in session_states:
            session_states[sid] = {"history": [], "in_exact": False, "in_thrash": False}
            reports[sid] = []

        state = session_states[sid]
        history: List[AgentAction] = state["history"]
        history.append(action)

        if len(history) > 10:
            history.pop(0)

        is_exact = (
            len(history) >= 3 and
            (history[-3].tool_name, history[-3].args_hash) ==
            (history[-2].tool_name, history[-2].args_hash) ==
            (history[-1].tool_name, history[-1].args_hash)
        )

        is_thrash = (
            len(history) >= 4 and
            (history[-4].tool_name, history[-4].args_hash) == (history[-2].tool_name, history[-2].args_hash) and
            (history[-3].tool_name, history[-3].args_hash) == (history[-1].tool_name, history[-1].args_hash) and
            (history[-4].tool_name, history[-4].args_hash) != (history[-3].tool_name, history[-3].args_hash)
        )

        if is_exact:
            if not state["in_exact"]:
                state["in_exact"] = True
                state["in_thrash"] = False
                # First time entering exact loop, initialize tracking
                state["exact_loop_start_idx"] = len(history) - 3
            # Accumulate tokens for this action if in exact loop
            if state["in_exact"]:
                # Add tokens for the current action to the latest exact loop report
                if reports[sid] and reports[sid][-1].loop_type == "exact_loop" and not hasattr(reports[sid][-1], '_finalized'):
                    reports[sid][-1].wasted_tokens += action.tokens_used
                    reports[sid][-1].count += 1
                else:
                    # Create new report for this exact loop
                    wasted = sum(a.tokens_used for a in history[-3:])
                    new_report = LoopReport(session_id=sid, loop_type="exact_loop", count=3, wasted_tokens=wasted, exact_loops=1, alternating_loops=0)
                    reports[sid].append(new_report)
        elif state["in_exact"]:  # is_exact is False but was True
            state["in_exact"] = False

        if is_thrash:
            if not state["in_thrash"]:
                state["in_thrash"] = True
                state["in_exact"] = False
                # First time entering thrash loop, initialize tracking
                state["thrash_loop_start_idx"] = len(history) - 4
            # Accumulate tokens for this action if in thrash loop
            if state["in_thrash"]:
                # Add tokens for the current action to the latest thrash loop report
                if reports[sid] and reports[sid][-1].loop_type == "thrashing" and not hasattr(reports[sid][-1], '_finalized'):
                    reports[sid][-1].wasted_tokens += action.tokens_used
                    reports[sid][-1].count += 1
                else:
                    # Create new report for this thrash loop
                    wasted = sum(a.tokens_used for a in history[-4:])
                    new_report = LoopReport(session_id=sid, loop_type="thrashing", count=2, wasted_tokens=wasted, exact_loops=0, alternating_loops=1)
                    reports[sid].append(new_report)
        elif state["in_thrash"]:  # is_thrash is False but was True
            state["in_thrash"] = False
    
    # Aggregate all reports into a single LoopReport
    total_exact_loops = sum(
        report.count for session_reports in reports.values() for report in session_reports if report.loop_type == "exact_loop"
    )
    total_thrashing_loops = sum(
        report.count for session_reports in reports.values() for report in session_reports if report.loop_type == "thrashing"
    )
    total_wasted_tokens = sum(
        report.wasted_tokens for session_reports in reports.values() for report in session_reports
    )
    
    # Return a dummy session_id since we're aggregating
    return LoopReport(
        session_id="aggregated",
        loop_type="aggregated",
        count=total_exact_loops + total_thrashing_loops,
        wasted_tokens=total_wasted_tokens,
        exact_loops=total_exact_loops,
        alternating_loops=total_thrashing_loops
    )
            
    return reports