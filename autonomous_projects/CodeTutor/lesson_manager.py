import json
from typing import List, Dict, Any
from core_logic import Lesson, load_lesson

class LessonManager:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.lessons: List[Dict[str, Any]] = []
        self.current_lesson_index: int = 0
        self.load_lessons()

    def load_lessons(self) -> None:
        """Load lessons from the storage file."""
        try:
            with open(self.storage_path, 'r') as file:
                self.lessons = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.lessons = []

    def save_lessons(self) -> None:
        """Save the current state of lessons to the storage file."""
        with open(self.storage_path, 'w') as file:
            json.dump(self.lessons, file, indent=4)

    def add_lesson(self, lesson: Dict[str, Any]) -> None:
        """Add a new lesson to the list and save it."""
        self.lessons.append(lesson)
        self.save_lessons()

    def get_current_lesson(self) -> Dict[str, Any]:
        """Get the current lesson based on the current index."""
        if 0 <= self.current_lesson_index < len(self.lessons):
            return self.lessons[self.current_lesson_index]
        raise IndexError("Current lesson index out of range")

    def move_to_next_lesson(self) -> None:
        """Move to the next lesson in the list."""
        if self.current_lesson_index + 1 < len(self.lessons):
            self.current_lesson_index += 1
        else:
            raise IndexError("No more lessons available")

    def move_to_previous_lesson(self) -> None:
        """Move to the previous lesson in the list."""
        if self.current_lesson_index - 1 >= 0:
            self.current_lesson_index -= 1
        else:
            raise IndexError("Already at the first lesson")

    def set_current_lesson_by_index(self, index: int) -> None:
        """Set the current lesson by its index."""
        if 0 <= index < len(self.lessons):
            self.current_lesson_index = index
        else:
            raise IndexError("Lesson index out of range")

    def get_lesson_by_path(self, lesson_path: str) -> Lesson:
        """Load a lesson from the given path and return it."""
        return load_lesson(lesson_path)

    def update_lesson(self, index: int, updated_lesson: Dict[str, Any]) -> None:
        """Update an existing lesson in the list and save it."""
        if 0 <= index < len(self.lessons):
            self.lessons[index] = updated_lesson
            self.save_lessons()
        else:
            raise IndexError("Lesson index out of range")

    def remove_lesson(self, index: int) -> None:
        """Remove a lesson from the list and save the changes."""
        if 0 <= index < len(self.lessons):
            del self.lessons[index]
            self.save_lessons()
        else:
            raise IndexError("Lesson index out of range")