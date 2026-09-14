import pytest
from negative_skill_enforcer.enforcer import enforce_negative_skills
from negative_skill_enforcer.spec import load_spec_from_dict


def test_valid_skill_with_correct_exception() -> None:
    """Test that a valid skill raising the correct exception passes enforcement."""
    skill_source = """
def scrape_twitter():
    raise PermissionError()
"""
    spec_dict = {"forbidden_functions": {"scrape_twitter": "PermissionError"}}
    spec = load_spec_from_dict(spec_dict)
    report = enforce_negative_skills(skill_source, spec)
    assert report.missing_functions == []
    assert report.incorrect_exceptions == []


def test_skill_missing_forbidden_function() -> None:
    """Test that a missing forbidden function is reported."""
    skill_source = """
def other_function():
    pass
"""
    spec_dict = {"forbidden_functions": {"scrape_twitter": "PermissionError"}}
    spec = load_spec_from_dict(spec_dict)
    report = enforce_negative_skills(skill_source, spec)
    assert report.missing_functions == ["scrape_twitter"]
    assert report.incorrect_exceptions == []


def test_skill_raises_wrong_exception() -> None:
    """Test that raising an incorrect exception type is reported."""
    skill_source = """
def scrape_twitter():
    raise ValueError("Not allowed")
"""
    spec_dict = {"forbidden_functions": {"scrape_twitter": "PermissionError"}}
    spec = load_spec_from_dict(spec_dict)
    report = enforce_negative_skills(skill_source, spec)
    assert report.missing_functions == []
    assert report.incorrect_exceptions == ["scrape_twitter"]


def test_skill_with_nested_raise() -> None:
    """Test that a raise inside a try/except block is still detected."""
    skill_source = """
def scrape_twitter():
    try:
        pass
    except Exception:
        raise PermissionError
"""
    spec_dict = {"forbidden_functions": {"scrape_twitter": "PermissionError"}}
    spec = load_spec_from_dict(spec_dict)
    report = enforce_negative_skills(skill_source, spec)
    assert report.missing_functions == []
    assert report.incorrect_exceptions == []


def test_invalid_spec_missing_key() -> None:
    """Test that a spec missing 'forbidden_functions' raises ValueError."""
    with pytest.raises(ValueError, match="Input spec must contain 'forbidden_functions' key."):
        load_spec_from_dict({})


def test_invalid_spec_dotted_exception_name() -> None:
    """Test that a dotted exception name raises ValueError."""
    spec_dict = {"forbidden_functions": {"scrape_twitter": "exceptions.PermissionError"}}
    with pytest.raises(ValueError, match="must be a valid Python identifier without dots"):
        load_spec_from_dict(spec_dict)


def test_invalid_python_source_raises_value_error() -> None:
    """Test that invalid Python source code raises ValueError."""
    skill_source = "def invalid_syntax("
    spec_dict = {"forbidden_functions": {"scrape_twitter": "PermissionError"}}
    spec = load_spec_from_dict(spec_dict)
    with pytest.raises(ValueError, match="Syntax error in source code"):
        enforce_negative_skills(skill_source, spec)