from typing import List, Dict

def extract_trends(raw: dict) -> List[Dict[str, str]]:
    """Transform raw API payload into a list of trend dicts with keys:
    - title
    - url
    - author
    - points
    - comments
    """
    trends = []
    for hit in raw.get("hits", []):
        trends.append({
            "title": hit.get("title") or hit.get("story_title") or "",
            "url": hit.get("url") or hit.get("story_url") or "",
            "author": hit.get("author", ""),
            "points": str(hit.get("points", 0)),
            "comments": str(hit.get("num_comments", 0)),
        })
    return trends
