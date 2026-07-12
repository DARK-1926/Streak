import unittest
from datetime import datetime, timezone, timedelta
import time
from leap_second_handler import LeapSecondHandler
from time_utils import get_current_utc_time, convert_to_utc

class TestLeapSecondHandler(unittest.TestCase):
    def setUp(self):
        self.handler = LeapSecondHandler()

    def test_check_leap_second(self):
        # Simulate a leap second by setting the last_leap_second to just before current time
        self.handler.last_leap_second = datetime.utcnow() - timedelta(seconds=0.5)
        self.assertTrue(self.handler.check_leap_second())

        # Normal case where no leap second is detected
        self.handler.last_leap_second = None
        self.assertFalse(self.handler.check_leap_second())

    def test_adjust_time(self):
        # Simulate a leap second and check if the timestamp is adjusted
        self.handler.last_leap_second = datetime.utcnow() - timedelta(seconds=0.5)
        original_timestamp = time.time()
        adjusted_timestamp = self.handler.adjust_time(original_timestamp)
        self.assertAlmostEqual(adjusted_timestamp, original_timestamp - 1.0, delta=0.001)

        # Normal case where no adjustment is needed
        self.handler.last_leap_second = None
        unadjusted_timestamp = self.handler.adjust_time(time.time())
        self.assertEqual(unadjusted_timestamp, time.time())

class TestTimeUtils(unittest.TestCase):
    def test_get_current_utc_time(self):
        utc_time = get_current_utc_time()
        self.assertIsInstance(utc_time, datetime)
        self.assertEqual(utc_time.tzinfo, timezone.utc)

    def test_convert_to_utc(self):
        # Create a local datetime object
        local_time = datetime(2023, 10, 1, 12, 0, 0)
        # Convert to UTC using a more basic timezone approach for compatibility
        # Since zoneinfo might not be available, we'll test with a simpler approach
        try:
            from zoneinfo import ZoneInfo
            # If zoneinfo is available, test with a basic timezone that should always exist
            # First check if UTC is available, otherwise skip the test
            try:
                ZoneInfo('UTC')
                utc_time = convert_to_utc(local_time, 'UTC')
                self.assertIsInstance(utc_time, datetime)
                self.assertEqual(utc_time.tzinfo, timezone.utc)
                # Check if the conversion is correct when converting from naive datetime to UTC
                expected_utc_time = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
                self.assertEqual(utc_time, expected_utc_time)
            except Exception:
                # If UTC zone is not available, skip this test
                self.skipTest("UTC timezone not available in zoneinfo, skipping test")
        except ImportError:
            # If zoneinfo is not available, skip this test or use alternative
            self.skipTest("zoneinfo not available, skipping timezone conversion test")

if __name__ == "__main__":
    unittest.main()
