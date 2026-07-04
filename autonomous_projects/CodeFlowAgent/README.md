# CodeFlowAgent

## Overview
CodeFlowAgent is a lightweight, efficient, and secure tool designed to help developers automate repetitive tasks such as code formatting, linting, and running tests. The agent is built to work seamlessly with existing development environments and supports cross-platform functionality.

## Architecture
The project is structured into several key components:

- **code_flow_agent.py**: Contains the core functionalities for formatting, linting, and running tests.
- **config_manager.py**: Manages the configuration settings for the agent.
- **file_system_handler.py**: Provides utilities for reading, writing, and managing files.
- **test_main.py**: Contains unit tests to ensure the reliability of the agent.
- **.gitignore**: Specifies files and directories to be ignored by Git.

## How It Works
### Code Formatting
- The `format_code` function in `code_flow_agent.py` formats the given code using a specified formatter function. By default, it uses `autopep8` as the formatter.
- The `default_formatter` function handles the actual formatting process, creating a temporary file, applying `autopep8`, and returning the formatted code.

### Code Linting
- The `lint_code` function in `code_flow_agent.py` lints the given code using a specified linter function. By default, it uses `pylint`.
- The `default_linter` function handles the linting process, similar to the `default_formatter`.

### Running Tests
- The `run_tests` function in `code_flow_agent.py` runs tests using a specified test runner function. By default, it uses `pytest`.
- The `default_test_runner` function handles the test execution process.

### Configuration Management
- The `ConfigManager` class in `config_manager.py` manages the configuration settings, including the default tools for formatting, linting, and testing.
- The configuration is stored in a JSON file, and the `ConfigManager` provides methods to load, save, and retrieve configuration settings.

### File System Handling
- The `file_system_handler.py` module provides functions for reading, writing, appending, and managing temporary files. These functions are used by the core functionalities to handle file operations.

## Setup
### Prerequisites
- Python 3.6 or higher
- `autopep8`, `pylint`, and `pytest` (can be installed via `pip`)

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/codeflowagent.git
   cd codeflowagent
   ```

2. Install the required dependencies:
   ```sh
   pip install autopep8 pylint pytest
   ```

3. Create a configuration file (e.g., `config.json`) with the following content:
   ```json
   {
       "formatter": "autopep8",
       "linter": "pylint",
       "test_runner": "pytest"
   }
   ```

4. Initialize the `ConfigManager` with the path to your configuration file:
   ```python
   from config_manager import ConfigManager
   config = ConfigManager('config.json')
   ```

## Usage
### Formatting Code
```python
from code_flow_agent import format_code, default_formatter

sample_code = "def test_func():\n    print('Hello, world!')\n"
formatted_code = format_code(sample_code, default_formatter)
print(formatted_code)
```

### Linting Code
```python
from code_flow_agent import lint_code, default_linter

sample_code = "def test_func():\n    print('Hello, world!')\n"
lint_result = lint_code(sample_code, default_linter)
print(lint_result)
```

### Running Tests
```python
from code_flow_agent import run_tests, default_test_runner

test_command = "pytest"
test_results = run_tests(test_command, default_test_runner)
print(test_results)
```

## Testing
To run the unit tests, use the following command:
```sh
python -m unittest discover -s .
```

This will execute all the tests defined in `test_main.py` and provide feedback on the functionality of the CodeFlowAgent.

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your changes to your fork.
5. Open a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.