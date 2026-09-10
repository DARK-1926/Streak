import hashlib
import json
from typing import Any, Dict


def normalize_and_hash(content: str) -> str:
    """
    Normalize the given string content and compute its SHA-256 hash.

    Normalization includes:
        - Stripping leading and trailing whitespace.
        - Converting line endings to Unix style (\\n).
        - Converting the entire string to lowercase.

    The normalized string is then encoded as UTF-8 and hashed using SHA-256.
    The resulting hash is returned as a hexadecimal string.

    Args:
        content (str): The input string to normalize and hash.

    Returns:
        str: The SHA-256 hexdigest of the normalized content.
    """
    normalized = content.strip().replace('\r\n', '\n').replace('\r', '\n').lower()
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def stable_hash(data: Dict[str, Any]) -> str:
    """
    Compute a deterministic SHA-256 hash of a dictionary by serializing it to a
    stable JSON representation.

    Uses json.dumps with sort_keys=True and minimal separators to ensure consistent
    serialization across runs and environments.

    Args:
        data (Dict[str, Any]): The dictionary to hash.

    Returns:
        str: The SHA-256 hexdigest of the serialized data.
    """
    serialized = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()