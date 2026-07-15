# HNContentIntegrityAgent

## Overview
HNContentIntegrityAgent is a specialized tool designed to enhance content integrity on Hacker News (HN) by flagging and categorizing AI-generated content. The agent uses natural language processing (NLP) techniques to analyze and classify articles, providing users with a clear indicator of whether the content is AI-generated.

## Architecture
The project is structured in a modular, test-driven manner to ensure robustness and maintainability. Here's a breakdown of the key components:

- **hn_content_fetcher.py**: Fetches the latest articles from Hacker News.
- **ai_detection_model.py**: Loads training data, trains an NLP model, and predicts whether text is AI-generated.
- **content_flagger.py**: Flags AI-generated content in the fetched articles.
- **test_main.py**: Contains unit tests for the project.
- **.gitignore**: Specifies files and directories to be ignored by Git.

## How it Works
1. **Fetching Articles**:
   - `fetch_hn_articles` in `hn_content_fetcher.py` fetches the latest articles from Hacker News using the HN API.
   - It retrieves the top 10 stories and extracts their titles, URLs, and text.

2. **Training the Model**:
   - `load_training_data` in `ai_detection_model.py` loads a dataset of texts and their corresponding labels (AI-generated or human-written).
   - `train_model` trains a logistic regression model using TF-IDF vectorization.

3. **Flagging Content**:
   - `flag_ai_generated_content` in `content_flagger.py` uses the trained model to predict whether each article's text is AI-generated.
   - It updates each article with a `is_ai_generated` key set to `True` or `False`.

4. **Testing**:
   - `test_main.py` contains unit tests to ensure the correctness of the fetching, training, and flagging processes.

## Design Decisions
- **Modular Design**: The project is divided into distinct modules, each responsible for a specific task. This makes the codebase easier to understand, test, and maintain.
- **Test-Driven Development (TDD)**: Unit tests are written to cover all critical functionalities, ensuring that the system behaves as expected and facilitating future development and refactoring.
- **Robust Error Handling**: The code includes comprehensive error handling to gracefully manage exceptions and provide meaningful feedback.

## Setup
### Prerequisites
- Python 3.8 or higher
- `requests`, `scikit-learn`, and `joblib` libraries

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/HNContentIntegrityAgent.git
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

## Running the Tests
To run the unit tests, execute the following command:
```sh
python -m unittest discover -s tests
```

This will run all the tests defined in `test_main.py` and provide a detailed report on the test results.

## Usage
To run the HNContentIntegrityAgent and generate a report of AI-generated content, execute the following command:
```sh
python content_flagger.py
```

This will fetch the latest articles from Hacker News, train the AI detection model, flag the AI-generated content, and print the results. Additionally, the results will be saved to `ai_generated_content_report.txt` for further analysis.