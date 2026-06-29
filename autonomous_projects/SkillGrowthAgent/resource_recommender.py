import os
from typing import Dict, List

RESOURCE_DATABASE = {
    "Python": [
        {"title": "Automate the Boring Stuff with Python", "type": "book", "url": "https://automatetheboringstuff.com/"},
        {"title": "Python Crash Course", "type": "book", "url": "https://nostarch.com/python-crash-course-3rd-edition"},
        {"title": "Real Python", "type": "website", "url": "https://realpython.com/"},
    ],
    "Data Structures": [
        {"title": "Introduction to Algorithms", "type": "book", "url": "https://mitpress.mit.edu/books/introduction-algorithms-third-edition"},
        {"title": "GeeksforGeeks Data Structures", "type": "website", "url": "https://www.geeksforgeeks.org/data-structures/"},
    ],
    "Web Development": [
        {"title": "Django for Beginners", "type": "book", "url": "https://djangoforbeginners.com/"},
        {"title": "Flask Web Development", "type": "book", "url": "https://flask.palletsprojects.com/en/2.0.x/"},
        {"title": "MDN Web Docs", "type": "website", "url": "https://developer.mozilla.org/en-US/docs/Web"},
    ]
}

def recommend_resources(skill_gaps: Dict[str, List[str]]) -> Dict[str, List[Dict]]:
    """
    Recommends learning resources based on the identified skill gaps.
    
    :param skill_gaps: A dictionary where keys are categories and values are lists of missing skills.
    :return: A dictionary where keys are categories and values are lists of recommended resources.
    """
    recommendations = {}
    for category, missing_skills in skill_gaps.items():
        if category in RESOURCE_DATABASE:
            category_resources = [resource for resource in RESOURCE_DATABASE[category] if any(skill in resource["title"] for skill in missing_skills)]
            if category_resources:
                recommendations[category] = category_resources
    return recommendations

def load_resource_database(file_path: str) -> Dict[str, List[Dict]]:
    """
    Loads the resource database from a JSON file.
    
    :param file_path: The path to the JSON file containing the resource database.
    :return: A dictionary representing the resource database.
    """
    import json
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Failed to load resource database: {e}")
        return {}

def save_resource_database(file_path: str, resource_db: Dict[str, List[Dict]]) -> None:
    """
    Saves the resource database to a JSON file.
    
    :param file_path: The path to the JSON file where the resource database will be saved.
    :param resource_db: The resource database to be saved.
    """
    import json
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(resource_db, file, indent=4)
    except IOError as e:
        print(f"Failed to save resource database: {e}")

# Example usage
if __name__ == "__main__":
    # Load the resource database from a file
    resource_db = load_resource_database("resources.json")
    if not resource_db:
        resource_db = RESOURCE_DATABASE

    # Simulate skill gaps
    skill_gaps = {
        "Python": ["advanced topics"],
        "Web Development": ["Django"]
    }

    # Get recommendations
    recommendations = recommend_resources(skill_gaps)
    print(recommendations)

    # Save the updated resource database
    save_resource_database("resources.json", resource_db)