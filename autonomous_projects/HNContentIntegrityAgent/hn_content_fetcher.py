# Note: This requires 'requests' library to be installed via 'pip install requests'
try:
    import requests
except ImportError as e:
    raise ImportError(
        "Missing required dependency 'requests'. "
        "Please install it with: pip install requests"
    ) from e
from typing import List, Dict


def fetch_hn_articles() -> List[Dict[str, str]]:
    """
    Fetches the latest articles from Hacker News and returns them as a list of dictionaries.
    Each dictionary contains the title, URL, and text of the article.
    """
    try:
        # Fetch the top stories IDs from the HN API
        response = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json')
        response.raise_for_status()
        top_stories_ids = response.json()

        # Initialize an empty list to store the articles
        articles = []

        # Limit to the first 10 articles for performance and to avoid rate limits
        for story_id in top_stories_ids[:10]:
            # Fetch each story's details
            story_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
            story_response = requests.get(story_url)
            story_response.raise_for_status()
            story_data = story_response.json()

            # Debug print: Print the story data
            print(f"Story Data: {story_data}")

            # Check if the story has a URL and is not a job or ask HN post
            if 'url' in story_data and story_data['type'] == 'story':
                # Extract the title, URL, and text
                title = story_data.get('title', '')
                url = story_data.get('url', '')
                text = story_data.get('text', '')

                # Debug print: Print the extracted values
                print(f"Title: {title}, URL: {url}, Text: {text}")

                # Append the article data to the list
                articles.append({
                    'title': title,
                    'url': url,
                    'text': text
                })

        return articles

    except requests.RequestException as e:
        print(f"Request Exception: {e}")
        return []

    except Exception as e:
        # Handle other exceptions
        print(f"An unexpected error occurred: {e}")
        return []
