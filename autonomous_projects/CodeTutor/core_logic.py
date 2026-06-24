from typing import List, Dict, Any
import importlib

class Lesson:
    def __init__(self, title: str, content: str, exercises: List[Dict[str, Any]]):
        self.title = title
        self.content = content
        self.exercises = exercises

    def get_exercise(self, index: int) -> Dict[str, Any]:
        """Retrieve an exercise by its index."""
        if 0 <= index < len(self.exercises):
            return self.exercises[index]
        raise IndexError("Exercise index out of range")

def load_lesson(lesson_path: str) -> Lesson:
    """Load a lesson from the given path. The path should be in the format 'module_name.LessonClassName'."""
    module_name, class_name = lesson_path.rsplit('.', 1)
    try:
        module = importlib.import_module(module_name)
        lesson_class = getattr(module, class_name)
        return lesson_class()
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Failed to load lesson from {lesson_path}: {e}")

class CoreLogic:
    def __init__(self, llm, lesson_loader: callable):
        self.llm = llm
        self.lesson_loader = lesson_loader
        self.current_lesson = None

    def set_current_lesson(self, lesson_path: str) -> None:
        """Set the current lesson using the provided lesson path."""
        self.current_lesson = self.lesson_loader(lesson_path)

    def process_user_input(self, user_input: str) -> str:
        """Process the user input and generate a response using the LLM."""
        if not self.current_lesson:
            return "No lesson is currently loaded. Please load a lesson first."
        
        try:
            response = self.llm.generate_response(user_input, context=self.current_lesson.content)
            return response
        except Exception as e:
            return f"An error occurred while processing your request: {str(e)}"

    def get_feedback(self, exercise_index: int, user_solution: str) -> str:
        """Get feedback on the user's solution for a specific exercise."""
        if not self.current_lesson:
            return "No lesson is currently loaded. Please load a lesson first."
        
        try:
            exercise = self.current_lesson.get_exercise(exercise_index)
            expected_solution = exercise['solution']
            feedback = self.llm.provide_feedback(user_solution, expected_solution)
            return feedback
        except IndexError:
            return "Exercise index out of range. Please check the exercise number."
        except Exception as e:
            return f"An error occurred while providing feedback: {str(e)}"