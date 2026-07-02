import unittest
from code_reviewer import analyze_code

class TestCodeReviewer(unittest.TestCase):
    def test_analyze_code_with_unused_import(self):
        code = "import os\nprint('Hello, world!')"
        feedback = analyze_code(code)
        self.assertIn("Unused import: os", feedback['unused_imports'])

    def test_analyze_code_with_valid_names(self):
        code = "def my_function():\n    x = 10\n    print(x)"
        feedback = analyze_code(code)
        self.assertEqual(feedback['naming_conventions'], [])

    def test_analyze_code_with_invalid_name(self):
        code = "def MyFunction():\n    X = 10\n    print(X)"
        feedback = analyze_code(code)
        self.assertIn("Invalid name for FunctionDef: MyFunction", feedback['naming_conventions'])
        self.assertIn("Invalid variable name: X", feedback['naming_conventions'])

    def test_analyze_code_with_none_comparison(self):
        code = "x = None\nif x == None:\n    print('None')"
        feedback = analyze_code(code)
        self.assertIn("Use 'is' to compare with None, not '=='", feedback['potential_bugs'])

    def test_analyze_code_with_no_issues(self):
        code = "def my_function():\n    x = 10\n    if x is None:\n        print('None')"
        feedback = analyze_code(code)
        self.assertEqual(feedback['unused_imports'], [])
        self.assertEqual(feedback['naming_conventions'], [])
        self.assertEqual(feedback['potential_bugs'], [])

    def test_analyze_code_with_syntax_error(self):
        code = "def my_function():\n    x = 10\n    if x is None"
        with self.assertRaises(SyntaxError):
            analyze_code(code)

if __name__ == "__main__":
    unittest.main()