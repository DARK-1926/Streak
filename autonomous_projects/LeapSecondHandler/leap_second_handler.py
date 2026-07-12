import datetime
import time
from typing import Optional

class LeapSecondHandler:
    """
    A class to handle and adjust for negative leap seconds in time-sensitive systems.
    """

    def __init__(self):
        self.last_leap_second: Optional[datetime.datetime] = None

    def check_leap_second(self) -> bool:
        """
        Check if the system is currently affected by a negative leap second.

        Returns:
            bool: True if a negative leap second is detected, False otherwise.
        """
        try:
            # Simulate checking for a leap second (this is a placeholder)
            current_time = datetime.datetime.utcnow()
            if self.last_leap_second and (current_time - self.last_leap_second).total_seconds() < 1:
                return True
            else:
                self.last_leap_second = current_time
                return False
        except Exception as e:
            print(f"An error occurred while checking for leap second: {e}")
            return False

    def adjust_time(self, timestamp: float) -> float:
        """
        Adjust the given timestamp if a negative leap second is detected.

        Args:
            timestamp (float): The original timestamp in Unix epoch format.

        Returns:
            float: The adjusted timestamp.
        """
        try:
            if self.check_leap_second():
                # Adjust the timestamp by subtracting one second
                adjusted_timestamp = timestamp - 1.0
                return adjusted_timestamp
            else:
                return timestamp
        except Exception as e:
            print(f"An error occurred while adjusting the timestamp: {e}")
            return timestamp

# Example usage
if __name__ == "__main__":
    handler = LeapSecondHandler()
    current_time = time.time()
    adjusted_time = handler.adjust_time(current_time)
    print(f"Current Time: {current_time}, Adjusted Time: {adjusted_time}")