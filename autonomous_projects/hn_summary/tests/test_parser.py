import pytest
from hn_summary.parser import parse_raw_feed, summarize_posts, Post

RAW_SAMPLE = """Problem: Ask HN: How are thinking efforts implemented?
Text: Claude and ChatGPT have thinking efforts where you can tune the amount of thinking allowed.<p>Like low, medium, high, xhigh and so on.<p>But are they different models underneath? Or same model with di

Problem: AWS Bedrock to require sharing data with Anthropic for Mythos
Text: > For Fable 5, Mythos 5, and future models on Bedrock with similar or higher capability levels, Anthropic will require 30-day retention for all traffic on Mythos-class models. Retaining data for a 

Problem: Show HN: Lightweight Task queue on Erlang/OTP, SQLite-backed, no overengineering
Text: Setting up Kafka or such enterprise oriented software with their clusters or dedicated servers is heavy and bothering enough that most small \nteams or indie hackers skip it entirely and making comprom"""

def test_parse_basic():
    posts = parse_raw_feed(RAW_SAMPLE)
    assert len(posts) == 3
    titles = [p.title for p in posts]
    assert titles[0] == "Ask HN: How are thinking efforts implemented?"
    assert "ai" in posts[0].tags  # contains 'ChatGPT'
    assert "ai" in posts[1].tags  # contains 'Anthropic'
    assert "gaming" not in posts[2].tags  # no keyword match, should be untagged

def test_summary_output():
    posts = parse_raw_feed(RAW_SAMPLE)
    summary = summarize_posts(posts)
    # Should contain headings for AI and Untagged groups
    assert "## Ai" in summary
    assert "## Untagged" in summary
    # Each title should appear
    for p in posts:
        assert p.title in summary
