# common workflows

## 1 outside the elevator
1.1 at floor 1, 2 outside the elevator, standard user operations includes: press up and down buttons to call the elevator. 

1.2 at floor -1 outside the elevator, standard user operations includes: press up button to call the elevator.

1.3 at floor 3 outside the elevator, standard user operations includes: press down button to call the elevator.

when the elevator is openning at the current floor of the user, pressing the call button the has the same direction with the elevator's direction will do nothiing;

when the elevator is opened at the current floor of the user, pressing the call button the has the same direction with the elevator's direction will reset the remain open time and the elevator will remain open for the default time.

when the elevator is closing at the current floor of the user, pressing the call button the has the same direction with the elevator's direction will make the elevator be openning again.

when the elevator has closed and there exists inside call, the elevator will deal with the call. And the outside call will be sheduled until there exists any elevator that can deal with the call (IDLE or on the way)


## 2 inside the elevator

In both elevators, standard user operations includes:

2.1 press the floor buttons (-1, 1, 2, 3) to go to the desired floor.

2.2 press the open button to open the door. 

2.3 press the close button to close the door. 

press the floor buttons will add the call to the elevator's destination list and the elevator will shedule it.

when the elevator is going up or down, pressing the open and close button will do nothing.

when the elevator is openning, pressing the open and close button will not influence the elevator's state.

when the elevator is closing, pressing the open button will make the elevator be openning again, pressing the close button will do nothing.

when the elevator is opened, pressing the open button will reset the remain open time and the elevator will remain open for the default time; pressing the close 
button will make the elevator be closing.

when the elevator is closed pressing the open button will make the elevator be openning; pressing the close button will do nothing.

# Rare workflows


## Risks

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
