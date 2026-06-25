import json

def transform_json_to_markdown(data: dict) -> str:
    """
    Transforms a JSON object into a markdown string.
    
    :param data: A dictionary representing the JSON object.
    :return: A string formatted in markdown.
    """
    try:
        markdown_lines = []
        for key, value in data.items():
            if isinstance(value, list):
                markdown_lines.append(f"### {key}\n")
                for item in value:
                    markdown_lines.append(f"- {item}\n")
            elif isinstance(value, dict):
                markdown_lines.append(f"### {key}\n")
                for sub_key, sub_value in value.items():
                    markdown_lines.append(f"**{sub_key}**: {sub_value}\n")
            else:
                markdown_lines.append(f"**{key}**: {value}\n")
        return ''.join(markdown_lines)
    except Exception as e:
        raise ValueError(f"Error transforming JSON to Markdown: {e}")

def decorate_prompt(prompt: str, decorations: dict) -> str:
    """
    Decorates a prompt string with additional information provided in the decorations dictionary.
    
    :param prompt: The original prompt string.
    :param decorations: A dictionary containing key-value pairs to be added to the prompt.
    :return: A decorated prompt string.
    """
    try:
        decoration_lines = [f"{key}: {value}" for key, value in decorations.items()]
        decoration_text = "\n".join(decoration_lines)
        return f"{decoration_text}\n\n{prompt}"
    except Exception as e:
        raise ValueError(f"Error decorating prompt: {e}")