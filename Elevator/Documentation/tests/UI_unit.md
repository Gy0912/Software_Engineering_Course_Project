~~~python
def highlight_floor_button(self, floor, highlight=True):
    # 12
    if floor in self.floor_buttons:
        btn = self.floor_buttons[floor]
        # 34
        if highlight:
            btn.setStyleSheet("background-color: #FFA500; font-weight: bold;")
        else:
            btn.setStyleSheet("")  # Reset to default
~~~
TC1: floor in self.floor_buttons -> True
TC2: floor in self.floor_buttons -> False
TC3: highlight -> True
TC4: highlight -> False

TestCases:
1: (1, True) : TC1 TC3
2: (1, False) : TC1 TC4
3: (8, True) : TC2

~~~python
def update_state(self, state, direction=0):
    self.state = state
    self.direction = direction

    direction = int(direction) if direction is not None else 0
    # 12
    if direction == 1:  # Up
        direction_symbol = "↑"
        color = "green"
    # 34
    elif direction == -1:  # Down
        direction_symbol = "↓"
        color = "red"
    else:  # Idle
        direction_symbol = "■"
        color = "gray"

    # Update direction display
    self.direction_display.setText(direction_symbol)
    self.direction_display.setStyleSheet(f"color: {color};")
~~~
TC1: direction == 1 -> True
TC2: direction == 1 -> False
TC3: direction == -1 -> True
TC4: direction == -1 -> True

TestCases:
1: (1, 1)
2: (1, -1)
3: (1, 0)

~~~python
def highlight_call_button(self, floor, direction, highlight=True):
    """Highlight external call buttons"""
    # 12
    if direction == 1 and floor in self.up_buttons:
        btn = self.up_buttons[floor]
    # 34
    elif direction == -1 and floor in self.down_buttons:
        btn = self.down_buttons[floor]
    else:
        return

    # 56
    if highlight:
        btn.setStyleSheet("background-color: #FFA500; font-weight: bold;")
    else:
        btn.setStyleSheet("")  # Reset to default
~~~

TC1: direction == 1 and floor in self.up_buttons -> True        
TC2: direction == 1 and floor in self.up_buttons -> False       
TC3: direction == -1 and floor in self.down_buttons -> True     
TC4: direction == -1 and floor in self.down_buttons -> False        
TC5: highlight -> True      
TC6: highlight -> False     

TestCases:
1: (1, 1, True) -> TC1, TC5
2: (-1, 1, False) -> TC2, TC3, TC6
2: (-1, -1, True) -> TC2, TC4

~~~python

def update_button_highlights(self):
    # Reset all button highlights
    for floor in self.up_buttons:
        self.highlight_call_button(floor, 1, False)
    for floor in self.down_buttons:
        self.highlight_call_button(floor, -1, False)
    for elevator_ui in self.elevators:
        for floor in elevator_ui.floor_buttons:
            elevator_ui.highlight_floor_button(floor, False)

    # Highlight based on current destinations and requests

    # Highlight external calls
        for elevator in self.elevator_system.elevators:
            for floor, direction in self.elevator_system.active_requests:
                self.highlight_call_button(floor, direction.value, True)
            for floor, direction in elevator.active_requests:
                self.highlight_call_button(floor, direction.value, True)


    # Highlight internal selections
    for i in range(self.num_elevators):
        elevator = self.elevator_system.elevators[i]
        for dest in elevator.destination_floors:
            #1 2
            if dest[1] == Direction.IDLE:
                self.elevators[i].highlight_floor_button(dest[0], True)
~~~

TC1: dest[1] == IDLE -> True
TC2: dest[2] == IDLE -> False

TestCases:

1: elevator_system.elevators[0].destination_floors[0] = [(1, Direction.IDLE,0)] -> TC1
2: elevator_system.elevators[0].destination_floors[0] = [(1, Direction.UP,0)] -> TC2

~~~python
def handle_door_command(self, elevator_id, command):
    cmd = "open_door" if command == 0 else "close_door"
    self.elevator_system.zmqthread.receivedmessage = f"{cmd}#{elevator_id}"
    self.elevator_system.zmqthread.messagetimestamp = time.time()
~~~

TC1: command == 0 -> True 
TC2: command == 0 -> False

TestCases:
1: (1, 0)
2: (2, 1)

~~~python
def update_ui_from_system(self):
    for i, elevator in enumerate(self.elevator_system.elevators):
        # Update floor position
        self.elevators[i].update_position(elevator.car)
        self.elevators[i].floor_display.setText(str(elevator.current_floor)if elevator.current_floor != 0 else "-1")

        # Update state and direction
        state = elevator.state
        direction = elevator.direction.value if hasattr(elevator.direction, 'value') else 0
        self.elevators[i].update_state(state, direction)

        # Update the displays in the call panel
        floor_display = getattr(self, f'elevator_{i+1}_floor{j}')
        direction_display = getattr(self, f'elevator_{i+1}_direction{j}')

        # Set floor display
        # 1 2
        floor_str = "-1" if elevator.current_floor == 0 else str(elevator.current_floor)
        floor_display.setText(floor_str)

        # Set direction display
        # 3 4
        if direction == 1:
            direction_display.setText("▲")
            direction_display.setStyleSheet("color: green;")
        # 5 6
        elif direction == -1:
            direction_display.setText("▼")
            direction_display.setStyleSheet("color: red;")
        else:
            direction_display.setText("■")
            direction_display.setStyleSheet("color: gray;")
    self.update_button_highlights()
~~~

TC1: elevator.current_floor == 0 -> True
TC2: elevator.current_floor == 0 -> False
TC3: direction == 1 -> True
TC4: direction == 1 -> False
TC5: direction == -1 -> True
TC6: direction == -1 -> False

TestCases:
1: elevators[0].direction = 1; elevators[1].direction = -1; elevators[0].current_floor = 0, elevators[1].current_floor = 0 -> TC 1, TC3, TC4, TC5
2: elevators[0].direction = 0; elevators[1].direction = 0; elevators[0].current_floor = 1, elevators[1].current_floor = 1 -> TC2, Tc4， TC6
