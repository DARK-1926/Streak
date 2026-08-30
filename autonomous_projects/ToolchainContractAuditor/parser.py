import json
from typing import Iterable, List, Dict, Any, Tuple


def parse_contracts(lines: Iterable[str]) -> List[Dict[str, Any]]:
    """
    Parse tool contract definitions from an iterable of JSON/JSONL strings.

    Iterates exactly once over the input, parsing each line as JSON and
    validating the presence of required keys. Invalid lines are skipped.

    Args:
        lines: An iterable of strings, each representing a JSON object.

    Returns:
        A list of validated contract dictionaries.
    """
    contracts: List[Dict[str, Any]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            data = json.loads(stripped)
            # Validate required keys explicitly to trigger KeyError if missing
            _ = data['name']
            _ = data['input_schema']
            _ = data['output_schema']
            contracts.append(data)
        except (json.JSONDecodeError, KeyError):
            continue
    return contracts


def parse_chain_links(lines: Iterable[str]) -> List[Tuple[str, str]]:
    """
    Parse execution chain sequences from an iterable of strings.

    Supports two formats per line:
    1. Plain text: 'ToolA->ToolB'
    2. JSON object: {"from": "ToolA", "to": "ToolB"}

    Iterates exactly once over the input. Invalid or malformed lines are skipped.

    Args:
        lines: An iterable of strings representing chain links.

    Returns:
        A list of tuples representing the execution flow (source, target).
    """
    links: List[Tuple[str, str]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            if stripped.startswith('{'):
                data = json.loads(stripped)
                src = data['from']
                tgt = data['to']
                links.append((str(src), str(tgt)))
            elif '->' in stripped:
                parts = stripped.split('->')
                if len(parts) == 2:
                    src, tgt = parts[0].strip(), parts[1].strip()
                    if src and tgt:
                        links.append((src, tgt))
        except (json.JSONDecodeError, KeyError, TypeError):
            continue
    return links