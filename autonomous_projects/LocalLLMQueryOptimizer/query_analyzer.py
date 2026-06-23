"""
query_analyzer.py

Module responsible for analyzing user queries to extract structural and semantic metrics
that inform optimization decisions for local LLMs. Provides functions to compute token counts,
identify unique keywords, detect emails and URLs, and generate human-readable analysis reports.
"""

import re
from typing import Dict, List, Any


def analyze_query(query: str) -> Dict[str, Any]:
    """
    Analyze a query string and return a dictionary of quantitative metrics.

    The analysis includes:
      - 'total_tokens': number of whitespace-separated tokens (words/tokens)
      - 'unique_keywords': count of distinct alphabetic words (case-insensitive, stripped of punctuation)
      - 'emails_count': number of email addresses found
      - 'urls_count': number of URLs found

    Args:
        query: Input query string to analyze.

    Returns:
        A dictionary containing the following keys:
          - "total_tokens": int
          - "unique_keywords": int
          - "emails_count": int
          - "urls_count": int

    Raises:
        TypeError: If input is not a string.
    """
    if not isinstance(query, str):
        raise TypeError("Query must be a string.")

    # Token count: split on whitespace (preserves internal punctuation in tokens)
    tokens = query.split()
    total_tokens = len(tokens)

    # Unique keywords: extract only alphabetic words, lowercase, deduplicate
    words = re.findall(r'\b[a-zA-Z]+\b', query)
    unique_keywords = len(set(word.lower() for word in words))

    # Email count
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, query)
    emails_count = len(emails)

    # URL count
    url_pattern = r'\bhttps?://[^\s]+\b'
    urls = re.findall(url_pattern, query)
    urls_count = len(urls)

    return {
        "total_tokens": total_tokens,
        "unique_keywords": unique_keywords,
        "emails_count": emails_count,
        "urls_count": urls_count,
    }


def get_analysis_report(query: str) -> str:
    """
    Generate a formatted, human-readable analysis report for a given query.

    The report contains labeled lines for each metric returned by `analyze_query`,
    using standardized labels matching test expectations.

    Args:
        query: Input query string to analyze and report on.

    Returns:
        A multi-line string with the following format:
          "Total Tokens: <value>"
          "Unique Keywords: <value>"
          "Emails Count: <value>"
          "URLs Count: <value>"

    Raises:
        TypeError: If input is not a string.
    """
    if not isinstance(query, str):
        raise TypeError("Query must be a string.")

    analysis = analyze_query(query)
    return (
        f"Total Tokens: {analysis['total_tokens']}\n"
        f"Unique Keywords: {analysis['unique_keywords']}\n"
        f"Emails Count: {analysis['emails_count']}\n"
        f"URLs Count: {analysis['urls_count']}"
    )