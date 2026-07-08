# CodeDocumentationAgent

## Overview
CodeDocumentationAgent is a tool designed to automatically generate, update, and validate documentation for Python code. The project aims to keep documentation in sync with the codebase, ensuring that it remains accurate and up-to-date.

## Architecture
The CodeDocumentationAgent consists of three main modules:
- **Document Generator**: Responsible for parsing the code and generating documentation.
- **Document Updater**: Handles reading and writing files, as well as updating the documentation based on changes in the code.
- **Document Validator**: Ensures that the generated and updated documentation is accurate and consistent.

### Document Generator
- **`document_generator.py`**:
  - `parse_code(code: str) -> Dict[str, List[ast.AST]]`: Parses the given Python code and extracts top-level definitions (functions, classes).
  - `generate_documentation_for_function(func_node: ast.FunctionDef) -> str`: Generates documentation for a single function.
  - `generate_documentation_for_class(class_node: ast.ClassDef) -> str`: Generates documentation for a single class.
  - `generate_documentation(codebase: Union[str, os.PathLike]) -> str`: Generates documentation for the entire codebase, which can be provided as a string or a file path.

### Document Updater
- **`document_updater.py`**:
  - `read_file(file_path: Union[str, os.PathLike]) -> str`: Reads the content of a file and returns it as a string.
  - `write_file(file_path: Union[str, os.PathLike], content: str) -> None`: Writes the given content to a file.
  - `get_documentation_map(documentation: str) -> Dict[str, str]`: Parses the documentation and creates a map from function/class names to their documentation.
  - `update_documentation(old_doc: Union[str, os.PathLike], new_codebase: Union[str, os.PathLike]) -> str`: Updates the existing documentation based on the new codebase.

### Document Validator
- **`document_validator.py`**:
  - `validate_documentation(documentation: str) -> bool`: Validates the generated or updated documentation for accuracy and consistency.

### Testing
- **`test_main.py`**: Contains unit tests for the document generation, update, and validation processes to ensure the correctness of the implementation.

## How It Works
1. **Document Generation**:
   - The `document_generator.py` module parses the provided Python code using the Abstract Syntax Tree (AST) and generates Markdown-formatted documentation for functions and classes.
   - The `generate_documentation` function can take either a string containing the code or a file path to a Python file.

2. **Document Update**:
   - The `document_updater.py` module reads the existing documentation and the new codebase.
   - It updates the documentation by comparing the old and new code, and writes the updated documentation back to the file.

3. **Document Validation**:
   - The `document_validator.py` module checks the generated or updated documentation for accuracy and consistency.
   - It ensures that all functions and classes have proper docstrings and that the formatting is correct.

## Setup and Installation
### Prerequisites
- Python 3.8 or higher
- `ast` (built-in)
- `os` (built-in)
- `tempfile` (built-in)
- `re` (built-in)

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/CodeDocumentationAgent.git
   cd CodeDocumentationAgent
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Running the Project
To run the CodeDocumentationAgent, you can use the following commands:

1. Generate documentation for a codebase:
   ```sh
   python document_generator.py <path_to_python_file>
   ```

2. Update the documentation based on changes in the codebase:
   ```sh
   python document_updater.py <path_to_old_documentation> <path_to_new_codebase>
   ```

3. Validate the generated or updated documentation:
   ```sh
   python document_validator.py <path_to_documentation>
   ```

### Running Tests
To run the unit tests, use the following command:
```sh
python -m unittest test_main.py
```

## Contributing
Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.