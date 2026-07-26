"""
Core state machine engine for the PresenceDriftAuditor.
"""

from dataclasses import dataclass
from typing import Dict, Iterable

from models import AuditReport, LogEvent


@dataclass
class _AgentState:
    """
    Private helper dataclass to track the state of a single agent.
    
    Attributes:
        last_seen: Timestamp of the last observed event.
        is_connected: Boolean indicating current connection status.
        current_process_id: The process ID currently associated with the agent.
        flap_count: Number of detected connection flaps.
        migration_count: Number of detected process migrations.
    """
    last_seen: float = 0.0
    is_connected: bool = False
    current_process_id: str = ""
    flap_count: int = 0
    migration_count: int = 0


def audit_presence(
    events: Iterable[LogEvent], 
    flap_threshold_sec: float = 5.0
) -> Dict[str, AuditReport]:
    """
    Processes an iterable of log events in a single O(N) pass to audit agent presence.
    
    Tracks connection durations, detects process migrations, and calculates 
    a deterministic stability score based on flap penalties.
    
    Args:
        events: An iterable of LogEvent objects.
        flap_threshold_sec: The maximum time in seconds between a disconnect 
                            and reconnect to be considered a flap.
                            
    Returns:
        A dictionary mapping agent_id to their corresponding AuditReport.
    """
    states: Dict[str, _AgentState] = {}
    
    for event in events:
        if event.agent_id not in states:
            states[event.agent_id] = _AgentState()
            
        state = states[event.agent_id]
        
        # Flapping logic
        if event.event_type == 'CONNECT':
            if not state.is_connected:
                if state.last_seen > 0.0 and (event.timestamp - state.last_seen) <= flap_threshold_sec:
                    state.flap_count += 1
            state.is_connected = True
        elif event.event_type == 'DISCONNECT':
            state.is_connected = False
            
        # Migration logic
        if event.event_type in ('CONNECT', 'HEARTBEAT'):
            if state.current_process_id and event.process_id != state.current_process_id:
                state.migration_count += 1
            state.current_process_id = event.process_id
            
        state.last_seen = event.timestamp
        
    # Construct final reports
    reports: Dict[str, AuditReport] = {}
    for agent_id, state in states.items():
        stability_score = max(0.0, 1.0 - (state.flap_count * 0.1))
        is_flapping = state.flap_count > 0
        
        reports[agent_id] = AuditReport(
            agent_id=agent_id,
            stability_score=stability_score,
            is_flapping=is_flapping,
            migrations=state.migration_count
        )
        
    return reports