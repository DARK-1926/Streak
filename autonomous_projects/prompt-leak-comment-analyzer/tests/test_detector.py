import unittest
from prompt_leak_analyzer.detector import detect, strip

SAMPLE = """def foo():
    # Prompt: use default values
    return 42

# Prompt: this is a leak comment
print(foo())
"""

class TestPromptLeakDetector(unittest.TestCase):
    def test_detect(self):
        hits = detect(SAMPLE)
        self.assertEqual(len(hits), 2)
        self.assertEqual(hits[0][0], 2)  # line 2
        self.assertEqual(hits[1][0], 5)  # line 5

    def test_strip(self):
        cleaned = strip(SAMPLE)
        self.assertNotIn("Prompt:", cleaned)
        self.assertIn("def foo():", cleaned)
        self.assertIn("return 42", cleaned)
        self.assertIn("print(foo())", cleaned)

if __name__ == "__main__":
    unittest.main()
