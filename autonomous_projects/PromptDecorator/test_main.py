import unittest
import json
from prompt_decorator import transform_json_to_markdown, decorate_prompt
from data_loader import load_json_data
from prompt_decorator import transform_json_to_markdown, decorate_prompt
from data_loader import load_json_data

class TestPromptDecorator(unittest.TestCase):
    def test_transform_json_to_markdown(self):
        # Test with a simple dictionary
        data = {"name": "John Doe", "age": 30}
        expected_output = "**name**: John Doe\n**age**: 30\n"
        self.assertEqual(transform_json_to_markdown(data), expected_output)

        # Test with a nested dictionary
        data = {"person": {"name": "Jane Doe", "age": 25}}
        expected_output = "### person\n**name**: Jane Doe\n**age**: 25\n"
        self.assertEqual(transform_json_to_markdown(data), expected_output)

        # Test with a list
        data = {"hobbies": ["reading", "swimming", "coding"]}
        expected_output = "### hobbies\n- reading\n- swimming\n- coding\n"
        self.assertEqual(transform_json_to_markdown(data), expected_output)

        # Test with an empty dictionary
        data = {}
        expected_output = ""
        self.assertEqual(transform_json_to_markdown(data), expected_output)

    def test_decorate_prompt(self):
        # Test with a simple decoration
        prompt = "This is a test prompt."
        decorations = {"date": "2023-10-01", "author": "Alice"}
        expected_output = "date: 2023-10-01\nauthor: Alice\n\nThis is a test prompt."
        self.assertEqual(decorate_prompt(prompt, decorations), expected_output)

        # Test with an empty decoration
        prompt = "This is another test prompt."
        decorations = {}
        expected_output = "\n\nThis is another test prompt."
        self.assertEqual(decorate_prompt(prompt, decorations), expected_output)

        # Test with multiple decorations
        prompt = "This is a third test prompt."
        decorations = {"date": "2023-10-02", "author": "Bob", "location": "New York"}
        expected_output = "date: 2023-10-02\nauthor: Bob\nlocation: New York\n\nThis is a third test prompt."
        self.assertEqual(decorate_prompt(prompt, decorations), expected_output)

    def test_load_json_data(self):
        # Test with a valid JSON file
        file_path = "test_data.json"
        expected_data = {"name": "Test User", "age": 28}
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(expected_data, file)
        self.assertEqual(load_json_data(file_path), expected_data)

        # Test with a non-existent file
        file_path = "non_existent_file.json"
        with self.assertRaises(ValueError) as context:
            load_json_data(file_path)
        self.assertTrue("The file at" in str(context.exception))

        # Test with invalid JSON content
        file_path = "invalid_json.json"
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write("Invalid JSON content")
        with self.assertRaises(ValueError) as context:
            load_json_data(file_path)
        self.assertTrue("Error decoding JSON from" in str(context.exception))

if __name__ == '__main__':
    unittest.main()
