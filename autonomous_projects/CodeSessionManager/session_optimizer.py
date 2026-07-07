import os
import tempfile
from typing import List, Tuple, Optional
from datetime import datetime, timedelta

class SessionOptimizer:
    """
    Provides functionality to optimize a coding session based on given parameters.
    The optimization is agnostic to specific session configurations and aims to
    enhance the developer's productivity by suggesting optimal session times.
    """

    def __init__(self, session_manager: 'SessionManager', session_tracker: 'SessionTracker') -> None:
        self.session_manager = session_manager
        self.session_tracker = session_tracker

    def suggest_optimal_session_time(self, preferred_duration: int) -> Tuple[datetime, datetime]:
        """
        Suggests an optimal start and end time for a coding session based on the preferred duration.

        :param preferred_duration: The preferred duration of the session in minutes.
        :return: A tuple containing the suggested start and end times.
        """
        now = datetime.now()
        suggested_start = now + timedelta(minutes=5)
        suggested_end = suggested_start + timedelta(minutes=preferred_duration)
        return (suggested_start, suggested_end)

    def get_average_session_duration(self) -> Optional[timedelta]:
        """
        Calculates the average duration of past sessions.

        :return: The average duration as a timedelta or None if no sessions are recorded.
        """
        session_status = self.session_manager.get_session_status()
        if not session_status:
            return None

        total_duration = timedelta()
        session_count = 0
        if session_status:
            start_time, end_time = session_status
            if end_time:
                total_duration += (end_time - start_time)
                session_count += 1

        if session_count == 0:
            return None
        return total_duration / session_count

    def log_optimization_suggestion(self, suggestion: Tuple[datetime, datetime]) -> None:
        """
        Logs the optimization suggestion to the activity log.

        :param suggestion: A tuple containing the suggested start and end times.
        """
        start_time, end_time = suggestion
        self.session_tracker.log_activity(f"Optimized session suggested from {start_time} to {end_time}")

def create_temp_session_optimizer() -> SessionOptimizer:
    """
    Creates a temporary session optimizer using a temporary directory for both
    session manager and session tracker.

    :return: An instance of SessionOptimizer.
    """
    temp_dir = tempfile.mkdtemp()
    session_manager = SessionManager(temp_dir)
    session_tracker = SessionTracker(temp_dir)
    return SessionOptimizer(session_manager, session_tracker)