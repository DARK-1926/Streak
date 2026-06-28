from typing import Dict, Optional

class FeedbackSystem:
    """
    The FeedbackSystem class is responsible for providing feedback to the user based on their responses to challenges.
    It includes methods to evaluate the response and generate a feedback message.
    """

    def __init__(self) -> None:
        """
        Initialize the FeedbackSystem with an empty dictionary to store feedback messages.
        """
        self.feedback_messages: Dict[str, str] = {
            'correct': "Great job! Your answer is correct.",
            'incorrect': "Oops! That's not quite right. Keep trying!",
            'hint': "Here's a hint: {}"
        }

    def provide_feedback(self, is_correct: bool, hint: Optional[str] = None) -> str:
        """
        Provide feedback based on whether the user's response was correct or not.

        :param is_correct: A boolean indicating whether the user's response was correct.
        :param hint: An optional string containing a hint to help the user.
        :return: A feedback message.
        """
        if is_correct:
            return self.feedback_messages['correct']
        else:
            if hint:
                return self.feedback_messages['hint'].format(hint)
            return self.feedback_messages['incorrect']

    def add_feedback_message(self, key: str, message: str) -> None:
        """
        Add or update a feedback message in the feedback system.

        :param key: The key for the feedback message.
        :param message: The new feedback message.
        """
        self.feedback_messages[key] = message

    def get_feedback_message(self, key: str) -> Optional[str]:
        """
        Retrieve a specific feedback message by its key.

        :param key: The key for the feedback message.
        :return: The feedback message if it exists, otherwise None.
        """
        return self.feedback_messages.get(key)