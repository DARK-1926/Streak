import pytest
import yaml
import os

def test_policy_template_exists():
    """Test that policy template file exists."""
    assert os.path.exists("governance/ai_adoption_policy_template.yaml")

def test_policy_template_valid_yaml():
    """Test that policy template is valid YAML."""
    with open("governance/ai_adoption_policy_template.yaml", "r") as f:
        policy = yaml.safe_load(f)
    assert "ai_adoption_policy" in policy
    assert "principles" in policy["ai_adoption_policy"]

def test_policy_has_required_principles():
    """Test that policy includes required principles."""
    with open("governance/ai_adoption_policy_template.yaml", "r") as f:
        policy = yaml.safe_load(f)
    principles = policy["ai_adoption_policy"]["principles"]
    principle_names = [p["name"] for p in principles]
    
    required_principles = ["Human Oversight", "Data Privacy", "Transparency", "Fairness"]
    for principle in required_principles:
        assert principle in principle_names
