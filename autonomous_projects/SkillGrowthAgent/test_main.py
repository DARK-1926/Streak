import unittest
from skill_manager import SkillManager
from challenge_generator import ChallengeGenerator
from feedback_system import FeedbackSystem
from scoring_system import ScoringSystem
from cli_interface import CLIInterface

class TestSkillGrowthAgent(unittest.TestCase):

    def setUp(self):
        self.skill_manager = SkillManager()
        self.challenge_generator = ChallengeGenerator(self.skill_manager)
        self.feedback_system = FeedbackSystem()
        self.scoring_system = ScoringSystem()
        self.cli_interface = CLIInterface(self.skill_manager, self.challenge_generator, self.feedback_system, self.scoring_system)

    def test_skill_manager_initialization(self):
        self.assertIsNotNone(self.skill_manager)

    def test_challenge_generator_initialization(self):
        self.assertIsNotNone(self.challenge_generator)

    def test_feedback_system_initialization(self):
        self.assertIsNotNone(self.feedback_system)

    def test_scoring_system_initialization(self):
        self.assertIsNotNone(self.scoring_system)

    def test_cli_interface_initialization(self):
        self.assertIsNotNone(self.cli_interface)

    def test_skill_manager_add_skill(self):
        self.skill_manager.add_skill("Python", 1)
        self.assertIn("Python", self.skill_manager.skills)

    def test_challenge_generator_generate_challenge(self):
        self.skill_manager.add_skill("coding", 1)
        self.skill_manager.add_skill("coding", 1)
        challenge = self.challenge_generator.generate_challenge("coding")
        feedback = self.feedback_system.provide_feedback("Python", 1)
        self.assertIsNotNone(feedback)

    def test_scoring_system_calculate_score(self):
        # Check if the scoring system has a method to calculate scores
        self.assertTrue(hasattr(self.scoring_system, 'calculate_score'),
                       "ScoringSystem does not have calculate_score method")
        try:
            score = self.scoring_system.calculate_score("Python", 1, "Sample solution")
            self.assertIsNotNone(score)
        except Exception as e:
            self.fail(f"Error calling calculate_score: {e}")

    def test_integration_skill_manager_and_challenge_generator(self):
        self.skill_manager.add_skill("coding", 1)
        self.skill_manager.add_skill("coding", 1)
        challenge = self.challenge_generator.generate_challenge("coding")
        self.assertIsNotNone(challenge)
        feedback = self.feedback_system.provide_feedback("Python", 1)
        self.assertIsNotNone(feedback)
        self.skill_manager.add_skill("Python", 1)
        feedback = self.feedback_system.provide_feedback("Python", 1)
        self.assertIsNotNone(feedback)
    def test_integration_skill_manager_and_scoring_system(self):
        self.skill_manager.add_skill("Python", 1)
        score = self.scoring_system.calculate_score("Python", 1, "Sample solution")
        self.assertIsNotNone(score)

if __name__ == '__main__':
    unittest.main()
