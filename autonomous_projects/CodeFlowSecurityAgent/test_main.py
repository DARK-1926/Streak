import unittest
from code_flow_security_agent import CodeFlowSecurityAgent
from security_rules import SecurityRules, initialize_default_rules
from ide_integration import get_supported_ides, integrate_with_ide

class TestCodeFlowSecurityAgent(unittest.TestCase):
    def setUp(self):
        self.rules = initialize_default_rules()
        self.agent = CodeFlowSecurityAgent(self.rules)

    def test_analyze_code(self):
        code_with_password = "password = 'mysecretpassword'"
        issues = self.agent.analyze_code(code_with_password)
        self.assertIn('hardcoded_passwords', issues, 'hardcoded_passwords not found in issues')
        self.assertEqual(len(issues['hardcoded_passwords']), 1)

        code_without_issues = "x = 5"
        issues = self.agent.analyze_code(code_without_issues)
        self.assertEqual(issues, {})
        self.assertTrue(self.agent.enforce_rules(code_without_issues), 'Expected enforce_rules to return True for code without issues')
        self.assertFalse(self.agent.enforce_rules(code_with_password), 'Expected enforce_rules to return False for code with issues')

    def test_enforce_rules(self):
        code_with_password = "password = 'mysecretpassword'"
        self.assertFalse(self.agent.enforce_rules(code_with_password, self.rules), 'Expected enforce_rules to return False for code with issues')
        
        code_without_issues = "x = 5"
        self.assertTrue(self.agent.enforce_rules(code_without_issues, self.rules), 'Expected enforce_rules to return True for code without issues')

        rules = initialize_default_rules()
        code_without_issues = "x = 5"
        self.assertTrue(self.agent.enforce_rules(code_without_issues, self.rules), 'Expected enforce_rules to return True for code without issues')
        self.assertIn('check_sql_injection', rules.get_security_rules())

        rules = SecurityRules()
        rules.add_rule('new_rule')
        self.assertIn('new_rule', rules.get_security_rules())

        with self.assertRaises(ValueError):
            rules.add_rule('new_rule')
class TestIDEIntegration(unittest.TestCase):
    def test_get_supported_ides(self):
        supported_ides = get_supported_ides()
        self.assertIsInstance(supported_ides, list)
        self.assertIn('PyCharm', supported_ides)
        self.assertIn('VSCode', supported_ides)
        self.assertIn('SublimeText', supported_ides)

    def test_integrate_with_ide(self):
        for ide in get_supported_ides():
            with self.subTest(ide=ide):
                integrate_with_ide(ide)

        with self.assertRaises(ValueError):
            integrate_with_ide('UnsupportedIDE')

if __name__ == '__main__':
    unittest.main()
