import unittest
from datetime import datetime, timedelta
import os
import tempfile
from session_manager import SessionManager, create_temp_session_manager
from session_tracker import SessionTracker, create_temp_session_tracker
from session_optimizer import SessionOptimizer, create_temp_session_optimizer

class TestSessionManager(unittest.TestCase):
    def setUp(self) -> None:
        self.session_manager = create_temp_session_manager()
        self.session_tracker = create_temp_session_tracker()
    def test_start_and_stop_session(self) -> None:
        self.session_manager.start_session()
        self.session_manager.stop_session()
        status = self.session_manager.get_session_status()
        self.assertIsNotNone(status)
        start_time, end_time = status
        self.assertIsInstance(start_time, datetime)
        self.assertIsInstance(end_time, datetime)

    def test_get_session_status(self) -> None:
        self.session_manager.start_session()
        status = self.session_manager.get_session_status()
        self.assertIsNotNone(status)
        start_time, end_time = status
        self.assertIsInstance(start_time, datetime)
        self.assertIsNone(end_time)

    def tearDown(self) -> None:
        import shutil
        temp_dir = self.session_manager.storage_path
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        temp_dir = self.session_tracker.session_path
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        # SessionTracker has no 'storage_path'; only session_path is valid
        temp_dir = self.session_tracker.session_path
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
