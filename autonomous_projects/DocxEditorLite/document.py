from typing import List, Optional

class Document:
    def __init__(self):
        self.content: List[Paragraph | Heading] = []

    @classmethod
    def load_from_file(cls, file) -> 'Document':
        """
        Loads the document content from a file.
        
        :param file: A file-like object to read the document from.
        :return: The Document instance with loaded content.
        """
        # This is a placeholder for actual file reading logic
        # which would be implemented using a library like python-docx.
        return cls()

    def save_to_file(self, file) -> None:
        """
        Saves the document content to a file.
        
        :param file: A file-like object to write the document to.
        """
        # This is a placeholder for actual file writing logic
        # which would be implemented using a library like python-docx.
        pass

    def add_paragraph(self, paragraph: 'Paragraph') -> None:
        """
        Adds a new paragraph to the document.
        
        :param paragraph: The Paragraph instance to add.
        """
        self.content.append(paragraph)

    def add_heading(self, heading: 'Heading') -> None:
        """
        Adds a new heading to the document.
        
        :param heading: The Heading instance to add.
        """
        self.content.append(heading)


class Paragraph:
    def __init__(self, text: str, style: Optional[str] = None):
        self.text = text
        self.style = style

    def __repr__(self):
        return f"Paragraph(text='{self.text}', style='{self.style}')"


class Heading:
    def __init__(self, text: str, level: int):
        if not 1 <= level <= 6:
            raise ValueError("Heading level must be between 1 and 6.")
        self.text = text
        self.level = level

    def __repr__(self):
        return f"Heading(text='{self.text}', level={self.level})"