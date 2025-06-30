~~~python
    def add_destination(self, floor, is_external_call=Direction.IDLE, pri=0.0):
        # 1,2
        if floor == -1:
            floor = 0
        existing = [f for f in self.destination_floors if f[0]
                    == floor and f[1] == is_external_call]
        # 3,4
        if not existing and (0 <= floor <= self.max_floor or floor == -1):
            self.destination_floors.append([int(floor), is_external_call, pri])
            # 5,6
            if self.currentDestination is None:
                self.currentDestination = self.destination_floors[0]
                # 7,8
                if self.state == ElevatorState.stopped_door_closed:
                    # 9,10
                    if self.currentDestination[0] > self.current_floor:
                        self.state = ElevatorState.up
                        self.direction = Direction.UP
                    # 11, 12
                    elif self.currentDestination[0] < self.current_floor:
                        self.state = ElevatorState.down
                        self.direction = Direction.DOWN
            self.destination_floors.sort(key=lambda x: (x[2], x[0]))
            # 13,14
            if is_external_call != Direction.IDLE:
                self.active_requests.add((int(floor), is_external_call))
~~~
Valid:
TC1: 0<=floor<=3
TC2: -1<=is_external_call<=1

Invalid:
TC3: floor<0
TC4: floor>3
TC5: is_external_call< -1
TC6: is_external_call> 1
TC7: non-integer floor
TC8: non-integer is_external_call

