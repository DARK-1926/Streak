from typing import List, Dict, Any

def present_content(curated_posts: List[Dict[str, Any]]) -> str:
    """
    Formats and presents the curated content as a user-friendly string.
    
    Args:
        curated_posts (List[Dict[str, Any]]): A list of dictionaries, each representing a post with its metadata.
        
    Returns:
        str: A formatted string presenting the curated posts.
    """
    try:
        if not curated_posts:
            return "No curated posts available."

        presentation = "Curated Hacker News Posts:\n"
        for index, post in enumerate(curated_posts, start=1):
            title = post.get('title', 'No Title')
            by = post.get('by', 'Unknown Author')
            score = post.get('score', 0)
            url = post.get('url', 'No URL Provided')

            post_info = f"{index}. Title: {title}\n"
            post_info += f"   By: {by}\n"
            post_info += f"   Score: {score}\n"
            post_info += f"   URL: {url}\n\n"

            presentation += post_info

        return presentation
    except Exception as e:
        print(f"Error during content presentation: {e}")
        return "An error occurred while presenting the content."
