"""
Core data structures and parsing logic for the PresenceDriftAuditor.
"""

import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class LogEvent:
    """
    Represents a single parsed log event from an agent.
    
    Attributes:
        timestamp: The time the event occurred.
        agent_id: The unique identifier for the agent.
        session_id: The unique identifier for the session.
        process_id: The unique identifier for the process.
        event_type: The type of event (CONNECT, DISCONNECT, HEARTBEAT).
    """
    timestamp: float
    agent_id: str
    session_id: str
    process_id: str
    event_type: str


@dataclass
class AuditReport:
    """
    Represents the stability audit report for a specific agent.
    
    Attributes:
        agent_id: The unique identifier for the agent.
        stability_score: A float between 0.0 and 1.0 indicating stability.
        is_flapping: Boolean indicating if the agent connection is flapping.
        migrations: The number of process migrations detected.
    """
    agent_id: str
    stability_score: float
    is_flapping: bool
    migrations: int


VALID_EVENT_TYPES = frozenset({'CONNECT', 'DISCONNECT', 'HEARTBEAT'})


def parse_log_line(line: str) -> Optional[LogEvent]:
    """
    Parses a raw JSON string into a LogEvent object.
    
    Validates that the JSON is a dictionary, contains all required keys,
    and that the event_type is one of the allowed types.
    
    Args:
        line: A raw JSON string representing a log event.
        
    Returns:
        A LogEvent instance if parsing and validation succeed, otherwise None.
    """
    try:
        data = json.loads(line)
        
        if not isinstance(data, dict):
            raise TypeError("Parsed JSON is not a dictionary")
            
        event_type = data['event_type']
        if event_type not in VALID_EVENT_TYPES:
            return None
            
        return LogEvent(
            timestamp=float(data['timestamp']),
            agent_id=str(data['agent_id']),
            session_id=str(data['session_id']),
            process_id=str(data['process_id']),
            event_type=str(event_type)
        )
        
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None