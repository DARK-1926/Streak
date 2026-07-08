import ast
import os
import tempfile
from typing import Dict, List
import tempfile
from typing import Dict, List

from document_generator import parse_code, generate_documentation_for_function, generate_documentation_for_class, generate_documentation
from document_updater import read_file, write_file, get_documentation_map, update_documentation
from document_validator import validate_documentation

def test_parse_code():
    code = """
def example_function(arg1, arg2):
    pass

class ExampleClass:
    def method(self):
        pass
"""
    parsed_code = parse_code(code)
    assert 'functions' in parsed_code and 'classes' in parsed_code
    assert len(parsed_code['functions']) == 1
    assert len(parsed_code['classes']) == 1

def test_generate_documentation_for_function():
    func_node = ast.FunctionDef(name='example_function', args=ast.arguments(args=[ast.arg(arg='arg1'), ast.arg(arg='arg2')], posonlyargs=[], kwonlyargs=[], kw_defaults=[], defaults=[]), body=[], decorator_list=[])
    doc = generate_documentation_for_function(func_node)
    assert "### example_function(arg1, arg2)" in doc
    assert "No description provided." in doc

def test_generate_documentation_for_class():
    class_node = ast.ClassDef(name='ExampleClass', bases=[], body=[ast.FunctionDef(name='method', args=ast.arguments(args=[ast.arg(arg='self')], posonlyargs=[], kwonlyargs=[], kw_defaults=[], defaults=[]), body=[], decorator_list=[])], decorator_list=[])
    doc = generate_documentation_for_class(class_node)
    assert "## ExampleClass" in doc
    assert "### method(self)" in doc

def test_generate_documentation_from_string():
    code = """
def example_function(arg1, arg2):
    pass

class ExampleClass:
    def method(self):
        pass
"""
    doc = generate_documentation(code)
    assert "### example_function(arg1, arg2)" in doc
    assert "## ExampleClass" in doc
    assert "### method(self)" in doc

def test_generate_documentation_from_file():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as tmpfile:
        tmpfile.write('def example_function(arg1, arg2):\n    pass\nclass ExampleClass:\n    def method(self):\n        pass\n')
        tmpfile.flush()
        tmpfile_path = tmpfile.name  # Capture name before closing
    try:
        doc = generate_documentation(tmpfile_path)
        assert "## ExampleClass" in doc
        assert "### method(self)" in doc
    finally:
        os.remove(tmpfile_path)

def test_read_file():
    content = "test content"
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmpfile:
        tmpfile.write(content)
        tmpfile_path = tmpfile.name
    try:
        read_content = read_file(tmpfile_path)
        assert read_content == content
    finally:
        os.remove(tmpfile_path)

def test_write_file():
    content = "test content"
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmpfile:
        tmpfile_path = tmpfile.name
    try:
        write_file(tmpfile_path, content)
        with open(tmpfile_path, 'r') as file:
            written_content = file.read()
        assert written_content == content
    finally:
        os.remove(tmpfile_path)

def test_get_documentation_map():
    documentation = """
## ExampleClass
No description provided.

### method(self)
No description provided.

### example_function(arg1, arg2)
No description provided.
"""
    doc_map = get_documentation_map(documentation)
    assert 'ExampleClass' in doc_map
    assert 'method' in doc_map
    assert 'example_function' in doc_map

def test_update_documentation():
    old_doc = """
## ExampleClass
No description provided.

### method(self)
No description provided.
"""
    new_codebase = """
def example_function(arg1, arg2):
    pass

class ExampleClass:
    def method(self):
        pass
"""
    updated_doc = update_documentation(old_doc, new_codebase)
    assert "### example_function(arg1, arg2)" in updated_doc
    assert "## ExampleClass" in updated_doc
    assert "### method(self)" in updated_doc

def test_validate_documentation():
    valid_doc = """
## ExampleClass
Description for ExampleClass.

### method(self)
Description for method.
"""
    invalid_doc = """
## ExampleClass
No description provided.

### method(self)
No description provided.
"""
    assert validate_documentation(valid_doc) == True
    assert validate_documentation(invalid_doc) == False

if __name__ == "__main__":
    test_parse_code()
    test_generate_documentation_for_function()
    test_generate_documentation_for_class()
    test_generate_documentation_from_string()
    test_generate_documentation_from_file()
    test_read_file()
    test_write_file()
    test_get_documentation_map()
    test_update_documentation()
    test_validate_documentation()
