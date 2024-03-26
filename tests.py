import unittest
from unittest.mock import patch, mock_open
import json
from your_script import load_config, validate_config, extract_related_keywords

class TestLoadConfig(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data='{"api_key": "valid_key"}')
    def test_load_config_valid(self, mock_file):
        config = load_config()
        self.assertEqual(config, {'api_key': 'valid_key'})

    @patch('builtins.open', new_callable=mock_open, read_data='invalid_json')
    def test_load_config_invalid_json(self, mock_file):
        with self.assertRaises(json.JSONDecodeError):
            load_config()

class TestValidateConfig(unittest.TestCase):
    def test_validate_config_valid(self):
        config = {
            'api_key': 'valid_key',
            'keywords': ['keyword1', 'keyword2'],
            'max_results_per_keyword': 10,
            'requests_per_second': 2,
            'max_depth': 3,
            'max_retries': 5,
            'default_timeout': 1.5
        }
        validate_config(config)  # No exception raised

    def test_validate_config_invalid_api_key(self):
        config = {
            'api_key': '',
            'keywords': ['keyword1', 'keyword2'],
            # ... (other valid values) ...
        }
        with self.assertRaises(ValueError):
            validate_config(config)

    # ... (additional test cases for other validation scenarios) ...

class TestExtractRelatedKeywords(unittest.TestCase):
    def test_extract_related_keywords(self):
        video_metadata = {
            'title': 'Python Programming Tutorial',
            'description': 'Learn Python programming from scratch in this tutorial.'
        }
        keywords = extract_related_keywords(video_metadata)
        expected_keywords = ['python', 'programming', 'tutorial', 'learn', 'scratch']
        self.assertCountEqual(keywords, expected_keywords)

    def test_extract_related_keywords_missing_description(self):
        video_metadata = {
            'title': 'Python Programming Tutorial',
            'description': ''
        }
        keywords = extract_related_keywords(video_metadata)
        self.assertEqual(keywords, [])

if __name__ == '__main__':
    unittest.main()
