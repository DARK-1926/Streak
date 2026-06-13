import os
import json
from pathlib import Path

from ai_frontend_linter.linter import lint_path, format_report
from ai_frontend_linter.config import LinterConfig, ThinkingLevel

# Use a temporary directory with fixture files
FIXTURE_DIR = Path(__file__).parent / "fixtures"

def _write_fixture(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_static_html_issue(tmp_path: Path, monkeypatch):
    # Create a simple HTML file missing alt attribute
    html_path = tmp_path / "index.html"
    _write_fixture(html_path, "<img src='logo.png'>\n<p>Hello</p>")

    cfg = LinterConfig(max_file_size_kb=10, thinking_level=ThinkingLevel.LOW, openai_api_key=None)
    result = lint_path(tmp_path, cfg)
    assert "index.html" in result
    issues = result["index.html"]
    assert any("alt" in i["message"].lower() for i in issues)
    # Advice should be absent because LLM disabled
    assert all("advice" not in i for i in issues)


def test_static_css_issue(tmp_path: Path):
    css_path = tmp_path / "style.css"
    _write_fixture(css_path, "h1 { font-size: 24px; !important; }")
    cfg = LinterConfig(max_file_size_kb=10, thinking_level=ThinkingLevel.LOW, openai_api_key=None)
    result = lint_path(tmp_path, cfg)
    issues = result["style.css"]
    msgs = [i["message"].lower() for i in issues]
    assert any("!important" in m for m in msgs)
    assert any("relative units" in m for m in msgs)


def test_static_js_issue(tmp_path: Path):
    js_path = tmp_path / "app.js"
    _write_fixture(js_path, "const user = document.location; eval(user);")
    cfg = LinterConfig(max_file_size_kb=10, thinking_level=ThinkingLevel.LOW, openai_api_key=None)
    result = lint_path(tmp_path, cfg)
    issues = result["app.js"]
    assert any("eval" in i["message"].lower() for i in issues)
    assert any("innerhtml" in i["message"].lower() for i in issues) is False


def test_report_formatting(tmp_path: Path):
    html_path = tmp_path / "bad.html"
    _write_fixture(html_path, "<script src='http://evil.com/lib.js'></script>")
    cfg = LinterConfig(max_file_size_kb=10, thinking_level=ThinkingLevel.LOW, openai_api_key=None)
    result = lint_path(tmp_path, cfg)
    report = format_report(result)
    assert "File: bad.html" in report
    assert "External script without integrity" in report

# The following test ensures that the environment variable loader works.
def test_config_from_env(monkeypatch):
    monkeypatch.setenv("AI_LINTER_MAX_FILE_KB", "300")
    monkeypatch.setenv("AI_LINTER_THINKING_LEVEL", "high")
    cfg = LinterConfig.from_env()
    assert cfg.max_file_size_kb == 300
    assert cfg.thinking_level == ThinkingLevel.HIGH
    assert cfg.token_budget == 1024
