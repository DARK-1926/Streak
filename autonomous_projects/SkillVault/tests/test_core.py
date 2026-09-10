import unittest
import tempfile
import os
from typing import Dict, Any
from skillvault.core import load_skill_from_source, compute_skill_hash, simulate_skill


class TestCore(unittest.TestCase):
    def test_load_skill_from_source_valid(self) -> None:
        source_code = 'def greet(name: str) -> str:\n    return f"Hi {name}"'
        skill_spec = load_skill_from_source(source_code)
        self.assertEqual(skill_spec.name, "greet")
        self.assertEqual(skill_spec.inputs, {"name": "str"})
        self.assertEqual(skill_spec.outputs, "str")
        self.assertEqual(skill_spec.source_code, source_code)

    def test_load_skill_from_source_invalid_multiple_functions(self) -> None:
        source_code = (
            "def func1(): pass\n"
            "def func2(): pass"
        )
        with self.assertRaises(ValueError) as context:
            load_skill_from_source(source_code)
        self.assertIn("exactly one function", str(context.exception))

    def test_compute_skill_hash_deterministic(self) -> None:
        source_code = 'def add(a: int, b: int) -> int:\n    return a + b'
        skill_spec = load_skill_from_source(source_code)
        hash1 = compute_skill_hash(skill_spec)
        hash2 = compute_skill_hash(skill_spec)
        self.assertEqual(hash1, hash2)

    def test_simulate_skill_correct_execution(self) -> None:
        source_code = 'def greet(name: str) -> str:\n    return f"Hi {name}"'
        skill_spec = load_skill_from_source(source_code)
        input_dict: Dict[str, Any] = {"name": "Alice"}
        result = simulate_skill(skill_spec, input_dict)
        self.assertEqual(result, {"output": "Hi Alice"})

    def test_simulate_skill_invalid_input_type(self) -> None:
        source_code = 'def add(a: int, b: int) -> int:\n    return a + b'
        skill_spec = load_skill_from_source(source_code)
        input_dict: Dict[str, Any] = {"a": "not_an_int", "b": 5}
        with self.assertRaises(TypeError):
            simulate_skill(skill_spec, input_dict)

    def test_load_skill_from_source_no_function(self) -> None:
        source_code = "x = 5\nprint(x)"
        with self.assertRaises(ValueError) as context:
            load_skill_from_source(source_code)
        self.assertIn("exactly one function", str(context.exception))