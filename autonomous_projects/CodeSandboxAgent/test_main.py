import unittest
import os
from sandbox import validate_code, execute_code
from security import sanitize_input, create_isolated_environment, cleanup_environment, check_disallowed_keywords, setup_secure_environment, teardown_secure_environment

class TestCodeSandboxAgent(unittest.TestCase):

    def test_validate_code(self):
        valid_code = "print('Hello, World!')"
        invalid_code = "exec('print(Hello, World!)')"
        self.assertTrue(validate_code(valid_code))
        self.assertFalse(validate_code(invalid_code))

    def test_execute_code(self):
        code = "print('Hello, World!')"
        output = execute_code(code)
        self.assertEqual(output.rstrip('\r\n'), "Hello, World!")

    def test_execute_code_invalid(self):
        code = "exec('print(Hello, World!)')"
        with self.assertRaises(ValueError):
            execute_code(code)

    def test_sanitize_input(self):
        input_str = "<script>alert('XSS')</script>"
        sanitized_str = sanitize_input(input_str)
        self.assertEqual(sanitized_str, "")

    def test_create_isolated_environment(self):
        env_path = create_isolated_environment()
        self.assertTrue(os.path.exists(env_path))
        teardown_secure_environment(env_path)

    def test_cleanup_environment(self):
        env_path = create_isolated_environment()
        cleanup_environment(env_path)
        self.assertFalse(os.path.exists(env_path))

    def test_check_disallowed_keywords(self):
        code = "exec('print(Hello, World!)')"
        disallowed_keywords = ['exec', 'eval', 'import']
        self.assertTrue(check_disallowed_keywords(code, disallowed_keywords))

    def test_setup_secure_environment(self):
        env_path = setup_secure_environment()
        self.assertTrue(os.path.exists(env_path))
        teardown_secure_environment(env_path)

    def test_teardown_secure_environment(self):
        env_path = setup_secure_environment()
        teardown_secure_environment(env_path)
        self.assertFalse(os.path.exists(env_path))

if __name__ == '__main__':
    unittest.main()
