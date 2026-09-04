import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

from fuzzer import FuzzVariant


@dataclass(frozen=True)
class ValidationReport:
    """Represents the result of executing a parser against a fuzz variant."""
    variant_strategy: str
    success: bool
    exception_type: Optional[str]
    exception_msg: Optional[str]
    execution_time_ms: float
    result: Optional[Any] = None


def validate_variant(variant: FuzzVariant, parser_fn: Callable[[dict], Any]) -> ValidationReport:
    """Execute a parser callable against a fuzz variant and capture the result.

    Args:
        variant: The FuzzVariant containing the payload and strategy metadata.
        parser_fn: A callable that accepts a dictionary and returns any value.

    Returns:
        A ValidationReport detailing success, exceptions, and execution time.
    """
    start_time = time.perf_counter()
    success = False
    exc_type: Optional[str] = None
    exc_msg: Optional[str] = None
    res: Optional[Any] = None

    try:
        res = parser_fn(variant.payload)
        success = True
    except (SystemExit, KeyboardInterrupt):
        raise
    except Exception as e:
        exc_type = type(e).__name__
        exc_msg = str(e)
    finally:
        end_time = time.perf_counter()

    execution_time_ms = (end_time - start_time) * 1000.0

    return ValidationReport(
        variant_strategy=variant.strategy,
        success=success,
        exception_type=exc_type,
        exception_msg=exc_msg,
        execution_time_ms=execution_time_ms,
        result=res
    )