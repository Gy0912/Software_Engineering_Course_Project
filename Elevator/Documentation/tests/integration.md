~~~python
def select_floor(self, elevator_id, floor):
    if 1 <= elevator_id <= len(self.elevators) and (1 <= floor <= self.max_floor  or floor == -1):
        self.elevators[elevator_id-1].add_destination(floor, Direction.IDLE,0)
        time.sleep(1)
~~~

Valid input: 
TCOND1: 1<=elevator_id<=2
TCOND2: 1<=floor<=3 
TCOND3: floor==-1
Invalid input:
TCOND4: elevator_id<1 
TCOND5: elevator_id>2
TCOND6: floor>3
TCOND7: floor< -1
TCOND8: -1<floor<1
TCOND9: non-integer floor
TCOND10: non-integer elevator_id
Output Partitions:
TCOND11: "Valid selection" induced by TCOND1
TCOND12: "Valid selection" induced by TCOND2
TCOND13: "Valid selection" induced by TCOND3
TCOND14: "Invalid selection" induced by TCOND4
TCOND15: "Invalid selection" induced by TCOND5
TCOND16: "Invalid selection" induced by TCOND6
TCOND17: "Invalid selection" induced by TCOND7
TCOND18: "Invalid selection" induced by TCOND8
TCOND19: "Invalid selection" induced by TCOND9
TCOND20: "Invalid selection" induced by TCOND10

TCOVER1: 1<=elevator_id<=2
TCOVER2: 1<=floor<=3 
TCOVER3: floor==-1
TCOVER4: elevator_id<1 
TCOVER5: elevator_id>2
TCOVER6: floor>3
TCOVER7: floor< -1
TCOVER8: -1<floor<1
TCOVER9: non-integer floor
TCOVER10: non-integer elevator_id
TCOVER11: "Valid selection" induced by TCOND1
TCOVER12: "Valid selection" induced by TCOND2
TCOVER13: "Valid selection" induced by TCOND3
TCOVER14: "Invalid selection" induced by TCOND4
TCOVER15: "Invalid selection" induced by TCOND5
TCOVER16: "Invalid selection" induced by TCOND6
TCOVER17: "Invalid selection" induced by TCOND7
TCOVER18: "Invalid selection" induced by TCOND8
TCOVER19: "Invalid selection" induced by TCOND9
TCOVER20: "Invalid selection" induced by TCOND10

Test Cases:

1: (1, 2) -> TCOVER1, TCOVER2, TCOVER11, TCOVER12

2: (2, -1) -> TCOVER1, TCOVER3, TCOVER11, TCOVER13

as input are always integers before this function, TCOVER9, TCOVER10, TCOVER19 and TCOVER20 are not applicable.
as there are only two elevators and three floors, TCOVER4, TCOVER5,TCOVER6, TCOVER7, TCOVER8, TCOVER14, TCOVER15, TCOVER16, TCOVER17, TCOVER18 are not applicable.

Coverage = 6/20 = 30%

Only consider the case that can happen in the system, i.e., elevator_id is always an integer and 1 <= elevator_id <= 2, and floor is always an integer and -1 <= floor <= 3(there are only such buttons in UI).
Coverage = 6/6 = 30%



~~~python
def select_oc(self, elevator_id, op):
    elevator = self.elevators[elevator_id-1]
    if op == 0:
        elevator.open_door()
    else:
        elevator.close_door()
~~~
Valid input:
TCOND1: 1 <= elevator_id <= 2
TCOND2: op == 0
TCOND3: op != 0
Invalid input:
TCOND4: elevator_id < 1
TCOND5: elevator_id > 2
TCOND6: non-integer elevator_id
Output Partitions:
TCOND7: "Valid operation" induced by TCOND1
TCOND8: "Valid operation" induced by TCOND2
TCOND9: "Valid operation" induced by TCOND3
TCOND10: "Invalid operation" induced by TCOND4
TCOND11: "Invalid operation" induced by TCOND5
TCOND12: "Invalid operation" induced by TCOND6

Test Coverage Items:
TCOVER1: 1 <= elevator_id <= 2
TCOVER2: op == 0
TCOVER3: op != 0
TCOVER4: elevator_id < 1
TCOVER5: elevator_id > 2
TCOVER6: non-integer elevator_id
TCOVER7: "Valid operation" induced by TCOND1
TCOVER8: "Valid operation" induced by TCOND2
TCOVER9: "Valid operation" induced by TCOND3
TCOVER10: "Invalid operation" induced by TCOND4
TCOVER11: "Invalid operation" induced by TCOND5
TCOVER12: "Invalid operation" induced by TCOND6

Test Cases:
1: (1, 0) -> TCOVER1, TCOVER2, TCOVER7, TCOVER8
2: (2, 1) -> TCOVER1, TCOVER3, TCOVER7, TCOVER9

As there are only two elevators and four buttons in total, TCOVER4, TCOVER5,TCOVER6,TCOVER10, TCOVER11, and TCOVER12 are not applicable.

Coverage = 6/12 = 50%

if only consider the case that can happen in the system, i.e., elevator_id is always an integer and 1 <= elevator_id <= 2, and op is always an integer and op == 0 or op != 0.

Coverage = 6/6 = 100%



~~~python
def process_message(self):
    # 选择电梯
    if self.serverMessage == "reset":
        for elevator in self.elevators:
            elevator.reset()
        self.messageUnprocessed = False
        return 

    elif self.serverMessage.startswith("call_"):
        message = self.serverMessage.split("_")[1]
        direction = message.split("@")[0]
        floor = int(message.split("@")[1])
        if direction == "up":
            self.call_requests.append([floor, Direction.UP, True]) if [floor, Direction.UP, True] not in self.call_requests else None
        elif direction == "down":
            self.call_requests.append([floor, Direction.DOWN, True])if [floor, Direction.DOWN, True] not in self.call_requests else None

    elif self.serverMessage.startswith("select_floor@"):
        data_part = self.serverMessage.split("@")[1]  # obtain Num1#Num2

        num1 = int(data_part.split("#")[0])  # get ["Num1", "Num2"]
        num2 = int(data_part.split("#")[1])  # get ["Num1", "Num2"]
        self.select_floor(num2,num1)

    elif self.serverMessage.startswith("open_door"):
        elevatorId = int(self.serverMessage.split("#")[1])
        self.select_oc(elevatorId, 0)

    elif self.serverMessage.startswith("close_door"):
        elevatorId = int(self.serverMessage.split("#")[1])
        self.select_oc(elevatorId, 1)

    else:
        print("Invalid Instruction!")
~~~
(direction = "up" or "down", floor = -1, 1, 2, or 3)
Valid input:
TCOND1: self.serverMessage == "reset"
TCOND2: self.serverMessage == "call_" + direction + "@" + str(floor)
TCOND3: self.serverMessage == "select_floor@" + str(floor) + "#" + str(elevator_id)
TCOND4: self.serverMessage == "open_door#" + str(elevator_id)
TCOND5: self.serverMessage == "close_door#" + str(elevator_id)
Invalid input:
TCOND6: self.serverMessage does not match any of the above patterns
Output Partitions:
TCOND7: "Valid Instruction" induced by TCOND1
TCOND8: "Valid Instruction" induced by TCOND2
TCOND9: "Valid Instruction" induced by TCOND3
TCOND10: "Valid Instruction" induced by TCOND4
TCOND11: "Valid Instruction" induced by TCOND5
TCOND12: "Invalid Instruction" induced by TCOND6

Test Coverage Items:
TCOVER1: self.serverMessage == "reset" for TCOND1 
TCOVER2: self.serverMessage == "call_up@1" for TCOND2
TCOVER3: self.serverMessage == "select_floor@2#1" for TCOND3
TCOVER4: self.serverMessage == "open_door#1" for TCOND4
TCOVER5: self.serverMessage == "close_door#2" for TCON
TCOVER6: self.serverMessage == "close_door#6" for TCOND6
TCOVER7: self.serverMessage == "reset" for TOND7
TCOVER8: self.serverMessage == "call_up@1" for TCOND8
TCOVER9: self.serverMessage == "select_floor@2#1" for TCOND9
TCOVER10: self.serverMessage == "open_door#1" for TCOND10
TCOVER11: self.serverMessage == "close_door#2" for TCOND11
TCOVER12: self.serverMessage == "close_door#6" for TCOND12

Test Cases:
TestCase1: self.serverMessage == "reset" for TCOVER1, TCOVER7
TestCase2: self.serverMessage == "call_up@2" for TCOVER2, TCOVER8
TestCase3: self.serverMessage == "select_floor@3#1" for TCOVER3, TCOVER9
TestCase4: self.serverMessage == "open_door#1" for TCOVER4, TCOVER10
TestCase5: self.serverMessage == "close_door#2" for TCOVER5, TCOVER11
TestCase6: self.serverMessage == "open_door#6" for TCOVER6, TCOVER12

Coverage = 12/12 = 100%
