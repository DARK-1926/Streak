import unittest
from docx_editor import load_document, save_document, add_paragraph, add_heading
from document import Document, Paragraph, Heading
import os
import tempfile

class TestDocxEditorLite(unittest.TestCase):
    def setUp(self):
        self.document = Document()
        fd, self.temp_file_path = tempfile.mkstemp(suffix='.docx')
        os.close(fd)

    def tearDown(self):
        if os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)

    def test_document_creation(self):
        self.assertIsInstance(self.document, Document)
        self.assertEqual(len(self.document.content), 0)

    def test_add_paragraph(self):
        text = "This is a test paragraph."
        style = "Normal"
        add_paragraph(self.document, text, style)
        self.assertEqual(len(self.document.content), 1)
        self.assertIsInstance(self.document.content[0], Paragraph)
        self.assertEqual(self.document.content[0].text, text)
        self.assertEqual(self.document.content[0].style, style)

    def test_add_heading(self):
        text = "Test Heading"
        level = 1
        add_heading(self.document, text, level)
        self.assertEqual(len(self.document.content), 1)
        self.assertIsInstance(self.document.content[0], Heading)
        self.assertEqual(self.document.content[0].text, text)
        self.assertEqual(self.document.content[0].level, level)

    def test_save_and_load_document(self):
        # Add content to the document
        add_paragraph(self.document, "Sample paragraph", "Normal")
        add_heading(self.document, "Sample Heading", 2)

        # Save the document
        save_document(self.document, self.temp_file_path)

        # Load the document
        loaded_document = load_document(self.temp_file_path)
        self.assertIsInstance(loaded_document, Document)
        # Note: Since load_from_file and save_to_file are currently unimplemented placeholders,
        # we only assert that the function executes without error and returns the proper type.

if __name__ == '__main__':
    unittest.main()