import os
import sys
from typing import List, Tuple
import decision_logic

def get_user_input() -> Tuple[float, List[Tuple[str, float]], float, str]:
    """
    Collects user input for income, expenses, savings rate, and risk tolerance.
    
    :return: A tuple containing the collected data.
    """
    try:
        # Get monthly income
        income = float(input("Enter your total monthly income: "))

        # Get expenses
        num_expenses = int(input("How many different types of expenses do you have? "))
        expenses = []
        for _ in range(num_expenses):
            name = input("Enter the name of the expense: ")
            amount = float(input(f"Enter the amount for {name}: "))
            expenses.append((name, amount))

        # Get savings rate
        savings_rate = float(input("Enter your savings rate (as a decimal, e.g., 0.2 for 20%): "))

        # Get risk tolerance
        risk_tolerance = input("Enter your risk tolerance (low, medium, high): ").lower()
        if risk_tolerance not in ['low', 'medium', 'high']:
            raise ValueError("Risk tolerance must be one of 'low', 'medium', or 'high'.")

        return income, expenses, savings_rate, risk_tolerance
    except ValueError as e:
        print(f"Invalid input: {e}")
        sys.exit(1)

def display_results(results: dict) -> None:
    """
    Displays the results of the financial decision to the user.
    
    :param results: A dictionary containing the financial advice.
    """
    if 'error' in results:
        print(f"Error: {results['error']}")
        return

    budget = results['budget']
    savings = results['savings']
    investment_suggestions = results['investment_suggestions']

    print("\nFinancial Advice:")
    print(f"Total Expenses: ${budget['total_expenses']:.2f}")
    print(f"Remaining Budget: ${budget['remaining_budget']:.2f}")
    print("Expenses Breakdown:")
    for name, amount in budget['expenses_breakdown'].items():
        print(f" - {name}: ${amount:.2f}")

    print(f"\nEstimated Monthly Savings: ${savings:.2f}")

    print("\nInvestment Suggestions:")
    for investment, allocation in investment_suggestions.items():
        print(f" - {investment}: ${allocation:.2f}")

def main() -> None:
    """
    Main function to run the user interface and process the financial decision.
    """
    try:
        income, expenses, savings_rate, risk_tolerance = get_user_input()
        results = decision_logic.make_financial_decision(income, expenses, savings_rate, risk_tolerance)
        display_results(results)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()