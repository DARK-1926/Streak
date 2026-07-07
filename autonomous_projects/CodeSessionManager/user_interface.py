import os
import datetime
from typing import Optional, Tuple
from session_manager import SessionManager
from session_tracker import SessionTracker
from session_optimizer import SessionOptimizer

def display_session_status(session_manager: SessionManager) -> None:
    """
    Displays the current or last session status to the user.

    :param session_manager: An instance of SessionManager.
    """
    try:
        session_status = session_manager.get_session_status()
        if session_status:
            start_time, end_time = session_status
            print(f"Session Start Time: {start_time}")
            if end_time:
                print(f"Session End Time: {end_time}")
                duration = end_time - start_time
                print(f"Session Duration: {duration}")
            else:
                print("Session is still ongoing.")
        else:
            print("No session data available.")
    except Exception as e:
        print(f"Failed to get session status: {e}")

def collect_session_configuration() -> Tuple[Optional[int], Optional[str]]:
    """
    Collects session configuration from the user including preferred session duration and activity description.

    :return: A tuple containing the preferred session duration in minutes and the activity description.
    """
    try:
        preferred_duration = int(input("Enter your preferred session duration (in minutes): "))
        activity_description = input("Enter a brief description of the activity: ")
        return (preferred_duration, activity_description)
    except ValueError:
        print("Invalid input. Please enter a valid number for the session duration.")
        return (None, None)

def main() -> None:
    """
    Main function to run the user interface. It initializes the session manager, tracker, and optimizer,
    and provides options to start, stop, and check the status of a coding session.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        session_manager = SessionManager(temp_dir)
        session_tracker = SessionTracker(temp_dir)
        session_optimizer = SessionOptimizer(session_manager, session_tracker)

        while True:
            print("\n--- CodeSessionManager ---")
            print("1. Start a new session")
            print("2. Stop the current session")
            print("3. Check session status")
            print("4. Suggest optimal session time")
            print("5. Exit")

            choice = input("Choose an option: ")

            if choice == '1':
                preferred_duration, activity_description = collect_session_configuration()
                if preferred_duration is not None and activity_description:
                    session_manager.start_session()
                    session_tracker.log_activity(activity_description)
                    suggested_times = session_optimizer.suggest_optimal_session_time(preferred_duration)
                    print(f"Suggested Start Time: {suggested_times[0]}")
                    print(f"Suggested End Time: {suggested_times[1]}")
                else:
                    print("Session not started due to invalid input.")

            elif choice == '2':
                session_manager.stop_session()

            elif choice == '3':
                display_session_status(session_manager)

            elif choice == '4':
                preferred_duration, _ = collect_session_configuration()
                if preferred_duration:
                    suggested_times = session_optimizer.suggest_optimal_session_time(preferred_duration)
                    print(f"Suggested Start Time: {suggested_times[0]}")
                    print(f"Suggested End Time: {suggested_times[1]}")
                else:
                    print("Invalid input. Please enter a valid number for the session duration.")

            elif choice == '5':
                break

            else:
                print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()