import argparse
import sys
import json
from urllib.parse import urljoin

import requests


def build_parser() -> argparse.ArgumentParser:
    """Create the top‑level argument parser."""
    parser = argparse.ArgumentParser(
        prog="lca-cli",
        description=(
            "LocalCodingAssistant command‑line client.\n\n"
            "Send a code prompt or question to a running LocalCodingAssistant server and "
            "receive a completion. The server is expected to expose a POST /complete "
            "endpoint that returns JSON with a 'completion' field."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "prompt",
        type=str,
        help="The code snippet or question to complete.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=128,
        help="Maximum number of tokens to generate (default: 128).",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="http://127.0.0.1:5000",
        help="Base URL of the LocalCodingAssistant server (default: http://127.0.0.1:5000).",
    )
    return parser


def request_completion(host: str, prompt: str, max_tokens: int) -> str:
    """Send a completion request to the server and return the generated text.

    Args:
        host: Base URL of the server.
        prompt: The user supplied prompt.
        max_tokens: Maximum tokens for the completion.

    Returns:
        The completion string returned by the server.

    Raises:
        requests.RequestException: Propagated if the request fails.
        ValueError: If the response does not contain the expected field.
    """
    endpoint = urljoin(host.rstrip("/") + "/", "complete")
    payload = {"prompt": prompt, "max_tokens": max_tokens}
    headers = {"Content-Type": "application/json"}

    response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
    response.raise_for_status()

    try:
        data = response.json()
    except json.JSONDecodeError as exc:
        raise ValueError("Server response is not valid JSON") from exc

    if "completion" not in data:
        raise ValueError("Missing 'completion' field in server response")

    return data["completion"]


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        completion = request_completion(args.host, args.prompt, args.max_tokens)
        print(completion)
    except requests.RequestException as exc:
        print(f"Connection error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Invalid response: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()