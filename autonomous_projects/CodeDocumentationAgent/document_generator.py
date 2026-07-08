import ast
import os

def parse_code(code: str) -> dict:
    tree = ast.parse(code)
    functions = []
    classes = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Only add functions that are not methods (not defined inside a class)
            if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if hasattr(parent, 'body') and node in parent.body):
                functions.append(node)
        elif isinstance(node, ast.ClassDef):
            classes.append(node)
    
    return {
        'functions': functions,
        'classes': classes
    }
    


def generate_documentation(source_or_code: str) -> str:
    if source_or_code.strip().endswith('.py') and os.path.exists(source_or_code):
        with open(source_or_code, 'r') as f:
            code = f.read()
    else:
        code = source_or_code
    
    parsed_code = parse_code(code)
    documentation = []
    
    for cls in parsed_code['classes']:
        documentation.append(generate_documentation_for_class(cls))
    
    for func in parsed_code['functions']:
        documentation.append(generate_documentation_for_function(func))
    
    return '\n'.join(documentation)


def generate_documentation_for_function(func_node: ast.FunctionDef) -> str:
    args = [arg.arg for arg in func_node.args.args]
    args_str = ', '.join(args)
    doc = f"### {func_node.name}({args_str})\n"
    doc += "No description provided.\n"
    return doc


def generate_documentation_for_class(class_node: ast.ClassDef) -> str:
    doc = f"## {class_node.name}\n"
    doc += "No description provided.\n\n"
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef):
            doc += generate_documentation_for_function(item)
    return doc
