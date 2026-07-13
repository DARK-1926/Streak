import sys
from typing import List, Dict, Any
import hn_api_integration

def display_stories(stories: List[Dict[str, Any]]) -> None:
    """
    Displays a list of stories in a readable format.
    
    Args:
        stories (List[Dict[str, Any]]): A list of dictionaries, each representing a story.
    """
    for index, story in enumerate(stories, start=1):
        print(f"Story {index}:")
        print(f"Title: {story.get('title', 'No Title')}")
        print(f"By: {story.get('by', 'Unknown')}")
        print(f"URL: {story.get('url', 'No URL')}")
        if 'text' in story:
            print("Text:")
            print(story['text'])
        print("-" * 40)

def filter_stories(stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filters out AI-generated stories from the provided list of stories.
    
    Args:
        stories (List[Dict[str, Any]]): A list of dictionaries, each representing a story.
        
    Returns:
        List[Dict[str, Any]]: A filtered list of stories with AI-generated content removed.
    """
    filtered_stories = []
    for story in stories:
        if not hn_api_integration.flag_story(story):
            filtered_stories.append(story)
    return filtered_stories

def main() -> None:
    """
    Main function to run the HNContentFilterAgent user interface.
    Fetches and displays stories, then allows the user to filter out AI-generated content.
    """
    try:
        # Fetch top stories from Hacker News
        stories = hn_api_integration.get_hn_stories('topstories')
        
        if not stories:
            print("No stories found.")
            return
        
        # Display all fetched stories
        print("All Stories:")
        display_stories(stories)
        
        # Filter out AI-generated stories
        filtered_stories = filter_stories(stories)
        
        if not filtered_stories:
            print("All stories were flagged as AI-generated. No stories to display after filtering.")
            return
        
        # Display filtered stories
        print("Filtered Stories (AI-generated content removed):")
        display_stories(filtered_stories)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()