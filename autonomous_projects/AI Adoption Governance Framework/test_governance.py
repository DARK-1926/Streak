#!/usr/bin/env python3
"""Tests for AI Adoption Governance Framework"""

import unittest
import sys
sys.path.insert(0, '.')

from ai_governance import UseCase, evaluate_use_case

class TestAIGovernance(unittest.TestCase):
    def test_evaluate_high_score_use_case(self):
        """Test evaluation of high-scoring use case"""
        use_case = UseCase(
            name='Test Project',
            business_value=9,
            technical_feasibility=8,
            data_availability=9,
            compliance_risk=2,
            implementation_effort=7
        )
        result = evaluate_use_case(use_case)
        self.assertEqual(result['recommendation'], 'APPROVED')
        self.assertGreaterEqual(result['total_score'], 7)
    
    def test_evaluate_low_score_use_case(self):
        """Test evaluation of low-scoring use case"""
        use_case = UseCase(
            name='Test Project',
            business_value=3,
            technical_feasibility=4,
            data_availability=3,
            compliance_risk=8,
            implementation_effort=9
        )
        result = evaluate_use_case(use_case)
        self.assertEqual(result['recommendation'], 'REVIEW_REQUIRED')
        self.assertLess(result['total_score'], 7)

if __name__ == '__main__':
    unittest.main()
