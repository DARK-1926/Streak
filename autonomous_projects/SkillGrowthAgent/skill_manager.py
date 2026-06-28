from typing import Dict, Optional

class SkillManager:
    """
    The SkillManager class is responsible for managing skills and their levels.
    It provides methods to add new skills and retrieve existing ones.
    """

    def __init__(self) -> None:
        """
        Initialize the SkillManager with an empty dictionary to store skills.
        """
        self.skills: Dict[str, int] = {}

    def add_skill(self, skill_name: str, level: int) -> None:
        """
        Add a new skill or update the level of an existing skill.

        :param skill_name: The name of the skill to add or update.
        :param level: The level of the skill.
        :raises ValueError: If the level is not a positive integer.
        """
        if level <= 0:
            raise ValueError("Skill level must be a positive integer.")
        self.skills[skill_name] = level

    def get_skill_level(self, skill_name: str) -> Optional[int]:
        """
        Retrieve the level of a specific skill.

        :param skill_name: The name of the skill to retrieve.
        :return: The level of the skill if it exists, otherwise None.
        """
        return self.skills.get(skill_name)

    def remove_skill(self, skill_name: str) -> None:
        """
        Remove a skill from the manager.

        :param skill_name: The name of the skill to remove.
        """
        if skill_name in self.skills:
            del self.skills[skill_name]

    def list_skills(self) -> Dict[str, int]:
        """
        List all skills and their levels.

        :return: A dictionary of all skills and their levels.
        """
        return self.skills