import json
import hashlib
from typing import Optional, Iterable
from collections import defaultdict
import models

REQUIRED_KEYS = {"session_id", "prompt_tokens", "completion_tokens", "prompt_text", "status"}


def parse_log_line(raw_line: str) -> Optional[dict]:
    """Parse a raw JSON log line into a normalized dictionary.

    Strips whitespace, skips empty lines, and validates required keys.
    Returns None if parsing fails or required keys are missing.
    """
    line = raw_line.strip()
    if not line:
        return None
    try:
        data = json.loads(line)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict) or not REQUIRED_KEYS.issubset(data.keys()):
        return None
    return {
        "session_id": str(data["session_id"]),
        "prompt_tokens": int(data["prompt_tokens"]),
        "completion_tokens": int(data["completion_tokens"]),
        "prompt_text": str(data["prompt_text"]),
        "status": str(data["status"]),
    }


def run_audit_stream(events: Iterable[dict], cost_per_1k: float = 0.005) -> models.AuditReport:
    """Execute a single-pass audit over an iterable of log event dicts.

    Tracks prompt hashes, rolling token counts, cost drift, and error retries.
    Returns a structured AuditReport with detected inefficiencies.
    """
    sessions = set()
    total_tokens = 0
    prompt_hashes = defaultdict(int)
    session_context = defaultdict(int)
    retry_tracker = defaultdict(lambda: {'last_hash': '', 'count': 0})
    inefficiencies = []
    waste_tokens = 0
    hash_tokens = defaultdict(int)

    for evt in events:
        if not REQUIRED_KEYS.issubset(evt.keys()):
            continue
        sid = evt["session_id"]
        sessions.add(sid)
        tok_sum = evt["prompt_tokens"] + evt["completion_tokens"]
        total_tokens += tok_sum

        p_hash = hashlib.sha256(evt["prompt_text"].encode("utf-8")).hexdigest()[:16]
        prompt_hashes[p_hash] += 1
        hash_tokens[p_hash] += tok_sum
        session_context[sid] += tok_sum

        tracker = retry_tracker[sid]
        if evt["status"] == "error":
            if tracker["last_hash"] == p_hash:
                tracker["count"] += 1
            else:
                tracker["last_hash"] = p_hash
                tracker["count"] = 1
        else:
            tracker["last_hash"] = p_hash
            tracker["count"] = 0

    for h, count in prompt_hashes.items():
        if count > 3:
            inefficiencies.append(models.InefficiencyPattern(
                pattern_type="prompt_duplication", session_id="global",
                count=count, details=f"Hash {h} repeated {count}x"
            ))
            waste_tokens += hash_tokens[h]

    for sid, ctx in session_context.items():
        if ctx > 8000:
            inefficiencies.append(models.InefficiencyPattern(
                pattern_type="context_bloat", session_id=sid,
                count=1, details=f"Context size {ctx}"
            ))
            waste_tokens += ctx

    for sid, tr in retry_tracker.items():
        if tr["count"] > 2:
            inefficiencies.append(models.InefficiencyPattern(
                pattern_type="retry_storm", session_id=sid,
                count=tr["count"], details="Consecutive errors"
            ))
            waste_tokens += session_context[sid]

    estimated_cost = (total_tokens / 1000.0) * cost_per_1k
    drift_score = (waste_tokens / total_tokens) if total_tokens > 0 else 0.0
    return models.AuditReport(
        total_sessions=len(sessions), total_tokens=total_tokens,
        estimated_cost=estimated_cost, inefficiencies=inefficiencies,
        drift_score=drift_score
    )