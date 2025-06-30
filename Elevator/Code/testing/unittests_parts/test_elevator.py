import unittest
import threading
import time
from unittest.mock import Mock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../system")))
from NetClient import ZmqClientThread
from elevator import Elevator, ElevatorState, Direction

class TestElevator(unittest.TestCase):
    def setUp(self):
        # Create a mock ZMQ client thread
        self.zmq_mock = ZmqClientThread(identity="Team8")
        # self.shared_lock = threading.Lock()
        
        # Create an elevator instance for testing
        self.elevator = Elevator(id=1, max_floor=3, zmqThread=self.zmq_mock)
        
        # Start the elevator thread
        self.elevator.stop()
        self.elevator_thread = threading.Thread(target=self.elevator.move_api)
        self.elevator_thread.daemon = True
        # self.elevator_thread.start()
        
        # Short sleep to allow thread to initialize
        time.sleep(0.1)


    def test_00_initial_state(self):
        """Test that elevator initializes with correct default values"""
        self.assertEqual(self.elevator.current_floor, 1)
        self.assertEqual(self.elevator.direction, Direction.IDLE)
        self.assertEqual(self.elevator.state, ElevatorState.stopped_door_closed)
        self.assertEqual(len(self.elevator.destination_floors), 0)
        self.assertEqual(len(self.elevator.active_requests), 0)

    def test_01_add_destination(self):
        """Test adding destinations to the elevator"""
        # TestCase 1
        self.elevator.add_destination(-1, Direction.IDLE, 0)
        self.assertEqual(self.elevator.destination_floors[0], [0, Direction.IDLE, 0])


        # TestCase 2
        self.elevator.reset()
        self.elevator.add_destination(2, Direction.UP, 0)
        self.elevator.add_destination(2, Direction.UP, 0)
        self.assertEqual(len(self.elevator.active_requests), 1)
        self.assertEqual(len(self.elevator.destination_floors), 1)
        self.assertEqual(self.elevator.destination_floors[0], [2, Direction.UP, 0])
        self.assertIn((2, Direction.UP), self.elevator.active_requests)
        self.assertEqual(self.elevator.direction, Direction.UP)

        # TestCase 3
        self.elevator.reset()
        self.elevator.add_destination(2, Direction.IDLE, 0)
        self.elevator.add_destination(3, Direction.IDLE, 0)
        self.assertEqual(len(self.elevator.destination_floors), 2)
        self.assertEqual(self.elevator.direction, Direction.UP)

        # TestCase 4
        self.elevator.reset()
        self.elevator.add_destination(1, Direction.UP, 0)
        self.assertEqual(len(self.elevator.active_requests), 1)
        self.assertEqual(self.elevator.destination_floors[0], [1, Direction.UP, 0])
        self.assertEqual(len(self.elevator.destination_floors), 1)

        # fakely simulate the elevator deal with the request
        self.elevator.update_destination()
        self.assertEqual(len(self.elevator.destination_floors), 0)
        self.assertEqual(len(self.elevator.active_requests), 0)
        self.elevator.state = ElevatorState.stopped_door_opened
        self.elevator.add_destination(1, Direction.UP, 0)
        self.assertEqual(len(self.elevator.destination_floors), 1)
        self.assertEqual(len(self.elevator.active_requests), 1)

    def test_02_resort_destination(self):
        """Test that destinations are resorted correctly"""

        # TestCase 1:
        #  self.destination_floors = [[2, Direction.IDLE, 0.0], [3, Direction.IDLE, 0.0]]
        #  self.state=stopped_door_closed;
        #  self.direction=Direction.IDLE;
        #  self.current_floor=1
        #  self.car=[1,0]

        # add 3 before 2
        self.elevator.destination_floors = [[2, Direction.IDLE, 0.0], [3, Direction.IDLE, 0.0]]
        self.currentDestination = [1, Direction.IDLE, 0.0]
        self.elevator.resort_destination()
        # Check the order of destinations: 2 shoule be before 3
        self.assertEqual(len(self.elevator.destination_floors), 2)
        self.assertEqual(self.elevator.destination_floors[0][0], 2)
        self.assertEqual(self.elevator.destination_floors[1][0], 3)

        # TestCase 2:
        # destination_floors=[(2, Direction.DOWN, 0), (1,Direction.IDLE, 0)]
        #  self.state=down; self.direction=DOWN;
        #  self.current_floor=3;self.car=[3,0]
        self.elevator.reset()
        self.elevator.currentDestination = [0, Direction.IDLE, 0.0]
        self.elevator.state = ElevatorState.down
        self.elevator.direction = Direction.DOWN
        self.elevator.current_floor = 3
        self.elevator.car = [3, 0]
        self.elevator.destination_floors = [[2, Direction.DOWN, 0], [1, Direction.IDLE, 0]]
        self.elevator.resort_destination()

        self.assertEqual(len(self.elevator.destination_floors), 2)
        self.assertEqual(self.elevator.destination_floors[0][0], 2)
        self.assertEqual(self.elevator.destination_floors[1][0], 1)

        # #  Test Case 3:
        # #  destination_floors=[(1, Direction.IDLE, 0), (2,Direction.IDLE, 0)]
        # #  self.state=up; self.direction=UP;
        # #  self.current_floor=1;self.car=[1.7,0]
        self.elevator.reset()
        self.elevator.currentDestination = [0, Direction.IDLE, 0.0]
        self.elevator.state = ElevatorState.up
        self.elevator.direction = Direction.UP
        self.elevator.current_floor = 1
        self.elevator.car = [1.7, 0]
        self.elevator.current_floor = 3
        self.elevator.destination_floors = [[0, Direction.IDLE, 0], [2, Direction.UP, 0]]
        self.elevator.resort_destination()

        self.assertEqual(len(self.elevator.destination_floors), 2)
        self.assertEqual(self.elevator.destination_floors[0][0], 2)
        self.assertEqual(self.elevator.destination_floors[1][0], 0)

        #  Test Case 4:
        #  self.state=down;
        #  self.direction=DOWN;
        #  self.current_floor=3;
        #  self.car=[2.7,0]
        #  destination_floors=[(3, Direction.IDLE, 0), (1,Direction.IDLE, 0)]
        self.elevator.reset()
        self.elevator.state = ElevatorState.down
        self.elevator.direction = Direction.DOWN
        self.elevator.current_floor = 3
        self.elevator.car = [2,7, 0]
        self.elevator.destination_floors = [[3, Direction.IDLE, 0], [1, Direction.DOWN, 0]]
        self.elevator.currentDestination = [2, Direction.IDLE, 0]
        self.elevator.resort_destination()

        self.assertEqual(len(self.elevator.destination_floors), 2)
        self.assertEqual(self.elevator.destination_floors[0][0], 1)
        self.assertEqual(self.elevator.destination_floors[1][0], 3)


    def test_03_open_door(self):
        """Test that the elevator can properly open its door"""
        #  Test Case 1: self.state=stopped_door_opened :
        self.elevator.state = ElevatorState.stopped_door_opened
        self.elevator.open_door()
        self.assertEqual(self.elevator.state, ElevatorState.stopped_door_opened)

        #  Test Case 2: self.state=stopped_door_closed : TC2, TC4, TC5, TC7
        self.elevator.reset()
        self.elevator.state = ElevatorState.stopped_door_closed
        self.elevator.open_door()
        self.assertEqual(self.elevator.state, ElevatorState.stopped_opening_door)

        #  Test Case 3: self.state=up: TC1
        self.elevator.reset()
        self.elevator.state = ElevatorState.up
        self.elevator.open_door()
        self.assertEqual(self.elevator.state, ElevatorState.up)

        #  Test Case 4: self.state=stopped_opening_door: TC2, TC4, TC6, TC8
        self.elevator.reset()
        self.elevator.state = ElevatorState.stopped_opening_door
        self.elevator.open_door()
        self.assertEqual(self.elevator.state, ElevatorState.stopped_opening_door)

    def test_04_close_door(self):
        """Test that the elevator can properly close its door"""
        # Test Case 1: self.state=stopped_door_opened
        self.elevator.state = ElevatorState.stopped_door_opened
        self.elevator.close_door()
        self.assertEqual(self.elevator.state, ElevatorState.stopped_closing_door)

        # Test Case 2: self.state=stopped_door_closed
        self.elevator.reset()
        self.elevator.state = ElevatorState.stopped_door_closed
        self.elevator.close_door()
        self.assertEqual(self.elevator.state, ElevatorState.stopped_door_closed)

        # Test Case 3: self.state=up
        self.elevator.reset()
        self.elevator.state = ElevatorState.up
        self.elevator.close_door()
        self.assertEqual(self.elevator.state, ElevatorState.up)

        # Test Case 4: self.state=stopped_opening_door
        self.elevator.reset()
        self.elevator.state = ElevatorState.stopped_opening_door
        self.elevator.close_door()
        self.assertEqual(self.elevator.state, ElevatorState.stopped_opening_door)

    def test_05_update_destination(self):
        """Test that the elevator updates its destination correctly"""

        #  Test Case 1:
        #  self.current_floor=3, self.direction = Direction.DOWN
        #  self.destination_floors=[(3, Direction.DOWN, 0), (2, Direction.IDLE, 0)]
        #  self.active_requests = {(3, Direction.DOWN)}:  TC1, TC2, TC3, TC5
        self.elevator.current_floor = 3
        self.elevator.direction = Direction.DOWN
        self.elevator.destination_floors = [(3, Direction.DOWN, 0), (2, Direction.IDLE, 0)]
        self.elevator.active_requests.add((3, Direction.DOWN))
        self.elevator.update_destination()
        self.assertEqual(len(self.elevator.destination_floors), 1)
        self.assertEqual(self.elevator.destination_floors[0][0], 2)
        self.assertEqual(len(self.elevator.active_requests), 0)

        #  Test Case 2:
        #  self.current_floor=2  self.direction = Direction.DOWN
        #  self.destination_floors=[(2, Direction.UP, 0), (2, Direction.DOWN, 0)]
        #  self.active_requests = {(2, Direction.DOWN),(2,Direction.UP)}:  TC1, TC3, TC4,TC5 TC6
        self.elevator.current_floor = 2
        self.elevator.direction = Direction.DOWN
        self.elevator.destination_floors = [(2, Direction.UP, 0), (2, Direction.DOWN, 0)]
        self.elevator.active_requests.add((2, Direction.DOWN))
        self.elevator.active_requests.add((2, Direction.UP))
        self.elevator.update_destination()
        self.assertEqual(len(self.elevator.destination_floors), 1)
        self.assertEqual(self.elevator.destination_floors[0][0], 2)
        self.assertEqual(self.elevator.destination_floors[0][1], Direction.UP)
        self.assertEqual(len(self.elevator.active_requests), 1)
        self.assertIn((2, Direction.UP), self.elevator.active_requests)

    def test_06_reset(self):
        self.elevator.reset()
        self.assertEqual(self.elevator.current_floor, 1)
        self.assertEqual(self.elevator.direction, Direction.IDLE)
        self.assertEqual(len(self.elevator.destination_floors), 0)
        self.assertEqual(len(self.elevator.active_requests), 0)
        self.assertEqual(self.elevator.finished, True)
        self.assertEqual(self.elevator.car, [1.0, 0.0])
        self.assertEqual(self.elevator.running, True)
        self.assertEqual(self.elevator.state, ElevatorState.stopped_door_closed)
        self.assertEqual(self.elevator.serverMessage, "")
        self.assertEqual(self.elevator.current_floor, 1)

    def test_07_move_api(self):
        """Test the move_api method of the elevator"""
        # Start the elevator thread
        #  Test Case 1: 初始状态无目标楼层 (覆盖基础分支)
        #  : TC2, TC4, TC6, TC14, TC20, TC22, TC24, TC32, TC42, TC60, TC74, TC82
        self.elevator.reset()
        self.elevator_thread = threading.Thread(target=self.elevator.move_api)
        self.elevator_thread.daemon = True
        self.elevator_thread.start()
        while not self.elevator.finished:
            continue
        self.elevator.running = False
        self.assertEqual(self.elevator.state, ElevatorState.stopped_door_closed)
        time.sleep(0.1)


        #  Test Case 2: 地下层特殊处理 (覆盖-1 逻辑)
        #  : TC1, TC5, TC13, TC19, TC21, TC25, TC28
        self.elevator.reset()
        self.current_floor = 0 
        self.destination_floors = [(-1, Direction.UP, 0)]
        self.state = ElevatorState.stopped_door_closed
        self.elevator_thread = threading.Thread(target=self.elevator.move_api)
        self.elevator_thread.daemon = True
        self.elevator_thread.start()
        while not self.elevator.finished:
            continue
        self.elevator.running = False
        self.assertEqual(self.elevator.state, ElevatorState.stopped_door_closed)

        #  Test Case 3: 顶层特殊处理+方向转换
        #  : TC3, TC7, TC9, TC11, TC15, TC17, TC23, TC26, TC27, TC29
        self.elevator.reset()
        self.current_floor = 3
        self.destination_floors = [(2, Direction.DOWN, 0), (1, Direction.UP, 0)]
        self.state = ElevatorState.stopped_door_closed
        self.elevator_thread = threading.Thread(target=self.elevator.move_api)
        self.elevator_thread.daemon = True
        self.elevator_thread.start()
        while not self.elevator.finished:
            continue
        self.elevator.running = False
        self.assertEqual(self.elevator.state, ElevatorState.stopped_door_closed)

        # Test Case 4: 精确楼层到达检测
        # : TC8, TC10, TC12, TC16, TC18, TC30, TC75, TC79
        self.elevator.reset()
        self.current_floor = 1
        self.destination_floors = [(2, Direction.IDLE, 0)]
        self.state = ElevatorState.up
        self.car = [1.49, 0.0] # 即将到达
        self.elevator_thread = threading.Thread(target=self.elevator.move_api)
        self.elevator_thread.daemon = True
        self.elevator_thread.start()
        while not self.elevator.finished:
            continue
        self.elevator.running = False
        self.assertEqual(self.elevator.state, ElevatorState.stopped_door_closed)

        #  Test Case 5: 开门过程+新请求插入
        #  : TC31, TC33, TC35, TC37, TC39, TC40, TC43
        self.elevator.reset()
        self.current_floor = 2
        self.destination_floors = [(2, Direction.UP, 0)]
        self.state = ElevatorState.stopped_opening_door
        self.car = [2.0, 0.9]
        self.elevator_thread = threading.Thread(target=self.elevator.move_api)
        self.elevator_thread.daemon = True
        self.elevator_thread.start()
        while not self.elevator.finished:
            continue
        self.elevator.running = False
        self.assertEqual(self.elevator.state, ElevatorState.stopped_door_closed)

        #  Test Case 6: 关门中断(新请求)
        #  : TC41, TC44, TC45, TC49, TC51, TC53, TC55, TC57
        self.elevator.reset()
        self.current_floor = 1
        self.destination_floors = [(1, Direction.DOWN, 0)]
        self.state = ElevatorState.stopped_closing_door
        self.car = [1.0, 0.1]
        self.elevator_thread = threading.Thread(target=self.elevator.move_api)
        self.elevator_thread.daemon = True
        self.elevator_thread.start()
        while not self.elevator.finished:
            continue
        self.elevator.running = False
        self.assertEqual(self.elevator.state, ElevatorState.stopped_door_closed)

        #  Test Case 7: 完全关门
        #  : TC46, TC48, TC50, TC52, TC54, TC56, TC58
        self.elevator.reset()
        self.current_floor = 2
        self.destination_floors = []
        self.state = ElevatorState.stopped_closing_door
        self.car = [2.0, 0.0]
        self.elevator_thread = threading.Thread(target=self.elevator.move_api)
        self.elevator_thread.daemon = True
        self.elevator_thread.start()
        while not self.elevator.finished:
            continue
        self.elevator.running = False
        self.assertEqual(self.elevator.state, ElevatorState.stopped_door_closed)

        #  Test Case 8: 门全开状态
        #  : TC59, TC61, TC63, TC65, TC67, TC69, TC71
        self.elevator.reset()
        self.current_floor = 3
        self.destination_floors = [(3, Direction.DOWN, 0)]
        self.state = ElevatorState.stopped_door_opened
        self.remain_open_time = 1.5
        self.elevator_thread = threading.Thread(target=self.elevator.move_api)
        self.elevator_thread.daemon = True
        self.elevator_thread.start()
        while not self.elevator.finished:
            continue
        self.elevator.running = False
        self.assertEqual(self.elevator.state, ElevatorState.stopped_door_closed)

        #  Test Case 9: 上升运动+楼层计数
        #  : TC73, TC76, TC77, TC80
        self.elevator.reset()
        self.current_floor = 1
        self.destination_floors = [(2, Direction.UP, 0)]
        self.state = ElevatorState.up
        self.car = [1.1, 0.0]
        self.elevator_thread = threading.Thread(target=self.elevator.move_api)
        self.elevator_thread.daemon = True
        self.elevator_thread.start()
        while not self.elevator.finished:
            continue
        self.elevator.running = False
        self.assertEqual(self.elevator.state, ElevatorState.stopped_door_closed)

        #  Test Case 10: 下降运动+精确停止
        #  : TC81, TC83, TC85, TC87
        self.elevator.reset()
        self.current_floor = 2
        self.destination_floors = [(1, Direction.DOWN, 0)]
        self.state = ElevatorState.down
        self.car = [1.1, 0.0]
        self.elevator_thread = threading.Thread(target=self.elevator.move_api)
        self.elevator_thread.daemon = True
        self.elevator_thread.start()
        while not self.elevator.finished:
            continue
        self.elevator.running = False
        self.assertEqual(self.elevator.state, ElevatorState.stopped_door_closed)

        #  Test Case 11: 空闲状态完成
        #  : TC34, TC36, TC38, TC47, TC62, TC64, TC66, TC68, TC70, TC72
        self.elevator.reset()
        self.current_floor = 0
        self.destination_floors = []
        self.state = ElevatorState.stopped_door_opened
        self.finished = True
        self.remain_open_time = 0
        self.elevator_thread = threading.Thread(target=self.elevator.move_api)
        self.elevator_thread.daemon = True
        self.elevator_thread.start()
        while not self.elevator.finished:
            continue
        self.elevator.running = False
        self.assertEqual(self.elevator.state, ElevatorState.stopped_door_closed)

        #  Test Case 12: 楼层精确匹配检测
        #  : TC78, TC84, TC86, TC88
        self.elevator.reset()
        self.current_floor = 1
        self.destination_floors = [(1, Direction.IDLE, 0)]
        self.state = ElevatorState.down
        self.car = [1.3, 0.0]
        self.elevator_thread = threading.Thread(target=self.elevator.move_api)
        self.elevator_thread.daemon = True
        self.elevator_thread.start()
        while not self.elevator.finished:
            continue
        self.elevator.running = False
        self.assertEqual(self.elevator.state, ElevatorState.stopped_door_closed)



if __name__ == '__main__':
    unittest.main()
