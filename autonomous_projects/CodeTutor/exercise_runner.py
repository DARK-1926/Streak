import subprocess
import sys
import tempfile
import os

class ExerciseRunner:
    def __init__(self, exercise):
        self.exercise = exercise
        self.expected_output = exercise.get('expected_output', '').rstrip('\r\n')
        self.test_input = exercise.get('test_input', '')

    def run_and_check(self, user_code):
        # Write user code to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(user_code)
            temp_file = f.name

        try:
            # Run the script with input piped
            result = subprocess.run(
                [sys.executable, temp_file],
                input=self.test_input,
                text=True,
                capture_output=True,
                timeout=5
            )

            # Normalize both outputs: strip trailing newlines for fair comparison
            actual_output = (result.stdout + result.stderr).rstrip('\r\n')
            if result.returncode != 0:
                return f"Your solution crashed with error: {result.stderr.strip()}"

            if actual_output == self.expected_output:
                return "Your solution is correct!"
            else:
                return f"Your solution did not match the expected output. Expected: {self.expected_output!r}, but got: {actual_output!r}"

        except subprocess.TimeoutExpired:
            return "Your solution timed out."
        except Exception as e:
            return f"An error occurred while running your solution: {str(e)}"
        finally:
            os.unlink(temp_file)
import sys
import tempfile
import os

class ExerciseRunner:
    def __init__(self, exercise):
        self.exercise = exercise
        self.expected_output = exercise.get('expected_output', '').rstrip('\n') + '\n'
        self.test_input = exercise.get('test_input', '')

    def run_and_check(self, user_code):
        # Write user code to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(user_code)
            temp_file = f.name

        try:
            # Run the code with input piped
            result = subprocess.run(
                [sys.executable, temp_file],
                input=self.test_input,
                text=True,
                capture_output=True,
                timeout=5
            )

            # Normalize both outputs: ensure they end with exactly one '\n'
            actual_output = result.stdout
            if not actual_output.endswith('\n'):
                actual_output += '\n'
            # Compare normalized outputs
            if actual_output == self.expected_output:
                return "Your solution is correct!"
            else:
                return f"Your solution did not match the expected output. Expected: {repr(self.expected_output)}, but got: {repr(actual_output)}"

        except subprocess.TimeoutExpired:
            return "Your solution timed out."
        except Exception as e:
            return f"An error occurred while running your code: {str(e)}"
        finally:
            os.unlink(temp_file)
import sys
from typing import Callable, Any
from io import StringIO

class ExerciseRunner:
    def __init__(self, exercise: dict):
        self.exercise = exercise
        self.expected_output = exercise.get('expected_output', None)
        self.test_input = exercise.get('test_input', None)

    def _run_code(self, code: str, input_data: str) -> str:
        """Run the provided code with the given input and return the output."""
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()
        old_stdin = sys.stdin
        if input_data:
            sys.stdin = StringIO(input_data + '\n')
        
        try:
            exec(code, {})
        except Exception as e:
            return f"An error occurred: {str(e)}"
        finally:
            sys.stdout = old_stdout
            sys.stdin = old_stdin
        
        return redirected_output.getvalue().strip()

    def run_and_check(self, user_code: str) -> str:
        """
        Run the user's code and check if it matches the expected output.
        
        :param user_code: The code submitted by the user to be executed.
        :return: A message indicating whether the code was correct or not.
        """
        output = self._run_code(user_code, self.test_input)
        if output == self.expected_output:
            return "Your solution is correct!"
        else:
            return f"Your solution did not match the expected output. Expected: {self.expected_output}, but got: {output}"

def load_exercise(exercise_path: str) -> dict:
    """Load an exercise from the given path. The path should be in the format 'module_name.ExerciseName'."""
    module_name, exercise_name = exercise_path.rsplit('.', 1)
    try:
        module = importlib.import_module(module_name)
        exercise = getattr(module, exercise_name)
        return exercise
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Failed to load exercise from {exercise_path}: {e}")
