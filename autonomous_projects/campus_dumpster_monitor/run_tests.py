import unittest
from campus_dumpster_monitor.detector import Detector

class TestDetector(unittest.TestCase):
    def test_detector_initialization(self):
        detector = Detector()
        self.assertIsInstance(detector, Detector)

    def test_detection_logic(self):
        detector = Detector()
        self.assertTrue(detector.detect(None))

if __name__ == '__main__':
    unittest.main()
