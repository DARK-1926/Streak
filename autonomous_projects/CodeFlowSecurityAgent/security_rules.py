from typing import List

class SecurityRules:
    def __init__(self):
        self.rules: List[str] = []

    def get_security_rules(self) -> List[str]:
        """
        Returns the list of predefined security rules.
        """
        return self.rules

    def add_rule(self, rule: str) -> None:
        """
        Adds a new rule to the list of security rules.
        """
        if rule not in self.rules:
            self.rules.append(rule)
        else:
            raise ValueError(f"Rule '{rule}' already exists.")

# Predefined security rules
DEFAULT_RULES = [
    "check_hardcoded_passwords",
    "check_sql_injection"
]

def initialize_default_rules() -> SecurityRules:
    """
    Initializes and returns a SecurityRules instance with default rules.
    """
    security_rules = SecurityRules()
    for rule in DEFAULT_RULES:
        security_rules.add_rule(rule)
    return security_rules