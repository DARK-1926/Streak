import re
from typing import List, Dict, Any

def preprocess_text(text: str) -> List[str]:
    # Convert to lowercase and tokenize
    tokens = re.findall(r'\b\w+\b', text.lower())
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
    return [token for token in tokens if token not in stop_words]
    # For testing purposes, we'll mock the NLTK functionality
    class MockNLTK:
        @staticmethod
        def download(*args):
            pass
    
    class MockWordTokenize:
        @staticmethod
        def tokenize(text):
            return text.split()
    
    class MockStopwords:
        @staticmethod
        def words(lang):
            return set()
    
    nltk = MockNLTK()
    word_tokenize = MockWordTokenize().tokenize
    stopwords = MockStopwords()
    print("Warning: NLTK not available, using mock implementation for testing")




def calculate_diversity_score(tokens: List[str]) -> float:
    """
    Calculates the diversity score based on the unique tokens in the text.
    
    Args:
        tokens (List[str]): A list of tokens.
        
    Returns:
        float: The diversity score.
    """
    if not tokens:
        return 0.0
    unique_tokens = len(set(tokens))
    total_tokens = len(tokens)
    return unique_tokens / total_tokens

def analyze_diversity(posts: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Analyzes the diversity of a list of HN posts based on their titles and content.
    
    Args:
        posts (List[Dict[str, Any]]): A list of dictionaries, each representing a post with its metadata.
        
    Returns:
        Dict[str, float]: A dictionary with post IDs as keys and their diversity scores as values.
    """
    diversity_scores = {}
    for post in posts:
        title = post.get('title', '')
        content = post.get('text', '')
        combined_text = f"{title} {content}"
        tokens = preprocess_text(combined_text)
        diversity_score = calculate_diversity_score(tokens)
        diversity_scores[post['id']] = diversity_score
    return diversity_scores
