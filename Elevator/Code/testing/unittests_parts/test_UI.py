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
from elevator_UI import ElevatorSystemUI, ElevatorUI

class TestElevatorUI(unittest.TestCase):
   @classmethod
   def setUpClass(cls):
       cls.app = QApplication(sys.argv)

   def setUp(self):
       self.elevator_ui = ElevatorUI(1, max_floors=3)

   def test_00_initial_state(self):

       self.assertEqual(self.elevator_ui.windowTitle(), "Elevator 1")

       self.assertEqual(len(self.elevator_ui.floor_buttons), 4)

       # 检查按钮文本
       self.assertEqual(self.elevator_ui.floor_buttons[3].text(), "3")
       self.assertEqual(self.elevator_ui.floor_buttons[0].text(), "-1")

       # 检查初始楼层显示
       self.assertEqual(self.elevator_ui.floor_display.text(), "1")

       # 检查初始方向显示
       self.assertEqual(self.elevator_ui.direction_display.text(), "■")

   def test_01_highlight_floor_button(self):
       """Test highlight_floor_button() method"""
       self.elevator_ui.highlight_floor_button(1, True)
       f1_btn = self.elevator_ui.floor_buttons[1]
       self.assertEqual(f1_btn.styleSheet(), "background-color: #FFA500; font-weight: bold;")
       self.elevator_ui.highlight_floor_button(1, False)
       self.assertEqual(f1_btn.styleSheet(), "")
       self.elevator_ui.highlight_floor_button(8, True)
       self.assertEqual(f1_btn.styleSheet(), "")

   def test_02_update_state(self):
       """Test update_state() method"""

       # Testcase1
       self.elevator_ui.update_state(1, 1)
       self.assertEqual(self.elevator_ui.direction_display.text(), "↑")
       self.assertEqual(self.elevator_ui.direction_display.styleSheet(), "color: green;")

       # Testcase2
       self.elevator_ui.update_state(1, -1)
       self.assertEqual(self.elevator_ui.direction_display.text(), "↓")
       self.assertEqual(self.elevator_ui.direction_display.styleSheet(), "color: red;")

       # Testcase3
       self.elevator_ui.update_state(1, 0)
       self.assertEqual(self.elevator_ui.direction_display.text(), "■")
       self.assertEqual(self.elevator_ui.direction_display.styleSheet(), "color: gray;")

class TestElevatorSystemUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)
    
    def setUp(self):
        self.elevator_system = ElevatorSystem(num_elevators=2, max_floor=3, identity="TestUI")
        self.ui = ElevatorSystemUI(self.elevator_system, num_elevators=2, max_floors=3)

    def test_00_initial_state(self):
        """Test Init states"""

        self.assertEqual(self.ui.windowTitle(), "Elevator Control System")
        
        self.assertEqual(len(self.ui.up_buttons), 3)
        self.assertEqual(len(self.ui.down_buttons), 3)
        
        # 检查按钮文本
        self.assertEqual(self.ui.up_buttons[2].text(), "▲")
        self.assertEqual(self.ui.up_buttons[1].text(), "▲")
        self.assertEqual(self.ui.up_buttons[0].text(), "▲")
        # 检查按钮文本
        self.assertEqual(self.ui.down_buttons[3].text(), "▼")
        self.assertEqual(self.ui.down_buttons[2].text(), "▼")
        self.assertEqual(self.ui.down_buttons[1].text(), "▼")
        
        # 检查初始楼层显示
        self.assertEqual(self.ui.elevator_1_floor3.text(), "1")
        self.assertEqual(self.ui.elevator_2_floor3.text(), "1")
        
        # 检查初始方向显示
        self.assertEqual(self.ui.elevator_1_direction3.text(), "")
        self.assertEqual(self.ui.elevator_2_direction3.text(), "")


    def test_01_highlight_call_button(self):
        """Test highlight_call_button() in ElevatorSystem"""

        self.ui.highlight_call_button(1, 1 ,True)
        self.assertEqual(self.ui.up_buttons[1].styleSheet(), "background-color: #FFA500; font-weight: bold;")

        self.ui.highlight_call_button(-1, 1 ,False)
        self.assertEqual(self.ui.down_buttons[1].styleSheet(), "")
        self.ui.highlight_call_button(-1, -1 ,True)

    def test_02_update_button_highlights(self):
        """Test update_button_highlights()"""

        # Testcase1
        self.ui.elevator_system.elevators[0].destination_floors=[]
        self.ui.elevator_system.elevators[0].destination_floors.append((1, Direction.IDLE,0))
        self.ui.update_button_highlights()
        f1_btn = self.ui.elevators[0].floor_buttons[1]
        self.assertEqual(f1_btn.styleSheet(), "background-color: #FFA500; font-weight: bold;")

        # Testcase2
        self.ui.elevator_system.elevators[0].destination_floors=[]
        self.ui.elevator_system.elevators[0].destination_floors.append((1, Direction.UP,0))
        self.ui.update_button_highlights()
        f1_btn = self.ui.elevators[0].floor_buttons[1]
        self.assertEqual(f1_btn.styleSheet(), "")

    def test_03_handle_door_command(self):
        """Test handle_door_command()"""

        # Testcase1
        self.ui.handle_door_command(1, 0)
        self.assertEqual(self.elevator_system.zmqThread.receivedMessage, "open_door#1")

        # Testcase2
        self.ui.handle_door_command(2, 1)
        self.assertEqual(self.elevator_system.zmqThread.receivedMessage, "close_door#2")

    def tesat_04_update_ui_from_system(self):
        """Test update_ui_from_system()"""

        # Testcase1
        #  1: elevators[0].direction = 1; elevators[1].direction = -1; elevators[0].current_floor = 0, elevators[1],current_floor = 0 -> TC 1, TC3, TC4, TC5
        self.ui.elevator_system.elevators[0].direction = 1
        self.ui.elevator_system.elevators[0].current_floor = 0

        self.ui.elevator_system.elevators[1].direction = -1
        self.ui.elevator_system.elevators[1].current_floor = 0
        self.ui.update_ui_from_system()
        self.assertEqual(self.ui.elevator_1_direction3.text(), "▲")
        self.assertEqual(self.ui.elevator_2_direction3.text(), "▼")
        self.assertEqual(self.ui.elevator_1_floor3.text(), "-1")
        self.assertEqual(self.ui.elevator_2_floor3.text(), "-1")


        # Testcase2
        #  2: elevators[0].direction = 0; elevators[1].direction = 0; elevators[0].current_floor = 1 , elevators[0].current_floor = 1-> TC2, Tc4， TC6
        self.ui.elevator_system.elevators[0].direction = 0
        self.ui.elevator_system.elevators[0].current_floor = 1

        self.ui.elevator_system.elevators[1].direction = 0
        self.ui.elevator_system.elevators[1].current_floor = 1
        self.ui.update_ui_from_system()
        self.assertEqual(self.ui.elevator_1_direction3.text(),"■")
        self.assertEqual(self.ui.elevator_2_direction3.text(), "■")
        self.assertEqual(self.ui.elevator_1_floor3.text(), "1")
        self.assertEqual(self.ui.elevator_2_floor3.text(), "1")

    def tearDown(self):
        """Cleanup after each test case"""

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
