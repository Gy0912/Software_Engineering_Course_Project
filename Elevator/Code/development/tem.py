#  import sys
#  from elevator import ElevatorState, Direction
#  import time
#  from PyQt6.QtWidgets import (
#      QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
#      QLabel, QPushButton, QFrame, QGridLayout
#  )
#  from PyQt6.QtCore import Qt, QTimer, pyqtSignal
#  from PyQt6.QtGui import QColor, QPainter, QPen, QFont
#
#  class ElevatorUI(QWidget):
#      floor_changed = pyqtSignal(int, int)  # elevator_id, floor
#      state_changed = pyqtSignal(int, int)  # elevator_id, state (0=open, 1=close)
#
#      def __init__(self, elevator_id, max_floors=4):
#          super().__init__()
#          self.elevator_id = elevator_id
#          self.max_floors = max_floors
#          self.current_floor = -1
#          self.state = ElevatorState.stopped_door_closed  # stopped_door_closed
#          self.direction = 0  # IDLE
#          self.floor_buttons = {}
#          self.init_ui()
#
#      def init_ui(self):
#          self.setFixedSize(200, 500)
#          self.setWindowTitle(f'Elevator {self.elevator_id}')
#
#          main_layout = QVBoxLayout()
#          self.setLayout(main_layout)
#
#          # Elevator shaft visualization
#          self.shaft = QFrame()
#          self.shaft.setFrameShape(QFrame.Shape.Box)
#          self.shaft.setLineWidth(2)
#          self.shaft.setFixedSize(150, 350)
#
#          # Create grid layout for floors
#          grid = QGridLayout(self.shaft)
#          grid.setSpacing(0)
#          grid.setContentsMargins(0, 0, 0, 0)
#
#          # Create floor rectangles
#          self.floor_widgets = []
#          for i in range(self.max_floors, -2, -1):  # Top to bottom, including -1
#              floor = QFrame()
#              floor.setFrameShape(QFrame.Shape.Box)
#              floor.setLineWidth(1)
#              floor.setFixedHeight(350 // (self.max_floors + 1))
#              grid.addWidget(floor, self.max_floors - i, 0)
#              self.floor_widgets.append(floor)
#
#          # Elevator car (initially at floor -1)
#          self.car = QLabel()
#          self.car.setFixedSize(140, (350 // (self.max_floors + 1)) - 10)
#          self.car.setStyleSheet("background-color: #4682B4; border: 2px solid #1E3F66;")
#          grid.addWidget(self.car, self.max_floors + 1, 0, Qt.AlignmentFlag.AlignCenter)
#
#          main_layout.addWidget(self.shaft)
#
#          # Status display
#          status_layout = QHBoxLayout()
#
#          self.status_label = QLabel("IDLE")
#          self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#          self.status_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
#          status_layout.addWidget(self.status_label)
#
#          self.floor_label = QLabel("Floor: -1")
#          self.floor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#          status_layout.addWidget(self.floor_label)
#
#          main_layout.addLayout(status_layout)
#
#          # Control buttons
#          control_layout = QHBoxLayout()
#
#          self.open_btn = QPushButton("Open")
#          self.open_btn.clicked.connect(lambda: self.open_door())
#          control_layout.addWidget(self.open_btn)
#
#          self.close_btn = QPushButton("Close")
#          self.close_btn.clicked.connect(lambda: self.close_door())
#          control_layout.addWidget(self.close_btn)
#
#          main_layout.addLayout(control_layout)
#
#          # Floor buttons
#          floor_btn_layout = QGridLayout()
#
#          for i in range(self.max_floors + 1):
#              floor_num = self.max_floors - i
#              btn = QPushButton(str(floor_num) if floor_num >= 0 else "-1")
#              btn.clicked.connect(self.create_floor_handler(floor_num))
#              floor_btn_layout.addWidget(btn, i, 0)
#              self.floor_buttons[floor_num] = btn
#
#          main_layout.addLayout(floor_btn_layout)
#
#      def create_floor_handler(self, floor):
#          def handler():
#              self.floor_changed.emit(self.elevator_id, floor)
#          return handler
#
#      def update_position(self, floor):
#          if -1 <= floor <= self.max_floors:
#              self.current_floor = floor
#              self.floor_label.setText(f"Floor: {floor}")
#
#              # Move the car visually
#              grid = self.shaft.layout()
#              grid.removeWidget(self.car)
#              grid.addWidget(self.car, self.max_floors - floor, 0, Qt.AlignmentFlag.AlignCenter)
#              self.car.show()
#
#      def highlight_floor_button(self, floor, highlight=True):
#          if floor in self.floor_buttons:
#              btn = self.floor_buttons[floor]
#              if highlight:
#                  btn.setStyleSheet("background-color: #FFA500; font-weight: bold;")
#              else:
#                  btn.setStyleSheet("")  # 恢复默认样式
#
#      def update_state(self, state, direction=0):
#          self.state = state
#          self.direction = direction
#
#          states = {
#              0: "GOING UP",
#              1: "GOING DOWN",
#              2: "STOPPED (Closed)",
#              3: "STOPPED (Open)",
#              4: "OPENING"
#          }
#
#          directions = {
#              1: "↑",
#              -1: "↓",
#              0: ""
#          }
#
#          #  self.status_label.setText(f"{states[state]} {directions[direction]}")
#
#          # Update car color based on state
#          if state == 3:  # door open
#              self.car.setStyleSheet("background-color: #90EE90; border: 2px solid #1E3F66;")
#          elif state == 4:  # opening door
#              self.car.setStyleSheet("background-color: #FFA07A; border: 2px solid #1E3F66;")
#          else:
#              self.car.setStyleSheet("background-color: #4682B4; border: 2px solid #1E3F66;")
#
#      def open_door(self):
#          if self.state == 2:  # Can only open from closed state
#              self.state_changed.emit(self.elevator_id, 0)  # 0 for open
#
#      def close_door(self):
#          if self.state == 3:  # Can only close from open state
#              self.state_changed.emit(self.elevator_id, 1)  # 1 for close
#
#  class ElevatorSystemUI(QMainWindow):
#      def __init__(self, elevator_system, num_elevators=2, max_floors=4):
#          super().__init__()
#          self.elevator_system = elevator_system
#          self.num_elevators = num_elevators
#          self.max_floors = max_floors
#          self.elevators = []
#          self.up_buttons = {}
#          self.down_buttons = {}
#
#          self.init_ui()
#
#
#          # Setup timer to periodically check elevator states
#          self.update_timer = QTimer()
#          self.update_timer.timeout.connect(self.update_ui_from_system)
#          self.update_timer.start(100)  # Update every 100ms
#
#      def init_ui(self):
#          self.setWindowTitle('Elevator Control System')
#          self.setGeometry(100, 100, 200 * self.num_elevators + 150, 600)
#
#          central_widget = QWidget()
#          self.setCentralWidget(central_widget)
#
#          main_layout = QHBoxLayout()
#          central_widget.setLayout(main_layout)
#
#          # Create elevator UIs
#          for i in range(self.num_elevators):
#              elevator = ElevatorUI(i+1, self.max_floors)
#              elevator.floor_changed.connect(self.handle_floor_request)
#              elevator.state_changed.connect(self.handle_door_command)
#              main_layout.addWidget(elevator)
#              self.elevators.append(elevator)
#
#          # Call panel
#          call_panel = QFrame()
#          call_panel.setFrameShape(QFrame.Shape.Box)
#          call_panel.setLineWidth(2)
#          call_panel.setFixedWidth(150)
#
#          call_layout = QVBoxLayout()
#          call_panel.setLayout(call_layout)
#
#          call_label = QLabel("External Calls")
#          call_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#          call_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
#          call_layout.addWidget(call_label)
#
#          # Up buttons
#          up_group = QFrame()
#          up_layout = QVBoxLayout()
#          up_group.setLayout(up_layout)
#
#          up_label = QLabel("Up")
#          up_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#          up_layout.addWidget(up_label)
#
#          for floor in range(self.max_floors, -2, -1):
#              if floor != self.max_floors:  # No up button on top floor
#                  btn = QPushButton(f"{floor} ▲" if floor >= 0 else "-1 ▲")
#                  btn.clicked.connect(self.create_call_handler(floor, 1))  # 1 for up
#                  up_layout.addWidget(btn)
#                  self.up_buttons[floor] = btn
#
#          call_layout.addWidget(up_group)
#
#          # Down buttons
#          down_group = QFrame()
#          down_layout = QVBoxLayout()
#          down_group.setLayout(down_layout)
#
#          down_label = QLabel("Down")
#          down_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#          down_layout.addWidget(down_label)
#
#          for floor in range(self.max_floors, -2, -1):
#              if floor != -1:  # No down button on bottom floor
#                  btn = QPushButton(f"{floor} ▼" if floor >= 0 else "-1 ▼")
#                  btn.clicked.connect(self.create_call_handler(floor, -1))  # -1 for down
#                  down_layout.addWidget(btn)
#                  self.down_buttons[floor] = btn
#
#          call_layout.addWidget(down_group)
#
#          # Emergency button
#          emergency_btn = QPushButton("EMERGENCY STOP")
#          emergency_btn.setStyleSheet("background-color: red; color: white; font-weight: bold;")
#          emergency_btn.clicked.connect(self.emergency_stop)
#          call_layout.addWidget(emergency_btn)
#
#          # Reset button
#          reset_btn = QPushButton("Reset System")
#          reset_btn.clicked.connect(self.reset_system)
#          call_layout.addWidget(reset_btn)
#
#          call_layout.addStretch()
#
#          main_layout.addWidget(call_panel)
#
#      def highlight_call_button(self, floor, direction, highlight=True):
#          """高亮外部呼叫按钮"""
#          if direction == 1 and floor in self.up_buttons:
#              btn = self.up_buttons[floor]
#          elif direction == -1 and floor in self.down_buttons:
#              btn = self.down_buttons[floor]
#          else:
#              return
#
#          if highlight:
#              btn.setStyleSheet("background-color: #FFA500; font-weight: bold;")
#          else:
#              btn.setStyleSheet("")  # 恢复默认样式
#
#      def create_call_handler(self, floor, direction):
#          def handler():
#              direction_str = "up" if direction == 1 else "down"
#              self.elevator_system.zmqThread.receivedMessage = f"call_{direction_str}@{floor}"
#              self.elevator_system.zmqThread.messageTimeStamp = time.time()
#          return handler
#
#      def handle_floor_request(self, elevator_id, floor):
#          self.elevator_system.zmqThread.receivedMessage = f"select_floor@{floor}#{elevator_id}"
#          self.elevator_system.zmqThread.messageTimeStamp = time.time()
#
#      def handle_door_command(self, elevator_id, command):
#          cmd = "open_door" if command == 0 else "close_door"
#          self.elevator_system.zmqThread.receivedMessage = f"{cmd}#{elevator_id}"
#          self.elevator_system.zmqThread.messageTimeStamp = time.time()
#
#      def update_ui_from_system(self):
#              for i, elevator in enumerate(self.elevator_system.elevators):
#                  # 更新楼层
#                  self.elevators[i].update_position(elevator.current_floor)
#
#                  # 更新状态和方向
#                  state = elevator.state
#                  direction = elevator.direction.value if hasattr(elevator.direction, 'value') else 0
#                  self.elevators[i].update_state(state, direction)
#              self.update_button_highlights()
#
#      def update_button_highlights(self):
#          """根据电梯系统状态更新按钮高亮"""
#          # 重置所有按钮高亮
#          for floor in self.up_buttons:
#              self.highlight_call_button(floor, 1, False)
#          for floor in self.down_buttons:
#              self.highlight_call_button(floor, -1, False)
#          for elevator_ui in self.elevators:
#              for floor in elevator_ui.floor_buttons:
#                  elevator_ui.highlight_floor_button(floor, False)
#
#          # 高亮外部呼叫
#          for elevator in self.elevator_system.elevators:
#              for floor, direction in elevator.active_requests:
#                  self.highlight_call_button(floor, direction.value if hasattr(direction, 'value') else direction, True)
#
#          # 高亮内部选择
#          for i in range(2):
#              elevator = self.elevator_system.elevators[i]
#              for dest in elevator.destination_floors:
#                  if dest[1] == Direction.IDLE:
#                      self.elevators[i].highlight_floor_button(dest[0], True)
#
#      def emergency_stop(self):
#          self.elevator_system.zmqThread.receivedMessage = "emergency_stop"
#          self.elevator_system.zmqThread.messageTimeStamp = time.time()
#
#      def reset_system(self):
#          self.elevator_system.zmqThread.receivedMessage = "reset"
#          self.elevator_system.zmqThread.messageTimeStamp = time.time()
#
#  if __name__ == '__main__':
#      # For testing the UI standalone
#      app = QApplication(sys.argv)
#      from main import ElevatorSystem
#      system = ElevatorSystem(num_elevators=2, max_floor=4, identity="TestUI")
#      window = ElevatorSystemUI(system)
#      window.show()
#      sys.exit(app.exec())
print(1)
