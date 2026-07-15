import unittest
from unittest.mock import patch, MagicMock
try:
    from content_flagger import flag_ai_generated_content
except ModuleNotFoundError as e:
    if "sklearn" in str(e):
        print(f'Warning: {e}. Please install it with `pip install scikit-learn` and `pip install joblib`')
        flag_ai_generated_content = None
    else:
        raise e
from unittest.mock import patch
from unittest.mock import patch, MagicMock
from ai_detection_model import load_training_data, train_model, predict
from content_flagger import flag_ai_generated_content
from hn_content_fetcher import fetch_hn_articles

class TestHNContentIntegrityAgent(unittest.TestCase):

    def test_fetch_hn_articles(self):
        articles = fetch_hn_articles()
        self.assertIsInstance(articles, list)
        for article in articles:
            self.assertIsInstance(article, dict)
            self.assertIn('title', article)
            self.assertIn('url', article)
            self.assertIn('text', article)

    @patch('hn_content_fetcher.requests', new_callable=MagicMock)
    def test_fetch_hn_articles_with_exception(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        articles = fetch_hn_articles()
        self.assertEqual(articles, [])

    def test_load_training_data(self):
        texts, labels = load_training_data()
        self.assertIsInstance(texts, list)
        self.assertIsInstance(labels, list)
        self.assertEqual(len(texts), len(labels))

    def test_train_model(self):
        training_data = load_training_data()
        model = train_model(training_data)
        self.assertIsNotNone(model)

    def test_predict(self):
        training_data = load_training_data()
        model = train_model(training_data)
        sample_text = "This is a sample text to check if it's AI-generated."
        result = predict(sample_text, model)
        self.assertIn(result, [True, False])

    def test_flag_ai_generated_content(self):
        training_data = load_training_data()
        model = train_model(training_data)
        articles = [
            {'title': 'Test Article 1', 'url': 'http://example.com/1', 'text': 'This is a test text.'},
            {'title': 'Test Article 2', 'url': 'http://example.com/2', 'text': 'Another test text.'}
        ]
        flag_ai_generated_content(articles, model)
        for article in articles:
            self.assertIn('is_ai_generated', article)
            self.assertIn(article['is_ai_generated'], [True, False])

if __name__ == "__main__":
    unittest.main()
