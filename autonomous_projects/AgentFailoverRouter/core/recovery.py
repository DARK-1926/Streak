import json
from typing import Any


def snapshot_context(context: dict[str, Any]) -> bytes:
    """
    Deterministically serializes a context dictionary to a JSON byte string.
    
    Uses sorted keys and compact encoding to ensure consistent output for identical inputs.
    Returns UTF-8 encoded bytes of the JSON representation.
    """
    return json.dumps(context, sort_keys=True, separators=(',', ':')).encode('utf-8')


def restore_context(snapshot: bytes) -> dict[str, Any]:
    """
    Deserializes a context snapshot from bytes back into a dictionary.
    
    Decodes UTF-8 bytes and parses JSON. Returns an empty dictionary if decoding fails
    due to malformed JSON or encoding issues.
    """
    try:
        decoded = snapshot.decode('utf-8')
        return json.loads(decoded)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def compute_context_diff(base: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    """
    Computes a minimal diff between two context dictionaries.
    
    Returns a new dictionary containing only keys that are either:
      - present in `current` but not in `base`, or
      - present in both but with different values.
      
    The result is suitable for replaying state changes after failover.
    """
    return {
        key: current[key]
        for key in current
        if base.get(key) != current[key]
    }