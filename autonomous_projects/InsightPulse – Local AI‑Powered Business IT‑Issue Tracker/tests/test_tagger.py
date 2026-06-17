import pytest
from unittest import mock
from unittest.mock import MagicMock, patch

# Assuming the tagger functions are located in insightpulse.tagger
from insightpulse.tagger import generate_tags, _compose_prompt


@pytest.fixture
def mock_transformer():
    """Create a mock transformer pipeline that mimics the generate method."""
    mock_pipe = MagicMock()
    mock_pipe.return_value = [{"generated_text": "network, latency, outage"}]
    return mock_pipe


def test_generate_tags_returns_comma_separated_lowercase(mock_transformer):
    """generate_tags should return a comma‑separated string of lower‑case tags."""
    with patch("insightpulse.tagger.pipeline", return_value=mock_transformer):
        result = generate_tags("User cannot connect to VPN.")
        # Ensure result is a string
        assert isinstance(result, str)
        # Tags should be lower‑case
        assert result == result.lower()
        # Should contain commas (at least one)
        assert "," in result
        # Split and verify each tag is non‑empty and stripped
        tags = [t.strip() for t in result.split(",")]
        assert all(tags)  # no empty tags
        # Expected mock output
        assert tags == ["network", "latency", "outage"]


def test_generate_tags_fallback_on_exception():
    """When the model raises an exception, generate_tags should fall back to a safe default."""
    # Force the pipeline to raise an exception when called
    failing_pipe = MagicMock(side_effect=RuntimeError("model failure"))

    with patch("insightpulse.tagger.pipeline", return_value=failing_pipe):
        result = generate_tags("Email service is down.")
        # Expect fallback to an empty string or a predefined safe value
        assert isinstance(result, str)
        # In this implementation fallback returns an empty string
        assert result == ""


def test_compose_prompt_sanity():
    """The internal prompt composition should include the user description and instruction."""
    description = "Database queries are timing out."
    prompt = _compose_prompt(description)
    # Prompt should contain the original description
    assert description in prompt
    # Should contain a clear instruction for tag generation
    assert "Generate a short, comma‑separated list of tags" in prompt
    # Ensure the prompt is lower‑case ready (doesn't enforce case but should be consistent)
    assert prompt.strip().endswith(":")