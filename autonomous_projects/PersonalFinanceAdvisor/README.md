# PersonalFinanceAdvisor

## Overview
PersonalFinanceAdvisor is a Python application designed to assist users in making informed financial decisions. The application provides functionalities for budgeting, savings estimation, and investment suggestions based on the user's income, expenses, savings rate, and risk tolerance.

## Architecture
The project is structured into several key components:
- **finance_model.py**: Contains functions for calculating the budget, estimating savings, and suggesting investments.
- **decision_logic.py**: Implements the decision-making logic that integrates the outputs from `finance_model.py` to provide comprehensive financial advice.
- **user_interface.py**: Handles user input and output, providing a simple command-line interface.
- **test_main.py**: Contains unit tests for the core financial models and decision logic to ensure the correctness of the application.
- **.gitignore**: Specifies files and directories to be ignored by Git.

## How it Works
1. **User Input Collection**:
   - The user is prompted to enter their total monthly income.
   - The user specifies the number and details of their monthly expenses.
   - The user inputs their savings rate and risk tolerance level.

2. **Budget Calculation**:
   - The `calculate_budget` function in `finance_model.py` computes the total expenses, remaining budget, and a breakdown of expenses.

3. **Savings Estimation**:
   - The `estimate_savings` function in `finance_model.py` calculates the estimated savings based on the remaining budget and the specified savings rate.

4. **Investment Suggestions**:
   - The `suggest_investments` function in `finance_model.py` provides investment allocations based on the available savings and the user's risk tolerance.

5. **Financial Decision Making**:
   - The `make_financial_decision` function in `decision_logic.py` integrates the results from the budget calculation, savings estimation, and investment suggestions to provide a comprehensive financial advice.

6. **Display Results**:
   - The `display_results` function in `user_interface.py` presents the financial advice to the user, including the total expenses, remaining budget, and suggested investment allocations.

## Design Choices
- **Modular Design**: The project is divided into distinct modules (`finance_model.py`, `decision_logic.py`, `user_interface.py`) to promote code reusability and maintainability.
- **Type Hints and Docstrings**: All public functions and classes are annotated with type hints and include detailed docstrings to enhance readability and ease of use.
- **Exception Handling**: The application gracefully handles exceptions, providing meaningful error messages to the user.
- **Testing Strategy**: Unit tests in `test_main.py` ensure the correctness of the core financial models and decision logic, while integration tests can be added to validate the overall system behavior.

## Setup and Installation
### Prerequisites
- Python 3.8 or higher
- A virtual environment (optional but recommended)

### Installation Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/PersonalFinanceAdvisor.git
   cd PersonalFinanceAdvisor
   ```

2. Create and activate a virtual environment (optional):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install any required dependencies (if applicable):
   ```sh
   pip install -r requirements.txt
   ```

### Running the Application
To run the application, execute the following command:
```sh
python user_interface.py
```

Follow the prompts to enter your financial information, and the application will provide you with personalized financial advice.

## Testing
To run the unit tests, use the following command:
```sh
python -m unittest test_main.py
```

This will execute all the tests defined in `test_main.py` and provide feedback on the test results.

## Contributing
Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for more details on how to contribute to this project.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.