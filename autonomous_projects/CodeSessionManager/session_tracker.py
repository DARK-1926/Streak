import os
import datetime
from typing import List, Optional
import tempfile  # Added import for tempfile
import datetime
from typing import List, Optional

class SessionTracker:
    """
    Tracks and logs activities during a coding session. This includes logging and retrieving session activities.
    """

    def __init__(self, session_path: str) -> None:
        self.session_path = session_path
        self.activity_log_file = os.path.join(session_path, 'activity_log.txt')
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Ensure that the storage path exists."""
        if not os.path.exists(self.session_path):
            os.makedirs(self.session_path)

    def log_activity(self, activity: str) -> None:
        """
        Logs an activity with a timestamp to the activity log file.

        :param activity: The activity description to log.
        """
        try:
            with open(self.activity_log_file, 'a') as f:
                f.write(f"{datetime.datetime.now()}: {activity}\n")
        except Exception as e:
            print(f"Failed to log activity: {e}")

    def get_activities(self) -> Optional[List[str]]:
        """
        Retrieves all logged activities from the activity log file.

        :return: A list of logged activities or None if the file does not exist.
        """
        try:
            with open(self.activity_log_file, 'r') as f:
                return [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            return None

def create_temp_session_tracker() -> SessionTracker:
    """
    Creates a temporary session tracker using a temporary directory.

    :return: An instance of SessionTracker.
    """
    temp_dir = tempfile.mkdtemp()
    return SessionTracker(temp_dir)
