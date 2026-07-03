import subprocess
import tempfile
import os
import re

def validate_code(code: str) -> bool:
    """
    Validates the input code for potential security issues.
    
    Args:
        code (str): The code snippet to be validated.
    
    Returns:
        bool: True if the code is valid, False otherwise.
    """
    # Define a list of disallowed keywords and patterns
    disallowed_keywords = ['exec', 'eval', 'import', 'open', 'os', 'sys', 'subprocess']
    disallowed_patterns = [re.compile(rf'\b{keyword}\b') for keyword in disallowed_keywords]

    # Check for disallowed keywords
    for pattern in disallowed_patterns:
        if pattern.search(code):
            return False

    return True

def execute_code(code: str) -> str:
    """
    Executes the provided code in an isolated environment and returns the output.
    
    Args:
        code (str): The code snippet to be executed.
    
    Returns:
        str: The output of the code execution.
    """
    if not validate_code(code):
        raise ValueError("Invalid code. Contains disallowed keywords or patterns.")

    try:
        # Create a temporary file to write the code
        fd, path = tempfile.mkstemp(suffix='.py')
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(code)

        # Execute the code in a subprocess
        result = subprocess.run(
            ['python', path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            check=True
        )

        # Read the output
        output = result.stdout.decode('utf-8')

    except subprocess.CalledProcessError as e:
        output = f"Execution failed: {e.stderr.decode('utf-8')}"

    except subprocess.TimeoutExpired:
        output = "Execution timed out."

    finally:
        # Clean up the temporary file
        os.remove(path)

    return output