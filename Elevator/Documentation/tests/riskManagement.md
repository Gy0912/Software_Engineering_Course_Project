# Risks

1 Elevator may stop at non-integer floors.

- high frequency, catastrophic harm.
- mitigation:
  - In the State transition function of elevator, state "stopped_door_closed" will be reached only when the elevator is at an integer floor.
  - other stop states can only be reached from "stopped_door_closed" state.

2 Door may continue going up after reaching floor 3; or continue going down after reaching floor -1.

- low frequency, catastrophic harm.
- mitigation:
  - check the requests: there will not exist select floor > 3 or select floor < -1 in the request queue.
  - the elevator will not change its current destination to one request floor once it has passed the requested floor.

3 Door may not be open after reaching destination floors if there are passenger pressing close button.

- high frequency, serious harm.
- mitigation:
  - when the elevator reaches a destination floor, it will always be opening the door.
  - When the door is opening, the close button will be ignored.

4 Passenger may press call button many times, and the elevator will serve for them many times.

- high frequency, serious harm.
- mitigation:
  - In the request queue, there will not exist two requests with the same floor and direction (if a new request is already in the queue, ignore it).

5 Two elevators will serve for one request and waste resources.

- high frequency, serious harm.
- mitigation:
  - In the request queue, there will not exist two requests with the same floor and direction.
  - In the sheduling, reqeusts will be ignored if they are already in the destination queue of any elevator.

6 Elevator will never serve for one request and passenger will not enter the elevator.

- low frequency, catastrophic harm.
- mitigation:
  - a request will be saved in the request and never be removed if it has not been served by any elevator.
  - The elevator will always eventually be IDLE after finishing all its destination requests and when there exist IDLE elevator, request will be served by it.

7 Door may open when elevator is moving.

- low frequency, catastrophic harm.
- mitigation:
  - In the Door open function, the door will open only when the elevator is stopped_door_closed or stopped_door_closing.
  - In the State transition function of elevator, state "stopped_door_openning" will be reached only when the elevator is stopped_door_closed or stopped_door_closing.
  - The two methods above ensure that the door will not open when the elevator is moving.

8 When the door is closing, the passenger is trying to enter the elevator, and so be hurt.

- low frequency, catastrophic harm.
- mitigation:
  - the passenger can press the call button to open the door.
  - the people(if exists) can press the open button to open the door.
