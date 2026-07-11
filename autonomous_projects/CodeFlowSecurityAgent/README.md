# CodeFlowSecurityAgent

## Overview
CodeFlowSecurityAgent is a security-focused agent designed to monitor and enforce secure coding practices in real-time. The project aims to help developers write more secure code by providing real-time feedback and enforcing predefined security rules.

## Architecture
The project is structured into several key components, each encapsulated in its own file:

- **`code_flow_security_agent.py`**: Contains the `CodeFlowSecurityAgent` class, which is responsible for analyzing and enforcing security rules on the provided code.
- **`security_rules.py`**: Defines the `SecurityRules` class and provides methods to manage and initialize default security rules.
- **`ide_integration.py`**: Provides functions to integrate the CodeFlowSecurityAgent with supported IDEs (PyCharm, VSCode, SublimeText).
- **`test_main.py`**: Contains unit tests for the `CodeFlowSecurityAgent`, `SecurityRules`, and IDE integration functionalities.
- **`.gitignore`**: Specifies files and directories to be ignored by Git.

## How it Works
1. **Define Security Rules**:
   - The `SecurityRules` class in `security_rules.py` manages a list of security rules. Default rules are initialized using the `initialize_default_rules` function.
   
2. **Real-Time Code Analysis**:
   - The `CodeFlowSecurityAgent` class in `code_flow_security_agent.py` analyzes the provided code against the defined security rules. It uses the Abstract Syntax Tree (AST) to parse the code and identify potential security issues.
   - The `analyze_code` method returns a dictionary of security issues, where each issue is represented as a tuple containing the line number, column number, and a message describing the issue.
   - The `enforce_rules` method checks if the provided code passes all the specified rules and returns a boolean indicating the result.

3. **IDE Integration**:
   - The `ide_integration.py` file provides functions to integrate the CodeFlowSecurityAgent with supported IDEs. The `integrate_with_ide` function handles the integration process, and specific integration logic for each IDE is implemented in internal functions (`_integrate_with_pycharm`, `_integrate_with_vscode`, `_integrate_with_sublimetext`).

4. **Testing**:
   - The `test_main.py` file contains unit tests for the `CodeFlowSecurityAgent`, `SecurityRules`, and IDE integration functionalities. These tests ensure that the core functionalities work as expected and help maintain the quality of the codebase.

## Setup and Installation
### Prerequisites
- Python 3.8 or higher
- Supported IDEs: PyCharm, VSCode, SublimeText

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repository/codeflowsecurityagent.git
   cd codeflowsecurityagent
   ```

2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Running the Tests
To run the unit tests, execute the following command:
```sh
python -m unittest discover -s tests
```

### Integrating with an IDE
To integrate the CodeFlowSecurityAgent with a supported IDE, use the `integrate_with_ide` function from `ide_integration.py`. For example, to integrate with PyCharm:
```python
from ide_integration import integrate_with_ide

integrate_with_ide("PyCharm")
```

## Contributing
Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on how to contribute to this project.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.