import unittest
import threading
import time
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../system")))
from elevator_system import ElevatorSystem, ElevatorState
from NetClient import ZmqClientThread
from elevator import Elevator, ElevatorState, Direction
class TestElevatorSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication instance once for all tests
        cls.app = QApplication(sys.argv)

    def setUp(self):
        # Mock the run method to prevent blocking
        # self.patcher = patch.object(ElevatorSystem, 'run')
        # self.mock_run = self.patcher.start()
        
        # Create an elevator system with 2 elevators and 3 floors for testing
        self.elevator_system = ElevatorSystem(num_elevators=2, max_floor=3, identity="TestSystem")
        self.call_elevator_thread = None
        for t in self.elevator_system.threads:
            if t.name == "call_elevator_thread":
                self.call_elevator_thread = t
                break
        
        # Short sleep to allow threads to initialize
        time.sleep(0.1)

    def test_00_initial_state(self):
        """Test that elevator system initializes with correct default values"""
        self.assertEqual(len(self.elevator_system.elevators), 2)
        self.assertEqual(self.elevator_system.max_floor, 3)
        self.assertEqual(len(self.elevator_system.call_requests), 0)
        self.assertEqual(len(self.elevator_system.active_requests), 0)
        
        # Check each elevator's initial state
        for i, elevator in enumerate(self.elevator_system.elevators):
            self.assertEqual(elevator.id, i+1)
            self.assertEqual(elevator.current_floor, 1)
            self.assertEqual(elevator.state, ElevatorState.stopped_door_closed)

    def test_01_call_elevator(self):
        """Test the call elevator logic"""

        #  Test Case 1:
        #  self.call_requests = [(1,Direction.UP, True),(2, Direction.UP, True), (1, Direction.DOWN, True), (1, Direction.DOWN, True)],
        #  self.elevators.current_floors = [-1, 3]
        #  self.elevators.states = [up, down]
        self.elevator_system.call_requests = [(1,Direction.UP, True),(2, Direction.UP, True), (1, Direction.DOWN, True), (1, Direction.DOWN, True)]
        self.elevator_system.elevators[0].current_floor = 0
        self.elevator_system.elevators[1].current_floor = 3
        self.elevator_system.elevators[0].state = ElevatorState.up
        self.elevator_system.elevators[1].state = ElevatorState.down
        self.call_elevator_thread.start()
        while self.elevator_system.call_requests:
            continue
        self.elevator_system.running = False
        self.assertEqual(len(self.elevator_system.call_requests), 0)
        self.assertIn([2,Direction.UP,0], self.elevator_system.elevators[0].destination_floors)
        self.assertIn([1,Direction.DOWN,0], self.elevator_system.elevators[1].destination_floors)
        self.assertIn([1,Direction.UP,0], self.elevator_system.elevators[1].destination_floors)
        self.assertEqual(len(self.elevator_system.elevators[1].destination_floors), 2)

        #  Test Case 2:
        #  self.call_requests = None
        #
        #  : TC3
        for elevator in self.elevator_system.elevators:
            elevator.reset()
        self.call_elevator_thread = threading.Thread(target=self.elevator_system.call_elevator)
        self.call_elevator_thread.deamon = True
        self.elevator_system.call_requests = []
        self.elevator_system.running = True
        self.call_elevator_thread.start()
        while self.elevator_system.call_requests:
            continue
        self.elevator_system.running = False
        self.assertEqual(len(self.elevator_system.call_requests), 0)
        self.assertEqual(len(self.elevator_system.elevators[0].destination_floors), 0)
        self.assertEqual(len(self.elevator_system.elevators[1].destination_floors), 0)


        #  Test Case 3:
        #  self.call_requests = [(2,Direction.UP, True),(2, Direction.DOWN, True)],
        #  self.elevators.current_floors = [1, 3]
        #  self.elevators.states = [stopped_closing_door, stopped_closing_door]
        #  self.elevators.directions = [Direction.UP, Direction.DOWN]
        for elevator in self.elevator_system.elevators:
            elevator.reset()
        self.call_elevator_thread = threading.Thread(target=self.elevator_system.call_elevator)
        self.call_elevator_thread.deamon = True
        self.elevator_system.call_requests = [(2,Direction.UP, True),(2, Direction.DOWN, True)]
        self.elevator_system.elevators[0].current_floor = 1
        self.elevator_system.elevators[1].current_floor = 3
        self.elevator_system.elevators[0].state = ElevatorState.stopped_closing_door
        self.elevator_system.elevators[1].state = ElevatorState.stopped_closing_door
        self.elevator_system.elevators[0].direction = Direction.UP
        self.elevator_system.elevators[1].direction = Direction.DOWN
        self.elevator_system.running = True
        self.call_elevator_thread.start()
        while self.elevator_system.call_requests:
            continue
        self.elevator_system.running = False
        self.assertEqual(len(self.elevator_system.call_requests), 0)
        self.assertIn([2,Direction.UP,0], self.elevator_system.elevators[0].destination_floors)
        self.assertIn([2,Direction.DOWN,0], self.elevator_system.elevators[1].destination_floors)
        self.assertEqual(len(self.elevator_system.elevators[0].destination_floors), 1)
        self.assertEqual(len(self.elevator_system.elevators[1].destination_floors), 1)

    def test_02_select_floor(self):
        """Test selecting floors in elevators"""
        # TestCase 1: Select floor 2 in elevator 1
        self.elevator_system.select_floor(1, 2)
        self.assertEqual(len(self.elevator_system.elevators[0].destination_floors), 1)
        self.assertEqual(len(self.elevator_system.elevators[1].destination_floors), 0)
        self.assertEqual(self.elevator_system.elevators[0].destination_floors[0][0], 2)
        self.assertEqual(self.elevator_system.elevators[0].destination_floors[0][1], Direction.IDLE)

        # TestCase 2: Select invalid floor
        for elevator in self.elevator_system.elevators:
            elevator.reset()
        self.elevator_system.select_floor(1, 5)
        self.assertEqual(len(self.elevator_system.elevators[1].destination_floors), 0)
        self.assertEqual(len(self.elevator_system.elevators[0].destination_floors), 0)

    def test_03_select_oc(self):
        """Test door open/close operations"""
        #  Test Case 1:
        #  elevator_id=1, op=0
        self.elevator_system.select_oc(1, 0)
        self.assertEqual(self.elevator_system.elevators[0].state, ElevatorState.stopped_opening_door)

        #  Test Case 2:
        #  elevator_id=2, op=1 : TC2
        self.elevator_system.select_oc(2, 1)
        self.assertEqual(self.elevator_system.elevators[1].state, ElevatorState.stopped_door_closed)

        #  Test Case 3:
        #  elevator_id=6, op=1 : TC2
        self.elevator_system.select_oc(2, 1)
        self.assertEqual(self.elevator_system.elevators[1].state, ElevatorState.stopped_door_closed)

    def test_04_process_message(self):
        """Test processing messages from the server"""
        # TestCase 1: Reset message
        self.elevator_system.serverMessage = "reset"
        self.elevator_system.process_message()
        for elevator in self.elevator_system.elevators:
            self.assertEqual(elevator.current_floor, 1)
            self.assertEqual(len(elevator.destination_floors), 0)
            self.assertEqual(elevator.state, ElevatorState.stopped_door_closed)


        # TestCase 2: Call up message
        for elevator in self.elevator_system.elevators:
            elevator.reset()
        self.elevator_system.call_requests = []  
        self.elevator_system.serverMessage = "call_up@2"
        self.elevator_system.process_message()
        self.assertEqual(len(self.elevator_system.call_requests), 1)
        self.assertEqual(self.elevator_system.call_requests[0][0], 2)
        self.assertEqual(self.elevator_system.call_requests[0][1], Direction.UP)

        # TestCase 3: Select floor message
        for elevator in self.elevator_system.elevators:
            elevator.reset()
        self.elevator_system.call_requests = []  
        self.elevator_system.serverMessage = "select_floor@2#1"
        self.elevator_system.process_message()
        self.assertEqual(len(self.elevator_system.elevators[0].destination_floors), 1)
        self.assertEqual(len(self.elevator_system.elevators[1].destination_floors), 0)
        self.assertEqual(self.elevator_system.elevators[0].destination_floors[0][0], 2)
        self.assertEqual(self.elevator_system.elevators[0].destination_floors[0][1], Direction.IDLE)

        #  Test Case 4:
        #  self.serverMessage = "open_door#1" 
        for elevator in self.elevator_system.elevators:
            elevator.reset()
        self.elevator_system.call_requests = []  
        self.elevator_system.serverMessage = "open_door#1"
        self.elevator_system.process_message()
        self.assertEqual(self.elevator_system.elevators[0].state, ElevatorState.stopped_opening_door)

        #  Test Case 5:
        #  self.serverMessage = "close_door#1" : TC9
        for elevator in self.elevator_system.elevators:
            elevator.reset()
        self.elevator_system.call_requests = []  
        self.elevator_system.serverMessage = "close_door#1"
        self.elevator_system.process_message()
        self.assertEqual(self.elevator_system.elevators[1].state, ElevatorState.stopped_door_closed)

        #  Test Case 6:
        #  self.serverMessage = "invalid_command" : TC2, TC4, TC6, TC8, TC10
        for elevator in self.elevator_system.elevators:
            elevator.reset()
        self.elevator_system.call_requests = []  
        self.elevator_system.serverMessage = "invalid_command"
        self.elevator_system.process_message()
        self.assertEqual(len(self.elevator_system.call_requests), 0)
        for elevator in self.elevator_system.elevators:
            self.assertEqual(elevator.state, ElevatorState.stopped_door_closed)
            self.assertEqual(len(elevator.destination_floors), 0)

    def tearDown(self):
        # Clean up by shutting down the elevator system
        self.elevator_system.shutdown()
        # self.patcher.stop()
        time.sleep(0.1)  # Allow time for threads to stop

if __name__ == '__main__':
    unittest.main()
