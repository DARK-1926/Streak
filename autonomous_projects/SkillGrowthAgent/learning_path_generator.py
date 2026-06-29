import os
from typing import Dict, List

def generate_learning_path(recommended_resources: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
    """
    Generates a personalized learning path based on the recommended resources.
    
    :param recommended_resources: A dictionary where keys are categories and values are lists of recommended resources.
    :return: A dictionary where keys are categories and values are lists of structured learning paths.
    """
    learning_path = {}
    for category, resources in recommended_resources.items():
        # Sort resources by type (prioritizing books over websites)
        sorted_resources = sorted(resources, key=lambda x: 0 if x['type'] == 'book' else 1)
        # Create a structured learning path
        structured_path = []
        for index, resource in enumerate(sorted_resources, start=1):
            structured_path.append({
                "step": index,
                "title": resource["title"],
                "type": resource["type"],
                "url": resource["url"]
            })
        learning_path[category] = structured_path
    return learning_path

def save_learning_path(learning_path: Dict[str, List[Dict]], file_path: str) -> None:
    """
    Saves the generated learning path to a JSON file.
    
    :param learning_path: The structured learning path.
    :param file_path: The path to the output file.
    """
    import json
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(learning_path, file, indent=4)

def load_learning_path(file_path: str) -> Dict[str, List[Dict]]:
    """
    Loads the learning path from a JSON file.
    
    :param file_path: The path to the input file.
    :return: The structured learning path.
    """
    import json
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Example usage
if __name__ == "__main__":
    # Example recommended resources
    example_resources = {
        "Python": [
            {"title": "Automate the Boring Stuff with Python", "type": "book", "url": "https://automatetheboringstuff.com/"},
            {"title": "Real Python", "type": "website", "url": "https://realpython.com/"},
        ],
        "Data Structures": [
            {"title": "Introduction to Algorithms", "type": "book", "url": "https://mitpress.mit.edu/books/introduction-algorithms-third-edition"},
            {"title": "GeeksforGeeks Data Structures", "type": "website", "url": "https://www.geeksforgeeks.org/data-structures/"},
        ]
    }
    
    # Generate learning path
    path = generate_learning_path(example_resources)
    
    # Save to a file
    output_file = "learning_path.json"
    save_learning_path(path, output_file)
    
    # Load from a file
    loaded_path = load_learning_path(output_file)
    print(loaded_path)