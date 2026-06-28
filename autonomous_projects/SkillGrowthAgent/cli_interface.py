from typing import Callable, Dict

class CLIInterface:
    """
    The CLIInterface class is responsible for handling the command-line interface interactions.
    It provides methods to display the main menu and handle user input.
    """

    def __init__(self, skill_manager: 'SkillManager', challenge_generator: 'ChallengeGenerator', feedback_system: 'FeedbackSystem', scoring_system: 'ScoringSystem') -> None:
        """
        Initialize the CLIInterface with instances of SkillManager, ChallengeGenerator, FeedbackSystem, and ScoringSystem.

        :param skill_manager: An instance of SkillManager to manage skills and their levels.
        :param challenge_generator: An instance of ChallengeGenerator to generate challenges.
        :param feedback_system: An instance of FeedbackSystem to provide feedback.
        :param scoring_system: An instance of ScoringSystem to manage the user's score and rank.
        """
        self.skill_manager = skill_manager
        self.challenge_generator = challenge_generator
        self.feedback_system = feedback_system
        self.scoring_system = scoring_system
        self.menu_options: Dict[str, Callable[[], None]] = {
            '1': self.list_skills,
            '2': self.add_skill,
            '3': self.generate_challenge,
            '4': self.show_score,
            '5': self.exit
        }

    def display_menu(self) -> None:
        """
        Display the main menu options to the user.
        """
        print("\nWelcome to SkillGrowthAgent CLI")
        print("1. List all skills")
        print("2. Add a new skill")
        print("3. Generate a challenge")
        print("4. Show current score")
        print("5. Exit")

    def handle_input(self) -> None:
        """
        Handle user input and route it to the appropriate function.
        """
        while True:
            self.display_menu()
            choice = input("Enter your choice: ")
            if choice in self.menu_options:
                try:
                    self.menu_options[choice]()
                except Exception as e:
                    print(f"An error occurred: {e}")
            else:
                print("Invalid choice. Please try again.")

    def list_skills(self) -> None:
        """
        List all skills and their levels.
        """
        skills = self.skill_manager.list_skills()
        if skills:
            for skill, level in skills.items():
                print(f"{skill}: Level {level}")
        else:
            print("No skills available.")

    def add_skill(self) -> None:
        """
        Add a new skill or update an existing one.
        """
        skill_name = input("Enter the skill name: ")
        try:
            level = int(input("Enter the skill level (positive integer): "))
            self.skill_manager.add_skill(skill_name, level)
            print(f"Skill '{skill_name}' added/updated successfully.")
        except ValueError as e:
            print(f"Error: {e}")

    def generate_challenge(self) -> None:
        """
        Generate a challenge for a specific skill.
        """
        skill_name = input("Enter the skill name for the challenge: ")
        challenge = self.challenge_generator.generate_challenge(skill_name)
        if challenge:
            print(f"Challenge for {challenge['skill_name']}: {challenge['challenge']}")
        else:
            print(f"No challenge available for skill: {skill_name}")

    def show_score(self) -> None:
        """
        Show the user's current score.
        """
        score = self.scoring_system.get_score()
        print(f"Your current score: {score}")

    def exit(self) -> None:
        """
        Exit the application.
        """
        print("Exiting SkillGrowthAgent CLI. Goodbye!")
        raise SystemExit