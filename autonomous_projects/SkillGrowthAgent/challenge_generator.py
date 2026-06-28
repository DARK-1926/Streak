from typing import Dict, Optional, Callable
import random

class ChallengeGenerator:
    """
    The ChallengeGenerator class is responsible for generating and validating challenges based on the user's skill level and type.
    It provides methods to create a new challenge and validate the user's response.
    """

    def __init__(self, skill_manager: 'SkillManager') -> None:
        """
        Initialize the ChallengeGenerator with a SkillManager instance.

        :param skill_manager: An instance of SkillManager to manage skills and their levels.
        """
        self.skill_manager = skill_manager
        self.challenges: Dict[str, Callable[[int], str]] = {
            'math': self._generate_math_challenge,
            'coding': self._generate_coding_challenge,
            'vocabulary': self._generate_vocabulary_challenge
        }

    def generate_challenge(self, skill_name: str) -> Optional[Dict[str, any]]:
        """
        Generate a challenge based on the user's skill level and type.

        :param skill_name: The name of the skill for which to generate a challenge.
        :return: A dictionary containing the challenge details if the skill exists, otherwise None.
        """
        skill_level = self.skill_manager.get_skill_level(skill_name)
        if skill_level is None:
            return None

        challenge_func = self.challenges.get(skill_name)
        if challenge_func is None:
            raise ValueError(f"Unsupported skill type: {skill_name}")

        challenge = challenge_func(skill_level)
        return {'skill_name': skill_name, 'challenge': challenge}

    def _generate_math_challenge(self, level: int) -> str:
        """
        Generate a math challenge based on the user's skill level.

        :param level: The level of the skill.
        :return: A string representing the math challenge.
        """
        num1 = random.randint(1, 10 * level)
        num2 = random.randint(1, 10 * level)
        operation = random.choice(['+', '-', '*'])
        return f"What is {num1} {operation} {num2}?"

    def _generate_coding_challenge(self, level: int) -> str:
        """
        Generate a coding challenge based on the user's skill level.

        :param level: The level of the skill.
        :return: A string representing the coding challenge.
        """
        # This is a placeholder. In a real application, this would be more complex.
        return f"Write a function that returns the sum of two numbers (Level {level})"

    def _generate_vocabulary_challenge(self, level: int) -> str:
        """
        Generate a vocabulary challenge based on the user's skill level.

        :param level: The level of the skill.
        :return: A string representing the vocabulary challenge.
        """
        # This is a placeholder. In a real application, this would be more complex.
        return f"Define the word 'ubiquitous' (Level {level})"

    def validate_response(self, skill_name: str, challenge: str, response: str) -> bool:
        """
        Validate the user's response to a challenge.

        :param skill_name: The name of the skill.
        :param challenge: The challenge string.
        :param response: The user's response.
        :return: A boolean indicating if the user's response was correct.
        """
        if skill_name == 'math':
            try:
                expected_result = eval(challenge.split('What is ')[1].replace('?', ''))
                return str(expected_result) == response
            except Exception as e:
                print(f"Error in math validation: {e}")
                return False
        elif skill_name == 'coding':
            # Placeholder for actual coding challenge validation
            return True
        elif skill_name == 'vocabulary':
            # Placeholder for actual vocabulary challenge validation
            return True
        else:
            raise ValueError(f"Unsupported skill type: {skill_name}")