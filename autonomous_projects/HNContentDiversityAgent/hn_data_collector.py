    # Note: Install requests library using 'pip install requests'
try:
    import requests
except ImportError:
    requests = None

from typing import List, Dict


def get_hn_posts() -> List[Dict]:
    """
    Fetches and returns a list of Hacker News (HN) posts.
    
    This function uses the HN API to collect the top stories and their details.
    It returns a list of dictionaries, each representing a post with its metadata.
    """
    try:
        # Fetch the IDs of the top stories
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        response = requests.get(top_stories_url)
        response.raise_for_status()
        story_ids = response.json()

        # Limit to the first 50 stories for performance and relevance
        story_ids = story_ids[:50]

        # Fetch the details of each story
        base_url = "https://hacker-news.firebaseio.com/v0/item/{}.json"
        posts = []
        for story_id in story_ids:
            story_url = base_url.format(story_id)
            response = requests.get(story_url)
            response.raise_for_status()
            story = response.json()
            if story is not None:
                posts.append(story)

        return posts
    except (AttributeError, Exception) as e:
        return []
