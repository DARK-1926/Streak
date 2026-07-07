from typing import Optional, Tuple
import datetime
import os
import tempfile

class SessionManager:
    """
    Manages coding sessions, allowing for starting, stopping, and checking the status of a session.
    """

    def __init__(self, storage_path: str) -> None:
        self.storage_path = storage_path
        self.session_file = os.path.join(storage_path, 'session_status.txt')
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Ensure that the storage path exists."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

    def start_session(self) -> None:
        """Starts a new coding session by recording the start time."""
        with open(self.session_file, 'w') as f:
            f.write(f"START: {datetime.datetime.now()}")

    def stop_session(self) -> None:
        """Stops the current coding session by appending the end time."""
        try:
            with open(self.session_file, 'a') as f:
                f.write(f"\nEND: {datetime.datetime.now()}")
        except FileNotFoundError:
            raise Exception("No active session to stop.")

    def get_session_status(self) -> Optional[Tuple[datetime.datetime, Optional[datetime.datetime]]]:
        """
        Returns the start and end times of the current or last session.
        If the session is still ongoing, the end time will be None.
        """
        try:
            with open(self.session_file, 'r') as f:
                lines = f.readlines()
                start_time = datetime.datetime.fromisoformat(lines[0].split(': ')[1].strip())
                end_time = None
                if len(lines) > 1:
                    end_time = datetime.datetime.fromisoformat(lines[1].split(': ')[1].strip())
                return (start_time, end_time)
        except FileNotFoundError:
            return None

def create_temp_session_manager() -> SessionManager:
    """
    Creates a temporary session manager using a temporary directory.
    This is useful for testing purposes.
    """
    temp_dir = tempfile.mkdtemp()
    return SessionManager(temp_dir)