import unittest
import sys
from unittest.mock import patch, MagicMock
import requests
import text_analysis
import user_interface
import hn_api_integration

class TestTextAnalysis(unittest.TestCase):
    def test_analyze_text(self):
        self.assertTrue(text_analysis.analyze_text("test test test test"))
        self.assertFalse(text_analysis.analyze_text("This is a unique sentence with no repetition."))

    def test_has_repetitive_patterns(self):
        self.assertTrue(text_analysis.has_repetitive_patterns("test test test test"))

    def test_has_unusual_punctuation(self):
        self.assertTrue(text_analysis.has_unusual_punctuation("This is a test.... This is only a test!!"))
        self.assertFalse(text_analysis.has_unusual_punctuation("This is a normal sentence."))

    @patch('requests.get')
    def test_get_hn_stories(self, mock_get):
        def mock_get_side_effect(url, *args, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            if 'topstories.json' in url:
                mock_resp.json.return_value = [12345, 67890]
            elif '12345.json' in url:
                mock_resp.json.return_value = {'id': 12345, 'text': 'Story 1'}
            elif '67890.json' in url:
                mock_resp.json.return_value = {'id': 67890, 'text': 'Story 2'}
            return mock_resp
            
        mock_get.side_effect = mock_get_side_effect
        stories = hn_api_integration.get_hn_stories('topstories', limit=2)
        self.assertEqual(len(stories), 2)
        self.assertEqual(stories[0]['id'], 12345)
        self.assertEqual(stories[1]['id'], 67890)

    def test_display_stories(self):
        stories = [
            {'title': 'Test Title 1', 'by': 'Author 1', 'url': 'http://example.com/1'},
            {'title': 'Test Title 2', 'by': 'Author 2', 'url': 'http://example.com/2'}
        ]
        user_interface.display_stories(stories)

    def test_filter_stories(self):
        stories = [
            {'text': 'test test test test'},
            {'text': 'This is a unique sentence with no repetition.'}
        ]
        filtered_stories = user_interface.filter_stories(stories)
        # The filter should remove stories with repetitive patterns, so we expect 1 story (the non-repetitive one)
        self.assertEqual(len(filtered_stories), 1)
        # Verify that the repetitive story was removed and the unique one remains
        self.assertEqual(filtered_stories[0]['text'], 'This is a unique sentence with no repetition.')

        stories = [
            {'text': 'test test test test'},
        ]
        filtered_stories = user_interface.filter_stories(stories)
        self.assertEqual(len(filtered_stories), 0)

        stories = [
            {'text': 'test test test test'},
        ]
        filtered_stories = user_interface.filter_stories(stories)
        self.assertEqual(len(filtered_stories), 0)
    @patch('builtins.print')
    @patch('user_interface.filter_stories')
    @patch('hn_api_integration.get_hn_stories')
    @patch('user_interface.display_stories')
    def test_main(self, mock_display_stories, mock_get_hn_stories, mock_filter_stories, mock_print):
        mock_filter_stories.return_value = [{'id': 123, 'title': 'Test Title', 'by': 'Author', 'url': 'http://example.com/'}]
        mock_get_hn_stories.return_value = [123]
        mock_display_stories.return_value = None
        # Call the actual main function (assuming it exists in user_interface)
        user_interface.main()
        self.assertGreater(mock_print.call_count, 0)
