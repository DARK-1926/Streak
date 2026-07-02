# CodeReviewAgent

## Overview
CodeReviewAgent is a tool designed to provide automated code review and feedback for Python code. It helps developers improve their code quality, maintainability, and adherence to best practices. The project is divided into three milestones:
1. Implement core code analysis and feedback generation.
2. Integrate with a simple command-line interface (CLI).
3. Add unit tests and validation.

## How it Works
The CodeReviewAgent works by analyzing the provided Python code using the abstract syntax tree (AST) to perform static analysis. It checks for common issues such as unused imports, variable naming conventions, and potential bugs. The feedback is then presented to the user in a structured format.

### Core Components
- **code_reviewer.py**: Contains the main functions for code analysis.
- **cli.py**: Provides a command-line interface for the CodeReviewAgent.
- **test_code_reviewer.py**: Contains unit tests for the code analysis functions.
- **test_cli.py**: Contains integration tests for the CLI.

## Installation
To install and run the CodeReviewAgent, follow these steps:

1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/code-review-agent.git
   cd code-review-agent
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Run the CLI:
   ```sh
   python cli.py
   ```

## Usage
### Command-Line Interface (CLI)
The CLI allows you to input Python code and receive feedback on various aspects of the code. Here's how to use it:

1. Start the CLI:
   ```sh
   python cli.py
   ```

2. Enter your Python code. Type `EOF` on a new line to signal the end of your code.

3. Review the feedback provided by the CodeReviewAgent.

### Example
```python
import os
def my_function():
    x = 10
    if x == None:
        print('None')
```

Feedback:
```
Unused Imports Issues:
- Unused import: os

Naming Conventions Issues:
- Invalid name for FunctionDef: my_function

Potential Bugs Issues:
- Use 'is' to compare with None, not '=='
```

## Design Decisions
- **AST-based Analysis**: Using the AST allows for a detailed and accurate analysis of the code structure.
- **Modular Architecture**: The project is divided into separate modules for code analysis, CLI, and testing, making it easier to maintain and extend.
- **Type Hints and Docstrings**: All public classes and methods have type hints and docstrings for better readability and maintainability.
- **Graceful Exception Handling**: Exceptions are handled gracefully to provide meaningful error messages to the user.

## Known Limitations
- **Static Analysis Limitations**: The tool currently relies on static analysis, which may not catch all runtime issues.
- **Limited Scope**: The current implementation focuses on a few specific issues (unused imports, naming conventions, and potential bugs). Future versions will include more comprehensive checks.
- **CLI Input**: The CLI currently reads input from the standard input. Future versions may support reading from files or other sources.

## Testing
The project includes unit tests and integration tests to ensure the reliability and correctness of the code. The tests are located in `test_code_reviewer.py` and `test_cli.py`.

### Running Tests
To run the tests, use the following command:
```sh
python -m unittest discover
```

This will execute all the tests in the `test_code_reviewer.py` and `test_cli.py` files.

## Contributing
Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on how to contribute to the project.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.