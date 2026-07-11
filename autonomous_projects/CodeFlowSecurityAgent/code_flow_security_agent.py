import re
from typing import List, Tuple
import ast

class CodeFlowSecurityAgent:
    def __init__(self, rules):
        self.rules = rules
    def analyze_code(self, code):
        issues = {}
        
        # Check for hardcoded passwords
        password_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'pwd\s*=\s*["\'][^"\']+["\']',
            r'pass\s*=\s*["\'][^"\']+["\']'
        ]
        
        for pattern in password_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                if 'hardcoded_passwords' not in issues:
                    issues['hardcoded_passwords'] = []
                issues['hardcoded_passwords'].extend(matches)
        
        # Apply other security rules if available
        if hasattr(self.rules, 'get_security_rules'):
            for rule_name in self.rules.get_security_rules():
                # Apply rule-specific checks here
                pass
        
        return issues
    
    def enforce_rules(self, code, rules=None):
        if rules is None:
            rules = self.rules
        issues = self.analyze_code(code)
        return len(issues) == 0

    def check_sql_injection(self, tree: ast.AST) -> List[Tuple[int, int, str]]:
        """
        Checks for potential SQL injection vulnerabilities.
        """
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'execute':
                    for arg in node.args:
                        if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod):
                            issues.append((node.lineno, node.col_offset, "Potential SQL injection vulnerability detected"))
        return issues
