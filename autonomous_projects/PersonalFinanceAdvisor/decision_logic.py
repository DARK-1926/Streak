from typing import Dict, List, Tuple
import finance_model

def make_financial_decision(income: float, expenses: List[Tuple[str, float]], savings_rate: float, risk_tolerance: str) -> Dict[str, any]:
    """
    Make a financial decision based on the provided income, expenses, savings rate, and risk tolerance.
    
    :param income: Total monthly income.
    :param expenses: A list of tuples where each tuple contains (expense_name, expense_amount).
    :param savings_rate: The percentage of the remaining budget to save.
    :param risk_tolerance: Risk tolerance level ('low', 'medium', 'high').
    :return: A dictionary with financial advice including budget, savings, and investment suggestions.
    """
    try:
        # Calculate the budget
        budget = finance_model.calculate_budget(income, expenses)
        
        # Estimate savings
        estimated_savings = finance_model.estimate_savings(income, budget['total_expenses'], savings_rate)
        
        # Suggest investments
        investment_suggestions = finance_model.suggest_investments(estimated_savings, risk_tolerance)
        
        return {
            'budget': budget,
            'savings': estimated_savings,
            'investment_suggestions': investment_suggestions
        }
    except Exception as e:
        # Handle exceptions gracefully
        return {
            'error': str(e)
        }