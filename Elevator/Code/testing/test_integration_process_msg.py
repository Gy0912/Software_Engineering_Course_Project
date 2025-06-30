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
        #  self.system.elevators[0].delt = 0.2
        #  self.system.elevators[1].delt = 0.2
        self.system.elevators[0].remain_open_time=1
        self.ui.show()
        QTest.qWait(2000)  # 确保UI完全加载


    def test_02_process_message(self):

        # TestCase1: reset
        for t in self.system.threads:
            t.start()
        self.system.elevators[0].current_floor = 2
        if self.system.elevators[0].update_callback:
            self.system.elevators[0].update_callback(self.system.elevators[0].id)
        self.system.elevators[1].current_floor = 3
        if self.system.elevators[1].update_callback:
            self.system.elevators[1].update_callback(self.system.elevators[1].id)
        QTest.qWait(500)
        
        self.system.zmqThread.receivedMessage= "reset"
        self.system.zmqThread.messageTimeStamp = time.time()
        self.system.messageUnprocessed = True
        while(self.system.messageUnprocessed):
            QTest.qWait(10)
        #  QTest.qWait(5000)  # 等待电梯移动
        while not(self.system.elevators[0].finished and self.system.elevators[1].finished):
            QTest.qWait(50)
        self.assertIn(self.system.elevators[1].state, [ElevatorState.stopped_door_closed, ElevatorState.stopped_closing_door])
        self.assertEqual(self.system.elevators[0].current_floor, 1)
        self.assertEqual(self.system.elevators[1].current_floor, 1)

        # TestCase2: call_up@2
        self.system.zmqThread.receivedMessage = "call_up@2"
        self.system.zmqThread.messageTimeStamp = time.time()
        self.system.messageUnprocessed = True
        #  for t in self.system.threads:
        #      t.start()
        while(self.system.messageUnprocessed):
            QTest.qWait(10)
        QTest.qWait(300)  # 等待电梯移动
        while (self.system.elevators[0].finished and self.system.elevators[1].finished):
            QTest.qWait(10)
        while not(self.system.elevators[0].finished and self.system.elevators[1].finished):
            QTest.qWait(10)
        self.assertIn(self.system.elevators[1].state, [ElevatorState.stopped_door_closed, ElevatorState.stopped_closing_door])
        self.assertEqual(self.system.elevators[0].current_floor, 2)
        self.assertEqual(self.system.elevators[1].current_floor, 1)

        # TestCase3: select_floor@3#1
        self.system.zmqThread.receivedMessage = "select_floor@3#1"
        self.system.zmqThread.messageTimeStamp = time.time()
        self.system.messageUnprocessed = True
        while(self.system.messageUnprocessed):
            QTest.qWait(10)
        #  QTest.qWait(6000)  # 等待电梯移动
        while (self.system.elevators[0].finished and self.system.elevators[1].finished):
            QTest.qWait(50)
        while not(self.system.elevators[0].finished and self.system.elevators[1].finished):
            QTest.qWait(50)
        self.assertIn(self.system.elevators[1].state, [ElevatorState.stopped_door_closed, ElevatorState.stopped_closing_door])
        self.assertEqual(self.system.elevators[0].current_floor, 3)
        self.assertEqual(self.system.elevators[1].current_floor, 1)

        while(self.system.elevators[0].state != ElevatorState.stopped_door_closed and self.system.elevators[0].finished == False):
            QTest.qWait(10)

        # TestCase4: open_door#1
        self.system.zmqThread.receivedMessage = "open_door#1"
        self.system.zmqThread.messageTimeStamp = time.time()
        self.system.messageUnprocessed = True
        while(self.system.messageUnprocessed):
            QTest.qWait(10)
        #  QTest.qWait(1000) # 等待电梯门打开
        while self.system.elevators[0].state == ElevatorState.stopped_door_closed:
            QTest.qWait(1)
        self.assertEqual(self.system.elevators[0].current_floor, 3)
        self.assertIn(self.system.elevators[0].state, [ElevatorState.stopped_door_opened, ElevatorState.stopped_opening_door])
        self.assertEqual(self.system.elevators[1].current_floor, 1)
        QTest.qWait(2000)

        # TestCase5: close_door#1
        #  self.system.elevators[0].running = False
        #  self.system.threads[1].join()  # 停止电梯1的线程

        self.system.remain_open_time = 1000
        self.system.elevators[0].open_door()
        while (self.system.elevators[0].state != ElevatorState.stopped_door_opened):
            QTest.qWait(10)
        #  self.system.
        self.system.elevators[0].finished = False

        self.system.elevators[0].message = ""
        self.system.zmqThread.receivedMessage = "close_door#1"
        self.system.zmqThread.messageTimeStamp = time.time()
        self.system.messageUnprocessed = True
        while(self.system.messageUnprocessed):
            QTest.qWait(10)
            
        while not (self.system.elevators[0].finished):
            QTest.qWait(10)

        self.assertEqual(self.system.elevators[0].current_floor, 3)
        #  self.assertEqual(self.system.elevators[0].state, ElevatorState.stopped_closing_door)
        self.assertEqual(self.system.elevators[0].message, "door_closed#1")

        # TestCase6: open_door#6
        # self.system.elevators[1].running = False
        self.system.elevators[1].state = ElevatorState.stopped_door_closed
        # self.system.elevators[1].finished = False

        self.system.zmqThread.receivedMessage = "open_door#6"
        self.system.zmqThread.messageTimeStamp = time.time()
        self.system.messageUnprocessed = True
        while(self.system.messageUnprocessed):
            QTest.qWait(10)
        self.assertEqual(self.system.elevators[0].finished, True)
        self.assertEqual(self.system.elevators[1].finished, True)
        self.assertEqual(self.system.elevators[0].current_floor, 3)
        self.assertEqual(self.system.elevators[0].current_floor, 3)
        self.assertEqual(self.system.elevators[1].state, ElevatorState.stopped_door_closed)

    def tearDown(self):
        """Cleanup after each test case"""

        self.ui.close()
        self.ui.deleteLater()
        QTest.qWait(1000)  # Ensure the UI is closed before the next test

    @classmethod
    def tearDownClass(cls):
        """Cleanup work after all test cases are executed"""
        # Ensure the event loop runs long enough to display the window
        QTest.qWait(1000)  # Delay 1 second to ensure the window is displayed
        cls.app.quit()
if __name__ == '__main__':
    unittest.main()
