from typing import List, Tuple, Dict
import math

def calculate_budget(income: float, expenses: List[Tuple[str, float]]) -> Dict[str, float]:
    """
    Calculate the budget based on income and a list of expenses.
    
    :param income: Total monthly income.
    :param expenses: A list of tuples where each tuple contains (expense_name, expense_amount).
    :return: A dictionary with 'total_expenses', 'remaining_budget' and 'expenses_breakdown'.
    """
    total_expenses = sum(expense[1] for expense in expenses)
    remaining_budget = income - total_expenses
    expenses_breakdown = {name: amount for name, amount in expenses}
    
    return {
        'total_expenses': total_expenses,
        'remaining_budget': remaining_budget,
        'expenses_breakdown': expenses_breakdown
    }

def estimate_savings(monthly_income: float, monthly_expenses: float, savings_rate: float) -> float:
    """
    Estimate the savings based on monthly income, expenses, and a savings rate.
    
    :param monthly_income: Total monthly income.
    :param monthly_expenses: Total monthly expenses.
    :param savings_rate: The percentage of the remaining budget to save.
    :return: Estimated monthly savings.
    """
    if savings_rate < 0 or savings_rate > 1:
        raise ValueError("Savings rate must be between 0 and 1.")
    
    remaining_budget = monthly_income - monthly_expenses
    estimated_savings = remaining_budget * savings_rate
    return estimated_savings

def suggest_investments(savings: float, risk_tolerance: str) -> Dict[str, float]:
    """
    Suggest investment allocations based on savings and risk tolerance.
    
    :param savings: Total savings available for investment.
    :param risk_tolerance: Risk tolerance level ('low', 'medium', 'high').
    :return: A dictionary with suggested investment allocations.
    """
    if risk_tolerance not in ['low', 'medium', 'high']:
        raise ValueError("Risk tolerance must be one of 'low', 'medium', or 'high'.")
    
    if risk_tolerance == 'low':
        allocation = {'bonds': 0.7, 'stocks': 0.3}
    elif risk_tolerance == 'medium':
        allocation = {'bonds': 0.5, 'stocks': 0.5}
    else:
        allocation = {'bonds': 0.3, 'stocks': 0.7}
    
    suggested_investments = {asset: savings * rate for asset, rate in allocation.items()}
    return suggested_investments