import unittest
from unittest.mock import patch
import sys
from io import StringIO
from cli import run_cli

class TestCLI(unittest.TestCase):
    @patch('sys.stdin', new_callable=StringIO)
    def test_cli_with_unused_import(self, mock_input):
        mock_input.write("import os\nprint('Hello, world!')\nEOF\n")
        mock_input.seek(0)
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            run_cli()
            output = fake_out.getvalue().strip()
        
        self.assertIn("Unused import: os", output)

    @patch('sys.stdin', new_callable=StringIO)
    def test_cli_with_valid_names(self, mock_input):
        mock_input.write("def my_function():\n    x = 10\n    print(x)\nEOF\n")
        mock_input.seek(0)
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            run_cli()
            output = fake_out.getvalue().strip()
        
        self.assertNotIn("Invalid name for FunctionDef", output)
        self.assertNotIn("Invalid variable name", output)

    @patch('sys.stdin', new_callable=StringIO)
    def test_cli_with_invalid_name(self, mock_input):
        mock_input.write("def MyFunction():\n    X = 10\n    print(X)\nEOF\n")
        mock_input.seek(0)
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            run_cli()
            output = fake_out.getvalue().strip()
        
        self.assertIn("Invalid name for FunctionDef: MyFunction", output)
        self.assertIn("Invalid variable name: X", output)

    @patch('sys.stdin', new_callable=StringIO)
    def test_cli_with_none_comparison(self, mock_input):
        mock_input.write("x = None\nif x == None:\n    print('None')\nEOF\n")
        mock_input.seek(0)
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            run_cli()
            output = fake_out.getvalue().strip()
        
        self.assertIn("Use 'is' to compare with None, not '=='", output)

    @patch('sys.stdin', new_callable=StringIO)
    def test_cli_with_no_issues(self, mock_input):
        mock_input.write("def my_function():\n    x = 10\n    if x is None:\n        print('None')\nEOF\n")
        mock_input.seek(0)
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            run_cli()
            output = fake_out.getvalue().strip()
        
        self.assertNotIn("Unused import", output)
        self.assertNotIn("Invalid name for FunctionDef", output)
        self.assertNotIn("Invalid variable name", output)
        self.assertNotIn("Use 'is' to compare with None, not '=='", output)

    @patch('sys.stdin', new_callable=StringIO)
    def test_cli_with_syntax_error(self, mock_input):
        mock_input.write("def my_function():\n    x = 10\n    if x is None\nEOF\n")
        mock_input.seek(0)
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            with self.assertRaises(SystemExit) as cm:
                run_cli()
            output = fake_out.getvalue().strip()
        
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("An error occurred during code analysis", output)

if __name__ == "__main__":
    unittest.main()