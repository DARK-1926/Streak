import unittest
from core_logic import execute_code, validate_code
from security import sanitize_input
from feedback import provide_feedback

class TestCoreLogic(unittest.TestCase):
    def test_execute_code(self) -> None:
        """Test the execute_code function."""
        code = "print('Hello, world!')"
        result = execute_code(code, {'print': print})
        self.assertIn('Hello, world!', result.get('data', {}).get('stdout', ''))

    def test_validate_code(self) -> None:
        """Test the validate_code function."""
        valid_code = "def add(a, b): return a + b"
        invalid_code = 'def add(a, b): return a + b +'  # Syntax error: incomplete expression
        self.assertTrue(validate_code(valid_code))
        self.assertFalse(validate_code(invalid_code))

class TestSecurity(unittest.TestCase):
    def test_sanitize_input(self) -> None:
        """Test the sanitize_input function."""
        input_data = "<script>alert('XSS')</script>"
        sanitized_data = sanitize_input(input_data)
        self.assertNotIn("<script>", sanitized_data)
        self.assertNotIn("</script>", sanitized_data)

class TestFeedback(unittest.TestCase):
    def test_provide_feedback(self) -> None:
        """Test the provide_feedback function."""
        code = "def add(a, b): return a + b"
        feedback = provide_feedback(code, result={'result': 'Code executed successfully', 'data': {}})
        self.assertIsInstance(feedback, str)
        self.assertNotEqual(feedback, "")

if __name__ == "__main__":
    unittest.main()
