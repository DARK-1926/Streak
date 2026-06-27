from typing import Optional
from document import Document, Paragraph, Heading

def load_document(file_path: str) -> Document:
    """
    Loads a DOCX document from the specified file path and returns a Document object.
    
    :param file_path: The path to the DOCX file.
    :return: A Document object representing the loaded document.
    """
    try:
        with open(file_path, 'rb') as file:
            document = Document.load_from_file(file)
        return document
    except Exception as e:
        raise IOError(f"Failed to load document: {e}")

def save_document(document: Document, file_path: str) -> None:
    
    """
    Saves the provided Document object to the specified file path.
    
    :param document: The Document object to save.
    :param file_path: The path where the document should be saved.
    """
    try:
        with open(file_path, 'wb') as file:
            document.save_to_file(file)
    except Exception as e:
        raise IOError(f"Failed to save document: {e}")

def add_paragraph(document: Document, text: str, style: Optional[str] = None) -> None:
    """
    Adds a new paragraph to the document with the given text and optional style.
    
    :param document: The Document object to which the paragraph will be added.
    :param text: The text content of the paragraph.
    :param style: An optional style for the paragraph.
    """
    try:
        paragraph = Paragraph(text, style=style)
        document.add_paragraph(paragraph)
    except Exception as e:
        raise ValueError(f"Failed to add paragraph: {e}")

def add_heading(document: Document, text: str, level: int) -> None:
    """
    Adds a new heading to the document with the given text and heading level.
    
    :param document: The Document object to which the heading will be added.
    :param text: The text content of the heading.
    :param level: The heading level (1-6).
    """
    if not 1 <= level <= 6:
        raise ValueError("Heading level must be between 1 and 6.")
    try:
        heading = Heading(text, level=level)
        document.add_heading(heading)
    except Exception as e:
        raise ValueError(f"Failed to add heading: {e}")
