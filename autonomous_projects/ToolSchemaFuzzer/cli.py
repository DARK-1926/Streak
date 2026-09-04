import argparse
import importlib.util
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable, List

from normalizer import normalize_schema
from fuzzer import generate_variants
from validator import validate_variant, ValidationReport

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)


def _load_parser_module(module_path: str, func_name: str) -> Callable[[dict], Any]:
    """Dynamically import a user parser module and extract the target callable.

    Args:
        module_path: Filesystem path to the Python module.
        func_name: Name of the function to extract from the module.

    Returns:
        A callable matching the expected parser signature.

    Raises:
        FileNotFoundError: If the module path does not exist.
        ValueError: If the module file is empty.
        ImportError: If the module spec cannot be loaded.
        AttributeError: If the function name is not found in the module.
        TypeError: If the extracted attribute is not callable.
    """
    path = Path(module_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Parser module not found: {path}")
    if os.path.getsize(path) == 0:
        raise ValueError(f"Parser module is empty: {path}")

    module_name = path.stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to load module spec for: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    if not hasattr(module, func_name):
        raise AttributeError(f"Module '{module_name}' has no attribute '{func_name}'")

    parser_fn = getattr(module, func_name)
    if not callable(parser_fn):
        raise TypeError(f"Attribute '{func_name}' is not callable.")

    return parser_fn


def run_audit(schema_path: str, parser_module_path: str, parser_func_name: str) -> List[ValidationReport]:
    """Execute the full fuzzing audit pipeline against a target parser.

    Args:
        schema_path: Path to the JSON schema file.
        parser_module_path: Path to the Python module containing the parser.
        parser_func_name: Name of the parser function to invoke.

    Returns:
        A list of ValidationReport objects detailing the audit results.
    """
    schema_file = Path(schema_path).resolve()
    if not schema_file.is_file():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")
    if os.path.getsize(schema_file) == 0:
        raise ValueError(f"Schema file is empty: {schema_file}")

    logger.info("Loading and normalizing schema from %s", schema_file)
    with open(schema_file, "r", encoding="utf-8") as f:
        raw_schema = json.load(f)

    normalized = normalize_schema(raw_schema)

    logger.info("Dynamically loading parser '%s' from %s", parser_func_name, parser_module_path)
    parser_fn = _load_parser_module(parser_module_path, parser_func_name)

    logger.info("Generating fuzz variants and executing validation harness...")
    reports: List[ValidationReport] = []

    for variant in generate_variants(normalized):
        report = validate_variant(variant, parser_fn)
        reports.append(report)

    logger.info("Audit complete. %d variants processed.", len(reports))

    report_dicts = [
        {
            "variant_strategy": r.variant_strategy,
            "success": r.success,
            "exception_type": r.exception_type,
            "exception_msg": r.exception_msg,
            "execution_time_ms": round(r.execution_time_ms, 4)
        }
        for r in reports
    ]
    print(json.dumps(report_dicts, indent=2))

    return reports


def main() -> None:
    """Parse command-line arguments and trigger the audit pipeline."""
    parser = argparse.ArgumentParser(
        description="ToolSchemaFuzzer: Deterministic stress-testing for agent tool-parsers."
    )
    parser.add_argument(
        "--schema",
        required=True,
        help="Path to the JSON schema file."
    )
    parser.add_argument(
        "--parser-module",
        required=True,
        help="Path to the Python module containing the parser function."
    )
    parser.add_argument(
        "--parser-func",
        required=True,
        help="Name of the parser function to test."
    )

    args = parser.parse_args()

    try:
        run_audit(args.schema, args.parser_module, args.parser_func)
    except FileNotFoundError as e:
        logger.error("File error: %s", e)
        sys.exit(1)
    except (ValueError, json.JSONDecodeError) as e:
        logger.error("Schema/Format error: %s", e)
        sys.exit(1)
    except (ImportError, AttributeError, TypeError) as e:
        logger.error("Module/Parser error: %s", e)
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected audit failure: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()