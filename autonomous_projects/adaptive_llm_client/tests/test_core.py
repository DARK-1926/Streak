import os
import sys
import json
import pytest

# Ensure the package root is on the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from adaptive_llm_client.core import AdaptiveLLM, EffortLevel

# Mock requests to avoid real API calls during CI
import types

class DummyResponse:
    def __init__(self, data):
        self._data = data
    def raise_for_status(self):
        pass
    def json(self):
        return self._data

def fake_post(url, json, headers, timeout):
    # Echo back the prompt with a marker so we can assert mapping
    model = json.get("model")
    prompt = json["messages"][0]["content"]
    return DummyResponse({
        "choices": [{"message": {"content": f"[{model}] {prompt}"}}]
    })

def monkeypatch_requests(monkeypatch):
    import requests
    monkeypatch.setattr(requests, "post", fake_post)

@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    # Provide a dummy key for the duration of the tests
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch_requests(monkeypatch)

def test_think_returns_expected_format():
    client = AdaptiveLLM()
    result = client.think(EffortLevel.HIGH, "Hello world")
    assert result.startswith("[gpt-4]")
    assert "Hello world" in result

def test_cache_is_used():
    client = AdaptiveLLM()
    first = client.think(EffortLevel.LOW, "repeat")
    # Directly tamper the fake_post to raise if called again
    import requests
    def exploding_post(*a, **kw):
        raise AssertionError("Network call should not happen on cache hit")
    requests.post = exploding_post
    second = client.think(EffortLevel.LOW, "repeat")
    assert first == second

def test_invalid_effort_raises():
    client = AdaptiveLLM()
    with pytest.raises(KeyError):
        client.think("nonexistent", "test")  # type: ignore
