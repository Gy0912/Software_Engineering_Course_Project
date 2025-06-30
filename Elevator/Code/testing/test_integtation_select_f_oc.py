import unittest
import time
import sys
import threading
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../system")))
from elevator_system import ElevatorSystem
from elevator import ElevatorState, Direction
from elevator_UI import ElevatorSystemUI

class TestElevatorSystemIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)
    
    def setUp(self):
        self.system = ElevatorSystem(num_elevators=2, max_floor=3, identity="Test")
        self.ui = ElevatorSystemUI(self.system, num_elevators=2, max_floors=3)
        for t in self.system.threads:
            t.start()
        #  self.system.elevators[0].delt = 0.2
        #  self.system.elevators[1].delt = 0.2
        self.system.elevators[0].remain_open_time=1
        self.ui.show()
        QTest.qWait(2000)  # 确保UI完全加载
        
    def test_02_select_floor_buttons(self):
        #  1: (1, 2) -> TCOVER1, TCOVER2, TCOVER11, TCOVER12
        #
        #  2: (2, -1) -> TCOVER1, TCOVER3, TCOVER11, TCOVER13

        QTest.mouseClick(self.ui.elevators[0].floor_buttons[2], Qt.MouseButton.LeftButton)
        QTest.qWait(100)
        QTest.mouseClick(self.ui.elevators[1].floor_buttons[0], Qt.MouseButton.LeftButton)
        QTest.qWait(100)
        self.assertEqual(self.system.elevators[0].state, ElevatorState.up)
        self.assertEqual(self.system.elevators[1].state, ElevatorState.down)
        while not(self.system.elevators[0].finished and self.system.elevators[1].finished):
            QTest.qWait(50)
        self.assertEqual(self.system.elevators[0].current_floor, 2)
        self.assertEqual(self.system.elevators[1].current_floor, 0)

    def test_01_door_control_buttons(self):
        """测试电梯门控制按钮(select_oc())"""
        # Testcase1: 
        # 1. click open door button on elevator 1
        QTest.mouseClick(self.ui.reset_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(1000)
        open_btn = self.ui.elevators[0].open_btn
        QTest.mouseClick(open_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(500)
        self.assertEqual(self.system.elevators[0].state, ElevatorState.stopped_opening_door)
        self.assertEqual(self.system.elevators[0].current_floor, 1)
        self.assertEqual(self.system.elevators[1].state, ElevatorState.stopped_door_closed)
        #  QTest.qWait(5000)
        while not(self.system.elevators[0].finished and self.system.elevators[1].finished):
            QTest.qWait(50)
        self.assertIn(self.system.elevators[1].state, [ElevatorState.stopped_door_closed, ElevatorState.stopped_closing_door])

        # Testcase2:
        # 2.1 click close door button on elevator when the state is stopped_door_closed
        QTest.mouseClick(self.ui.reset_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(2000)
        open_btn = self.ui.elevators[1].open_btn
        QTest.mouseClick(open_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(500)
        self.assertEqual(self.system.elevators[1].state, ElevatorState.stopped_opening_door)
        self.assertEqual(self.system.elevators[1].current_floor, 1)
        self.assertEqual(self.system.elevators[0].state, ElevatorState.stopped_door_closed)
        QTest.mouseClick(self.ui.elevators[1].close_btn, Qt.MouseButton.LeftButton)
        #  QTest.qWait(5000)
        while not(self.system.elevators[0].finished and self.system.elevators[1].finished):
            QTest.qWait(50)
        self.assertIn(self.system.elevators[1].state, [ElevatorState.stopped_door_closed, ElevatorState.stopped_closing_door])

        # 2.2 click close door button when openning
        QTest.mouseClick(self.ui.reset_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(2000)
        open_btn = self.ui.elevators[1].open_btn
        QTest.mouseClick(open_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(100)
        close_btn = self.ui.elevators[1].close_btn
        QTest.mouseClick(close_btn, Qt.MouseButton.LeftButton)
        self.assertEqual(self.system.elevators[1].state, ElevatorState.stopped_opening_door)
        self.assertEqual(self.system.elevators[1].current_floor, 1)
        self.assertEqual(self.system.elevators[0].state, ElevatorState.stopped_door_closed)
        QTest.mouseClick(self.ui.elevators[1].close_btn, Qt.MouseButton.LeftButton)
        #  QTest.qWait(5000)
        while not(self.system.elevators[1].finished):
            QTest.qWait(50)
        self.assertIn(self.system.elevators[1].state, [ElevatorState.stopped_door_closed, ElevatorState.stopped_closing_door])
        
        # 2.3 click open when closing
        QTest.mouseClick(self.ui.reset_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(2000)
        open_btn = self.ui.elevators[1].open_btn
        QTest.mouseClick(open_btn, Qt.MouseButton.LeftButton)
        while self.system.elevators[1].state != ElevatorState.stopped_closing_door:
            QTest.qWait(20)
        self.assertEqual(self.system.elevators[1].state, ElevatorState.stopped_closing_door)

        QTest.qWait(200)
        QTest.mouseClick(open_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(200)

        self.assertIn(self.system.elevators[1].state, [ElevatorState.stopped_opening_door,ElevatorState.stopped_door_opened])
        self.assertEqual(self.system.elevators[1].current_floor, 1)
        self.assertEqual(self.system.elevators[0].state, ElevatorState.stopped_door_closed)
        QTest.mouseClick(self.ui.elevators[1].close_btn, Qt.MouseButton.LeftButton)
        #  QTest.qWait(5000)
        while not(self.system.elevators[1].finished):
            QTest.qWait(50)
        self.assertIn(self.system.elevators[1].state, [ElevatorState.stopped_door_closed, ElevatorState.stopped_closing_door])

    def tearDown(self):
        """Cleanup after each test case"""

        self.ui.close()
        self.ui.deleteLater()
        QTest.qWait(1000)  # Ensure the UI is closed before the next test

        # import gc
        # gc.collect()

    @classmethod
    def tearDownClass(cls):
        """Cleanup work after all test cases are executed"""
        # Ensure the event loop runs long enough to display the window
        QTest.qWait(1000)  # Delay 1 second to ensure the window is displayed
        cls.app.quit()
if __name__ == '__main__':
    unittest.main()
