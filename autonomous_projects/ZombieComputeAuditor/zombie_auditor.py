"""
Core logic for ZombieComputeAuditor.

This module provides pure functions for parsing and aggregating agent telemetry logs
without any side effects or file I/O operations.
"""

import json
from typing import Any, Dict, Iterable


def audit_agent_yield(
    log_lines: Iterable[str], 
    cost_threshold: float = 10.0, 
    task_threshold: int = 0
) -> dict:
    """
    Parse JSONL log lines and aggregate compute cost and task completion per agent.
    
    Flags agents as 'zombies' if their total compute cost meets or exceeds the 
    cost_threshold while their total tasks completed are at or below the task_threshold.
    Malformed or incomplete records are gracefully ignored.
    
    Args:
        log_lines: An iterable of strings, where each string is a JSON-encoded log line.
        cost_threshold: The minimum total compute cost to consider an agent a zombie.
        task_threshold: The maximum total tasks completed to consider an agent a zombie.
        
    Returns:
        A dictionary mapping agent_id to a dictionary containing 'total_cost', 
        'total_tasks', and 'is_zombie' status.
    """
    stats: Dict[str, Dict[str, Any]] = {}
    
    for line in log_lines:
        try:
            record = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue
            
        if not isinstance(record, dict):
            continue
            
        required_keys = {"agent_id", "compute_cost", "tasks_completed"}
        if not required_keys.issubset(record.keys()):
            continue
            
        agent_id = record["agent_id"]
        
        try:
            compute_cost = float(record["compute_cost"])
            tasks_completed = int(record["tasks_completed"])
        except (ValueError, TypeError):
            continue
            
        if agent_id not in stats:
            stats[agent_id] = {"total_cost": 0.0, "total_tasks": 0}
            
        stats[agent_id]["total_cost"] += compute_cost
        stats[agent_id]["total_tasks"] += tasks_completed
        
    for agent_data in stats.values():
        agent_data["is_zombie"] = (
            agent_data["total_cost"] >= cost_threshold and 
            agent_data["total_tasks"] <= task_threshold
        )
        
    return stats