import unittest
    # The following line requires the 'requests' library, ensure it is installed using 'pip install requests'
from hn_data_collector import get_hn_posts
from content_analyzer import preprocess_text, calculate_diversity_score, analyze_diversity
from content_curator import curate_content
from presentation_layer import present_content

class TestHNContentDiversityAgent(unittest.TestCase):

    def test_get_hn_posts(self):
        posts = get_hn_posts()
        self.assertIsInstance(posts, list)
        for post in posts:
            self.assertIsInstance(post, dict)
            self.assertIn('id', post)
            self.assertIn('title', post)

    def test_preprocess_text(self):
        text = "This is a sample text with some stop words and punctuation!"
        tokens = preprocess_text(text)
        self.assertIsInstance(tokens, list)
        self.assertTrue(all(isinstance(token, str) for token in tokens))
        self.assertNotIn('is', tokens)
        self.assertNotIn('a', tokens)
        self.assertNotIn('with', tokens)

    def test_calculate_diversity_score(self):
        tokens = ['hello', 'world', 'hello', 'python']
        score = calculate_diversity_score(tokens)
        self.assertEqual(score, 0.75)

    def test_analyze_diversity(self):
        posts = [
            {'id': 1, 'title': 'Sample Title 1', 'text': 'Some text here.'},
            {'id': 2, 'title': 'Sample Title 2', 'text': 'Another text here.'}
        ]
        diversity_scores = analyze_diversity(posts)
        self.assertIsInstance(diversity_scores, dict)
        self.assertIn(1, diversity_scores)
        self.assertIn(2, diversity_scores)
        self.assertGreaterEqual(diversity_scores[1], 0.0)
        self.assertLessEqual(diversity_scores[1], 1.0)
        self.assertGreaterEqual(diversity_scores[2], 0.0)
        self.assertLessEqual(diversity_scores[2], 1.0)

    def test_curate_content(self):
        posts = [
            {'id': 1, 'title': 'Sample Title 1', 'text': 'Some text here.'},
            {'id': 2, 'title': 'Sample Title 2', 'text': 'Another text here.'}
        ]
        diversity_scores = {1: 0.8, 2: 0.9}
        curated_posts = curate_content(posts, diversity_scores)
        self.assertIsInstance(curated_posts, list)
        self.assertLessEqual(len(curated_posts), 10)
        for post in curated_posts:
            self.assertIsInstance(post, dict)
            self.assertIn('id', post)
            self.assertIn('title', post)

    def test_present_content(self):
        curated_posts = [
            {'id': 1, 'title': 'Sample Title 1', 'by': 'Author 1', 'score': 100, 'url': 'http://example.com/1'},
            {'id': 2, 'title': 'Sample Title 2', 'by': 'Author 2', 'score': 200, 'url': 'http://example.com/2'}
        ]
        presentation = present_content(curated_posts)
        self.assertIsInstance(presentation, str)
        self.assertIn('Curated Hacker News Posts:', presentation)
        self.assertIn('Title: Sample Title 1', presentation)
        self.assertIn('By: Author 1', presentation)
        self.assertIn('Score: 100', presentation)
        self.assertIn('URL: http://example.com/1', presentation)
        self.assertIn('Title: Sample Title 2', presentation)
        self.assertIn('By: Author 2', presentation)
        self.assertIn('Score: 200', presentation)
        self.assertIn('URL: http://example.com/2', presentation)

if __name__ == '__main__':
    unittest.main()
