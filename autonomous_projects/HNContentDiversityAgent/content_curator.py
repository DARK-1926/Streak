from typing import List, Dict, Any

def curate_content(posts: List[Dict[str, Any]], diversity_scores: Dict[int, float]) -> List[Dict[str, Any]]:
    """
    Curates a list of HN posts based on their diversity scores to provide a diverse and interesting selection.
    
    Args:
        posts (List[Dict[str, Any]]): A list of dictionaries, each representing a post with its metadata.
        diversity_scores (Dict[int, float]): A dictionary with post IDs as keys and their diversity scores as values.
        
    Returns:
        List[Dict[str, Any]]: A curated list of posts.
    """
    try:
        # Filter out posts without diversity scores
        scored_posts = [post for post in posts if post['id'] in diversity_scores]
        
        # Sort posts by diversity score in descending order
        sorted_posts = sorted(scored_posts, key=lambda post: diversity_scores[post['id']], reverse=True)
        
        # Select the top 10 diverse posts
        curated_posts = sorted_posts[:10]
        
        return curated_posts
    except Exception as e:
        print(f"Error during content curation: {e}")
        return []