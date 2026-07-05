import ast
import io
import sys
from typing import Dict, Any
def execute_code(code: str, builtins: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute Python code safely and return structured result."""
    if builtins is None:
        builtins = {}
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    try:
        # Compile and execute in isolated namespace
        compiled = compile(code, '<string>', 'exec')
        namespace = {'__builtins__': {**__builtins__, **builtins}}
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(compiled, namespace)
        return {
            'success': True,
            'data': {
                'stdout': stdout_capture.getvalue(),
                'stderr': stderr_capture.getvalue()
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': {
                'stdout': stdout_capture.getvalue(),
                'stderr': stderr_capture.getvalue()
            }
        }

class redirect_stdout:
    def __init__(self, new_target):
        self._new_target = new_target
        self._old_target = None
    def __enter__(self):
        self._old_target = sys.stdout
        sys.stdout = self._new_target
        return self._new_target
    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self._old_target

class redirect_stderr:
    def __init__(self, new_target):
        self._new_target = new_target
        self._old_target = None
    def __enter__(self):
        self._old_target = sys.stderr
        sys.stderr = self._new_target
        return self._new_target
    def __exit__(self, exc_type, exc_value, traceback):
        sys.stderr = self._old_target

def validate_code(code: str) -> bool:
    """
    Validates the provided Python code to check for syntax errors.
    
    :param code: A string containing the Python code to be validated.
    :return: True if the code is valid, False otherwise.
    """
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False
