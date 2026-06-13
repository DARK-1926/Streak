import pytest
from hn_summary.core import extract_titles

SAMPLE_SNIPPETS = [
    "Problem: How are thinking efforts implemented?\nText: Claude and ChatGPT have thinking efforts where you can tune the amount of thinking allowed.<p>Like low, medium, high, xhigh and so on.<p>But are they different models underneath? Or same model with di",
    "Problem: Favorite text heavy blogs that are a joy to read?\nText: After ten years I’m working on a redesign of my personal tech blog. I want to look at some other blogs with good modern design. Of course searching for ‘well designed blogs’ or ‘webdesign 2026’ brings",
    "Problem: I'm Eric Ries, author of \"The Lean Startup\" and new book \"Incorruptible\" – AMA\nText: Hey gang, you may remember me from such books as _The Lean Startup_.",
]

EXPECTED = [
    {"title": "How are thinking efforts implemented?"},
    {"title": "Favorite text heavy blogs that are a joy to read?"},
    {"title": "I'm Eric Ries, author of \"The Lean Startup\" and new book \"Incorruptible\" – AMA"},
]

def test_extract_titles():
    results = extract_titles(SAMPLE_SNIPPETS)
    for res, exp in zip(results, EXPECTED):
        assert res["title"] == exp["title"]
