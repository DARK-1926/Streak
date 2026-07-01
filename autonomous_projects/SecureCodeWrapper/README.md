# SecureCodeWrapper

## Overview
SecureCodeWrapper is a Python project designed to provide a secure environment for executing code. It ensures that the code runs in a sandboxed environment, isolated from the host's file system and network, thereby preventing any malicious actions.

## Architecture
The project is structured into several key components:
- **secure_code_wrapper.py**: Contains the main logic for initializing the environment and executing code.
- **sandbox_manager.py**: Manages the creation, isolation, and destruction of sandboxes.
- **api_handler.py**: Handles incoming API requests, parses them, and formats responses.
- **test_main.py**: A comprehensive test suite to validate the security and functionality of the project.
- **.gitignore**: Specifies files and directories to be ignored by Git.

## How it Works
1. **Environment Initialization**: The `initialize_environment` function in `secure_code_wrapper.py` sets up the necessary configurations and checks.
2. **Sandbox Creation**: When a request to execute code is received, a new sandbox is created using `create_sandbox` from `sandbox_manager.py`.
3. **Isolation**: The sandbox is isolated from the host's file system and network using `isolate_file_system` and `isolate_network` functions.
4. **Code Execution**: The provided code is executed in the sandbox using `execute_code` from `secure_code_wrapper.py`.
5. **Sandbox Destruction**: After the code execution, the sandbox is cleaned up and removed using `destroy_sandbox`.

## Security Measures
- **File System Isolation**: The sandbox has no access to the host's file system, preventing any read/write operations outside the sandbox.
- **Network Isolation**: The sandbox is isolated from the network, preventing any outbound or inbound network connections.
- **Exception Handling**: All critical operations are wrapped in try-except blocks to handle exceptions gracefully and provide meaningful error messages.
- **Temporary Directories**: Sandboxes are created in temporary directories, which are automatically cleaned up after use.

## Setup and Installation
### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/SecureCodeWrapper.git
   cd SecureCodeWrapper
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Running the Project
To run the project, you can use the following command:
```sh
python -m unittest discover
```
This will run the test suite defined in `test_main.py` to ensure everything is working as expected.

## Usage
### Executing Code
To execute code in a secure sandboxed environment, you can use the `execute_code` function from `secure_code_wrapper.py`. Here is an example:
```python
from secure_code_wrapper import execute_code

code = "def add(a, b): return a + b; result = add(1, 2)"
input_data = {}
result = execute_code(code, input_data)
print(result)  # Output: {'result': 3}
```

### API Handler
The `api_handler.py` module provides functions to handle incoming API requests. You can use these functions to integrate the project with a web server or other external systems.

### Testing
The `test_main.py` module contains a comprehensive test suite. To run the tests, use the following command:
```sh
python -m unittest discover
```

## Contributing
Contributions are welcome! Please follow the style guide and rules mentioned in the project documentation.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.