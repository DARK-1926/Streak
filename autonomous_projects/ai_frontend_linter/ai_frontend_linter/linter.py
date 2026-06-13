import re
import json
import base64
from pathlib import Path
from typing import List, Dict, Any

from .config import LinterConfig, ThinkingLevel

# ---------- Static analysis helpers ----------

HTML_ISSUES = [
    (re.compile(r"<img[^>]*(?<!alt=)['\"]?[^>]*>", re.IGNORECASE), "Image tag missing alt attribute"),
    (re.compile(r"<script[^>]*src=['\"]?https?://[^'\"]+['\"]?[^>]*>", re.IGNORECASE), "External script without integrity/subresource‑policy"),
]

CSS_ISSUES = [
    (re.compile(r"!important"), "Avoid using !important; it hampers maintainability"),
    (re.compile(r"\bfont-size:\s*\d+px\b"), "Prefer relative units (rem/em) over absolute px"),
]

JS_ISSUES = [
    (re.compile(r"eval\("), "Use of eval can lead to XSS vulnerabilities"),
    (re.compile(r"innerHTML"), "Direct innerHTML assignment can cause XSS; consider textContent or a sanitizer"),
]

def _run_static_checks(content: str, patterns: List[tuple]) -> List[Dict[str, Any]]:
    findings = []
    for regex, message in patterns:
        for m in regex.finditer(content):
            start = m.start()
            line = content[:start].count("\n") + 1
            findings.append({
                "message": message,
                "line": line,
                "snippet": content[start:start+60].strip().replace("\n", " "),
            })
    return findings

# ---------- LLM reasoning ----------

def _call_llm(prompt: str, config: LinterConfig) -> str:
    """Call OpenAI's chat completion endpoint.

    The function respects the token budget derived from ``config.thinking_level``.
    Returns the raw assistant message.
    """
    import openai
    if not config.openai_api_key:
        raise RuntimeError("OpenAI API key not configured")
    openai.api_key = config.openai_api_key
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=config.token_budget,
        temperature=0,
    )
    return response.choices[0].message.content.strip()

def _enhance_findings_with_llm(findings: List[Dict[str, Any]], file_path: Path, config: LinterConfig) -> List[Dict[str, Any]]:
    if not findings or not config.openai_api_key:
        return findings
    enhanced = []
    for f in findings:
        prompt = (
            f"You are a senior front‑end engineer. The following snippet from {file_path} raises a lint warning:\n\n"
            f"Line {f['line']}: {f['snippet']}\n\n"
            f"Explain why this is a problem and suggest a concrete, minimal code change that resolves it."
        )
        try:
            advice = _call_llm(prompt, config)
        except Exception as exc:
            advice = f"[LLM error: {exc}]"
        f["advice"] = advice
        enhanced.append(f)
    return enhanced

# ---------- Public API ----------

def lint_path(root: Path, config: LinterConfig | None = None) -> Dict[str, List[Dict[str, Any]]]:
    """Recursively lint HTML, CSS and JS files under *root*.

    Returns a dict mapping relative file paths to a list of issue dictionaries.
    """
    if config is None:
        config = LinterConfig.from_env()
    results: Dict[str, List[Dict[str, Any]]] = {}
    for file_path in root.rglob("*.*"):
        if file_path.suffix.lower() not in {".html", ".htm", ".css", ".js"}:
            continue
        if file_path.stat().st_size > config.max_file_size_kb * 1024:
            continue
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        if file_path.suffix.lower() in {".html", ".htm"}:
            findings = _run_static_checks(content, HTML_ISSUES)
        elif file_path.suffix.lower() == ".css":
            findings = _run_static_checks(content, CSS_ISSUES)
        else:  # .js
            findings = _run_static_checks(content, JS_ISSUES)
        findings = _enhance_findings_with_llm(findings, file_path, config)
        if findings:
            results[str(file_path.relative_to(root))] = findings
    return results

def format_report(lint_dict: Dict[str, List[Dict[str, Any]]]) -> str:
    """Pretty‑print the lint dictionary as a human readable report."""
    lines = []
    for file, issues in sorted(lint_dict.items()):
        lines.append(f"File: {file}")
        for i, issue in enumerate(issues, 1):
            lines.append(f"  {i}. Line {issue['line']}: {issue['message']}")
            lines.append(f"     Snippet : {issue['snippet']}")
            advice = issue.get("advice")
            if advice:
                lines.append(f"     Advice  : {advice}")
        lines.append("")
    return "\n".join(lines)
