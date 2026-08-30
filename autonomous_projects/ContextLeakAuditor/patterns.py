from typing import Iterable, Dict, Any, List, Set
from core import LeakSignature


def compute_text_signature(text: str) -> int:
    """
    Compute a deterministic integer signature for text using a sorted
    character trigram shingle approach. Normalizes whitespace to ensure
    robust matching across minor formatting variations. Pure and stdlib-only.
    """
    if not isinstance(text, str) or len(text) < 3:
        return 0

    cleaned = " ".join(text.split())
    if len(cleaned) < 3:
        return 0

    shingles = sorted(cleaned[i:i + 3] for i in range(len(cleaned) - 2))

    h = 0
    for shingle in shingles:
        for char in shingle:
            h = (h * 31 + ord(char)) & 0xFFFFFFFF
    return h


def scan_redundancy(events: Iterable[Dict[str, Any]]) -> List[LeakSignature]:
    """
    Scan an iterable of agent event logs in a single pass to detect
    redundant context injections. Tracks seen payload signatures in a set,
    flags duplicates, and assigns severity based on repetition count.
    Pure function with no side-effects or external dependencies.
    """
    signatures: List[LeakSignature] = []
    seen_hashes: Set[int] = set()
    repetition_counts: Dict[int, int] = {}
    step_counter = 0

    for event in events:
        step_counter += 1
        try:
            step = int(event.get("step", step_counter))
            payload = event.get("system") or event.get("tool_output")

            if not isinstance(payload, str) or not payload.strip():
                continue

            sig = compute_text_signature(payload)

            if sig in seen_hashes:
                count = repetition_counts.get(sig, 1) + 1
                repetition_counts[sig] = count

                if count >= 5:
                    severity = "high"
                elif count >= 3:
                    severity = "medium"
                else:
                    severity = "low"

                wasted_tokens = max(1, len(payload) // 4)
                signatures.append(LeakSignature(
                    type="redundant_injection",
                    step=step,
                    severity=severity,
                    tokens_wasted=wasted_tokens
                ))
            else:
                seen_hashes.add(sig)
                repetition_counts[sig] = 1

        except (TypeError, KeyError, ValueError, AttributeError):
            continue

    return signatures