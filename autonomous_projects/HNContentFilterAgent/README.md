# HNContentFilterAgent

## Overview
The HNContentFilterAgent is a tool designed to identify and flag AI-generated content on Hacker News. It provides a user-friendly interface to filter such content, making it easier for users to focus on human-generated content.

## Architecture
The HNContentFilterAgent is structured into several key components:
- **Text Analysis Module (`text_analysis.py`)**: Analyzes text to determine if it is likely as AI-generated.
- **Hacker News API Integration (`hn_api_integration.py`)**: Fetches stories from the Hacker News API and flags them based on the text analysis.
- **User Interface (`user_interface.py`)**: Provides a command-line interface for users to fetch, display, and filter stories.
- **Testing Suite (`test_main.py`)**: Contains unit and integration tests to ensure the reliability of the system.

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/HNContentFilterAgent.git
   cd HNContentFilterAgent
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

## Usage
To run the HNContentFilterAgent, execute the following command:
```sh
python user_interface.py
```

### How it Works
1. **Fetching Stories**: The `get_hn_stories` function in `hn_api_integration.py` fetches a list of stories from the Hacker News API.
2. **Analyzing Text**: Each story's text is analyzed by the `analyze_text` function in `text_analysis.py` to check for repetitive patterns, unusual punctuation, and other characteristics indicative of AI-generated content.
3. **Flagging Stories**: The `flag_story` function in `hn_api_integration.py` uses the results of the text analysis to flag stories as AI-generated.
4. **Displaying and Filtering**: The `display_stories` and `filter_stories` functions in `user_interface.py` are used to display all fetched stories and then filter out the flagged AI-generated stories.

## Running Tests
To run the test suite, execute the following command:
```sh
python -m unittest discover -s tests
```

This will run all the tests defined in `test_main.py`, including unit tests for each component and integration tests for the entire system.

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your fork.
5. Submit a pull request to the main repository.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.