import sys
from typing import Dict, List

from code_reviewer import analyze_code


def run_cli() -> None:
    """
    Provides a command-line interface for the CodeReviewAgent. It prompts the user to input Python code,
    calls the `analyze_code` function from `code_reviewer.py`, and displays the feedback to the user.
    """
    print("Welcome to CodeReviewAgent CLI!")
    print("Please enter the Python code you would like to review (type 'EOF' on a new line to finish):")
    
    lines = []
    try:
        while True:
            line = input()
            if line == "EOF":
                break
            lines.append(line)
    except EOFError:
        print("\nUnexpected EOF. Please make sure to type 'EOF' on a new line to signal the end of your code.")
        sys.exit(1)

    code = '\n'.join(lines)
    if not code:
        print("No code provided. Exiting.")
        sys.exit(0)

    try:
        feedback = analyze_code(code)
    except Exception as e:
        print(f"An error occurred during code analysis: {e}")
        sys.exit(1)

    print("\nCode Review Feedback:")
    for category, messages in feedback.items():
        if messages:
            print(f"\n{category.replace('_', ' ').title()} Issues:")
            for message in messages:
                print(f"- {message}")

if __name__ == "__main__":
    run_cli()