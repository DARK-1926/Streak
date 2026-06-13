import requests

def fetch_trends(url: str = "https://hn.algolia.com/api/v1/search_by_date?tags=story&hitsPerPage=20") -> dict:
    """Fetch raw Hacker News stories JSON from Algolia API.
    Returns the parsed JSON dict or raises RuntimeError on failure.
    """
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch trends: {resp.status_code}")
    return resp.json()
