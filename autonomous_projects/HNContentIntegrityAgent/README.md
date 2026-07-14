# HNContentIntegrityAgent

## Overview
The HNContentIntegrityAgent is a tool designed to automatically flag and label AI-generated content on Hacker News, providing a clear indicator for users to skip such content. This project aims to enhance the integrity of the content on Hacker News by identifying and marking AI-generated posts.

## Architecture
The project is structured into several key components:
- **content_analyzer.py**: Contains functions for loading patterns and analyzing text.
- **flag_manager.py**: Handles the flagging of content as AI-generated or not.
- **hn_api_simulator.py**: Simulates the Hacker News API for testing purposes.
- **test_main.py**: Contains unit tests for the core functionalities.
- **.gitignore**: Specifies files and directories to be ignored by Git.

### How it Works
1. **Pattern Loading**: The `load_patterns` function in `content_analyzer.py` loads regex patterns from a file. These patterns are used to detect AI-generated text.
2. **Text Analysis**: The `analyze_text` function in `content_analyzer.py` uses the loaded patterns to analyze a given text and determine if it is likely to be AI-generated.
3. **Content Flagging**: The `flag_content` function in `flag_manager.py` updates a simulated database (JSON file) with the flag status of the content.
4. **API Simulation**: The `hn_api_simulator.py` simulates the Hacker News API, allowing the retrieval and updating of content flags.
5. **Testing**: The `test_main.py` contains a comprehensive suite of unit tests to ensure the correctness of the implementation.

## Setup and Installation
### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/HNContentIntegrityAgent.git
   cd HNContentIntegrityAgent
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

## File Descriptions
- **content_analyzer.py**:
  - `load_patterns(file_path: str) -> List[Tuple[re.Pattern, str]]`: Loads regex patterns and their descriptions from a file.
  - `analyze_text(text: str, patterns: List[Tuple[re.Pattern, str]]) -> bool`: Analyzes the given text against the loaded patterns to determine if it is AI-generated.

- **flag_manager.py**:
  - `flag_content(content_id: str, is_ai_generated: bool, db_path: str = 'content_flags.json') -> None`: Flags a piece of content as AI-generated or not in a simulated database (JSON file).

- **hn_api_simulator.py**:
  - `get_content_by_id(content_id: str) -> Optional[Dict[str, Any]]`: Retrieves content details by its unique identifier.
  - `update_content_flag(content_id: str, is_ai_generated: bool) -> None`: Updates the flag status of a piece of content in the simulated database.

- **test_main.py**:
  - Contains unit tests for the core functionalities of the project.

- **.gitignore**:
  - Specifies files and directories to be ignored by Git, such as virtual environments, cache files, and temporary files.

## Design Decisions
- **Pattern-based Detection**: Using regex patterns to detect AI-generated text allows for flexibility and easy updates. Patterns can be added or modified without changing the core logic.
- **Simulated Database**: A JSON file is used to simulate a database for storing content flags. This simplifies the setup and testing process.
- **Modular Structure**: The project is divided into modular components, each with a specific responsibility. This makes the codebase easier to maintain and test.
- **Comprehensive Testing**: A comprehensive suite of unit tests ensures that the core functionalities work as expected and helps in catching regressions.

By following these guidelines and using the provided tools, you can effectively set up and run the HNContentIntegrityAgent to help maintain the integrity of content on Hacker News.