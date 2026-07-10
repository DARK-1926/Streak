import unittest
from finance_model import calculate_budget, estimate_savings, suggest_investments
from decision_logic import make_financial_decision

class TestFinanceModel(unittest.TestCase):
    def test_calculate_budget(self):
        income = 5000.0
        expenses = [('Rent', 1500.0), ('Utilities', 200.0), ('Groceries', 300.0)]
        result = calculate_budget(income, expenses)
        self.assertEqual(result['total_expenses'], 2000.0)
        self.assertEqual(result['remaining_budget'], 3000.0)
        self.assertDictEqual(result['expenses_breakdown'], {'Rent': 1500.0, 'Utilities': 200.0, 'Groceries': 300.0})

    def test_estimate_savings(self):
        monthly_income = 5000.0
        monthly_expenses = 2000.0
        savings_rate = 0.2
        result = estimate_savings(monthly_income, monthly_expenses, savings_rate)
        self.assertEqual(result, 600.0)

    def test_suggest_investments_low_risk(self):
        savings = 1000.0
        risk_tolerance = 'low'
        result = suggest_investments(savings, risk_tolerance)
        self.assertDictEqual(result, {'bonds': 700.0, 'stocks': 300.0})

    def test_suggest_investments_medium_risk(self):
        savings = 1000.0
        risk_tolerance = 'medium'
        result = suggest_investments(savings, risk_tolerance)
        self.assertDictEqual(result, {'bonds': 500.0, 'stocks': 500.0})

    def test_suggest_investments_high_risk(self):
        savings = 1000.0
        risk_tolerance = 'high'
        result = suggest_investments(savings, risk_tolerance)
        self.assertDictEqual(result, {'bonds': 300.0, 'stocks': 700.0})

    def test_suggest_investments_invalid_risk(self):
        savings = 1000.0
        risk_tolerance = 'very high'
        with self.assertRaises(ValueError):
            suggest_investments(savings, risk_tolerance)

class TestDecisionLogic(unittest.TestCase):
    def test_make_financial_decision(self):
        income = 5000.0
        expenses = [('Rent', 1500.0), ('Utilities', 200.0), ('Groceries', 300.0)]
        savings_rate = 0.2
        risk_tolerance = 'low'
        result = make_financial_decision(income, expenses, savings_rate, risk_tolerance)
        self.assertEqual(result['budget']['total_expenses'], 2000.0)
        self.assertEqual(result['budget']['remaining_budget'], 3000.0)
        self.assertDictEqual(result['budget']['expenses_breakdown'], {'Rent': 1500.0, 'Utilities': 200.0, 'Groceries': 300.0})
        self.assertEqual(result['savings'], 600.0)
        self.assertDictEqual(result['investment_suggestions'], {'bonds': 420.0, 'stocks': 180.0})

    def test_make_financial_decision_invalid_risk(self):
        income = 5000.0
        expenses = [('Rent', 1500.0), ('Utilities', 200.0), ('Groceries', 300.0)]
        savings_rate = 0.2
        risk_tolerance = 'very high'
        result = make_financial_decision(income, expenses, savings_rate, risk_tolerance)
        self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main()