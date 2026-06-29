import os
import json
import unittest
from unittest.mock import patch, mock_open
from skillgap_analyzer import SkillGapAnalyzer, load_skill_profile
from resource_recommender import recommend_resources, load_resource_database, save_resource_database
from learning_path_generator import generate_learning_path, save_learning_path, load_learning_path

class TestSkillGrowthAgent(unittest.TestCase):

    def setUp(self):
        self.skill_profile = {
            "Python": ["ast", "unittest"],
            "Web Development": ["Django", "Flask"]
        }
        self.resource_db = {
            "Python": [
                {"title": "Automate the Boring Stuff with Python", "type": "book", "url": "https://automatetheboringstuff.com/"},
                {"title": "Real Python", "type": "website", "url": "https://realpython.com/"},
            ],
            "Web Development": [
                {"title": "Django for Beginners", "type": "book", "url": "https://djangoforbeginners.com/"},
                {"title": "Flask Web Development", "type": "book", "url": "https://flask.palletsprojects.com/en/2.0.x/"},
            ]
        }


    def test_load_skill_profile(self):
        m = mock_open(read_data=json.dumps(self.skill_profile))
        with patch('builtins.open', m):
            loaded_profile = load_skill_profile('skill_profile.json')
            # Normalize both sides to sorted lists for order-agnostic comparison
            normalized_expected = {k: sorted(v) for k, v in self.skill_profile.items()}
            normalized_loaded = {k: sorted(v) for k, v in loaded_profile.items()}
            self.assertEqual(normalized_loaded, normalized_expected)

    def test_skill_gap_analyzer(self):
        analyzer = SkillGapAnalyzer(self.skill_profile)
        gaps = analyzer.identify_skill_gaps('path/to/codebase')
        # Normalize to sorted lists for deterministic comparison
        normalized_gaps = {k: sorted(v) for k, v in gaps.items()}
        expected_gaps = {k: sorted(v) for k, v in {'Python': ['unittest', 'ast'], 'Web Development': ['Django', 'Flask']}.items()}
        self.assertEqual(normalized_gaps, expected_gaps)

    def test_recommend_resources(self):
        skill_gaps = {"Python": ["advanced topics"], "Web Development": ["Django"]}
        m = mock_open(read_data=json.dumps(self.resource_db))
        with patch('builtins.open', m):
            recommendations = recommend_resources(skill_gaps)
        expected_recommendations = {
            "Web Development": [{"title": "Django for Beginners", "type": "book", "url": "https://djangoforbeginners.com/"}]
        }
        self.assertEqual(recommendations, expected_recommendations)

    def test_load_resource_database(self):
        m = mock_open(read_data=json.dumps(self.resource_db))
        with patch('builtins.open', m):
            loaded_db = load_resource_database('resources.json')
            self.assertEqual(loaded_db, self.resource_db)

    def test_save_resource_database(self):
        m = mock_open()
        with patch('builtins.open', m), patch('os.path.exists', return_value=True):
            save_resource_database('resources.json', self.resource_db)
            m.assert_called_once_with('resources.json', 'w', encoding='utf-8')

    def test_generate_learning_path(self):
        recommended_resources = {
            "Python": [
                {"title": "Automate the Boring Stuff with Python", "type": "book", "url": "https://automatetheboringstuff.com/"},
                {"title": "Real Python", "type": "website", "url": "https://realpython.com/"},
            ],
            "Web Development": [
                {"title": "Django for Beginners", "type": "book", "url": "https://djangoforbeginners.com/"},
                {"title": "Flask Web Development", "type": "book", "url": "https://flask.palletsprojects.com/en/2.0.x/"},
            ]
        }
        learning_path = generate_learning_path(recommended_resources)
        expected_path = {
            "Python": [
                {"step": 1, "title": "Automate the Boring Stuff with Python", "type": "book", "url": "https://automatetheboringstuff.com/"},
                {"step": 2, "title": "Real Python", "type": "website", "url": "https://realpython.com/"},
            ],
            "Web Development": [
                {"step": 1, "title": "Django for Beginners", "type": "book", "url": "https://djangoforbeginners.com/"},
                {"step": 2, "title": "Flask Web Development", "type": "book", "url": "https://flask.palletsprojects.com/en/2.0.x/"},
            ]
        }
        self.assertEqual(learning_path, expected_path)

    def test_save_and_load_learning_path(self):
        learning_path = {
            "Python": [
                {"step": 1, "title": "Automate the Boring Stuff with Python", "type": "book", "url": "https://automatetheboringstuff.com/"},
                {"step": 2, "title": "Real Python", "type": "website", "url": "https://realpython.com/"},
            ],
            "Web Development": [
                {"step": 1, "title": "Django for Beginners", "type": "book", "url": "https://djangoforbeginners.com/"},
            ],
        }
        m = mock_open()
        with patch('builtins.open', m), patch('os.path.exists', return_value=True):
            save_learning_path(learning_path, 'learning_path.json')
        m_read = mock_open(read_data=json.dumps(learning_path))
        with patch('builtins.open', m_read):
            loaded_path = load_learning_path('learning_path.json')
            self.assertEqual(loaded_path, learning_path)

if __name__ == "__main__":
    unittest.main()
