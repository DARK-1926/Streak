import json
from typing import Dict, Any
import os

def flag_content(content_id: str, is_ai_generated: bool, db_path: str = 'content_flags.json') -> None:
    """
    Flags a piece of content as AI-generated or not in a simulated database (JSON file).
    
    :param content_id: The unique identifier for the content.
    :param is_ai_generated: Boolean indicating whether the content is AI-generated.
    :param db_path: Path to the JSON file acting as the database. Defaults to 'content_flags.json'.
    """
    try:
        # Load existing flags from the database
        if os.path.exists(db_path):
            with open(db_path, 'r') as db_file:
                content_flags = json.load(db_file)
        else:
            content_flags = {}

        # Update the flag status for the given content ID
        content_flags[content_id] = is_ai_generated

        # Save the updated flags back to the database
        with open(db_path, 'w') as db_file:
            json.dump(content_flags, db_file, indent=4)

    except Exception as e:
        print(f"An error occurred while flagging content: {e}")

# Example usage
if __name__ == "__main__":
    flag_content('12345', True)  # Flag content with ID '12345' as AI-generated
    flag_content('67890', False)  # Flag content with ID '67890' as not AI-generated