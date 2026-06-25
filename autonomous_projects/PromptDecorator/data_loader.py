import json
from typing import Dict

def load_json_data(file_path: str) -> Dict:
    """
    Loads JSON data from a file and returns it as a dictionary.
    
    :param file_path: The path to the JSON file.
    :return: A dictionary containing the JSON data.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise ValueError(f"The file at {file_path} was not found.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON from {file_path}: {e}")
    except Exception as e:
        raise ValueError(f"An error occurred while loading JSON from {file_path}: {e}")