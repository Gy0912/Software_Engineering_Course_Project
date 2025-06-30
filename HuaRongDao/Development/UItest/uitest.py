import sys
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from main import SimpleApp

class TestSimpleApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the test environment and set class-level variables"""
        cls.app = QApplication(sys.argv)

    def setUp(self):
        """Initialization of each test case"""
        self.form = SimpleApp()
        self.form.show()

    def test_button_click(self):
        """Test button click functionality and observe GUI changes"""
        QTest.qWait(1000)  # Wait for 1000 milliseconds to observe the interface change
        self.assertEqual(self.form.label.text(), 'Initial Text')
        QTest.mouseClick(self.form.button, Qt.LeftButton)
        QTest.qWait(1000)  # Wait for 1000 milliseconds to observe the interface change
        self.assertEqual(self.form.label.text(), 'Text Updated')

    def tearDown(self):
        """Cleanup after each test case"""
        self.form.close()

    @classmethod
    def tearDownClass(cls):
        """Cleanup work after all test cases are executed"""
        # Ensure the event loop runs long enough to display the window
        QTest.qWait(1000)  # Delay 1 second to ensure the window is displayed
        cls.app.quit()

if __name__ == "__main__":
    unittest.main()