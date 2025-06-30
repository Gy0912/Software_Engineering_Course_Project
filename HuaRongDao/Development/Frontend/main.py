import sys
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QMessageBox, QDialog, QDialogButtonBox, QFormLayout)
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer, QRect
from Server import ZmqFrontendServer

class BoardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.board = ['#'] * 20
        self.selected_id = '1'
        self.piece_colors = {
            '0': QColor(150, 150, 255), '1': QColor(255, 200, 200), '2': QColor(200, 255, 200),
            '3': QColor(255, 255, 150), '4': QColor(200, 200, 255), '5': QColor(255, 180, 255),
            '6': QColor(180, 255, 255), '7': QColor(180, 255, 255), '8': QColor(180, 255, 255), '9': QColor(180, 255, 255)
        }
        self.rect_map = {}

    def update_board(self, board_str):
        if len(board_str) == 20:
            self.board = list(board_str)
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        cell_w = self.width() // 4
        cell_h = self.height() // 5
        self.rect_map.clear()
        drawn = set()
        for i in range(20):
            value = self.board[i]
            if value == '#' or value in drawn:
                continue
            drawn.add(value)
            x = (i % 4) * cell_w
            y = (i // 4) * cell_h
            w, h = self.get_piece_span(value)
            rect = QRect(x, y, w * cell_w, h * cell_h)
            self.rect_map[value] = rect
            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(self.piece_colors.get(value, Qt.gray))
            painter.drawRect(rect)
            if value == self.selected_id:
                painter.setBrush(Qt.red)
                cx = rect.center().x()
                cy = rect.center().y()
                painter.drawEllipse(cx - 5, cy - 5, 10, 10)

    def get_piece_span(self, pid):
        if pid == '1': return 2, 2
        elif pid in {'0', '2', '3', '5'}: return 1, 2
        elif pid == '4': return 2, 1
        else: return 1, 1

    def mousePressEvent(self, event):
        pos = event.pos()
        for pid, rect in self.rect_map.items():
            if rect.contains(pos):
                self.selected_id = pid
                self.update()
                break

class LevelDialog(QDialog):
    def __init__(self, callback):
        super().__init__()
        self.setWindowTitle("选择关卡")
        layout = QFormLayout()

        self.levels = {
            "测试关卡": "24432673011501158##9",
            "横刀立马": "01150115244327836##9",
            "指挥若定": "01150115644927832##3",
            "将拥曹营": "#11#0112035263574489",
            "齐头并进": "01120112678934453##5",
            "兵分三路": "61190112044237853##5",
            "雨声淅沥": "01160117244325#385#9",
            "左右布兵": "6117811902350235#44#",
            "桃花园中": "6117011203528359#44#"
        }

        for name, board in self.levels.items():
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, b=board: self.select_level(b, callback))
            layout.addRow(btn)

        self.setLayout(layout)

    def select_level(self, board_str, callback):
        callback(board_str)
        self.accept()

class GameWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("华容道 - 前端")
        self.setGeometry(200, 200, 600, 400)
        self.server = ZmqFrontendServer()
        self.board_widget = BoardWidget()
        self.info_label = QLabel("初始化中...")
        self.timer_label = QLabel("Time: 0s")
        self.step_label = QLabel("Steps: 0")
        self.record_label = QLabel("Best: ∞s / ∞ steps")
        self.elapsed = 0
        self.steps = 0
        self.best_time = float('inf')
        self.best_steps = float('inf')

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        self.init_ui()
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.check_response)
        self.poll_timer.start(100)

        self.current_board = "24432673011501158##9"
        self.server.send_string(f"set@{self.current_board}")

    def init_ui(self):
        move_layout = QGridLayout()
        self.up_btn = QPushButton("↑")
        self.down_btn = QPushButton("↓")
        self.left_btn = QPushButton("←")
        self.right_btn = QPushButton("→")
        self.undo_btn = QPushButton("Undo")
        self.reset_btn = QPushButton("重置")
        self.level_btn = QPushButton("关卡选择")

        self.up_btn.clicked.connect(lambda: self.send_move("Up"))
        self.down_btn.clicked.connect(lambda: self.send_move("Down"))
        self.left_btn.clicked.connect(lambda: self.send_move("Left"))
        self.right_btn.clicked.connect(lambda: self.send_move("Right"))
        self.undo_btn.clicked.connect(lambda: self.server.send_string("undo"))
        self.reset_btn.clicked.connect(self.reset_game)
        self.level_btn.clicked.connect(self.choose_level)

        move_layout.addWidget(self.up_btn, 0, 1)
        move_layout.addWidget(self.left_btn, 1, 0)
        move_layout.addWidget(self.right_btn, 1, 2)
        move_layout.addWidget(self.down_btn, 2, 1)
        move_layout.addWidget(self.undo_btn, 3, 0)
        move_layout.addWidget(self.reset_btn, 3, 2)
        move_layout.addWidget(self.level_btn, 4, 1)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.timer_label)
        right_layout.addWidget(self.step_label)
        right_layout.addWidget(self.record_label)
        right_layout.addLayout(move_layout)
        right_layout.addWidget(self.info_label)

        layout = QHBoxLayout()
        layout.addWidget(self.board_widget, stretch=3)
        layout.addLayout(right_layout, stretch=1)
        self.setLayout(layout)

    def update_timer(self):
        self.elapsed += 1
        self.timer_label.setText(f"Time: {self.elapsed}s")

    def send_move(self, direction):
        pid = self.board_widget.selected_id
        name_map = {
            '0': 'Zhangfei', '1': 'Caocao', '2': 'Machao', '3': 'Huangzhong',
            '4': 'Guanyu', '5': 'Zhaoyun', '6': 'Zu1', '7': 'Zu2', '8': 'Zu3', '9': 'Zu4'
        }
        if pid in name_map:
            cmd = f"move@{name_map[pid]}#{direction}"
            self.server.send_string(cmd)
            self.steps += 1
            self.step_label.setText(f"Steps: {self.steps}")

    def check_response(self):
        if self.server.receivedMessage:
            msg = self.server.receivedMessage
            if len(msg) == 20:
                self.board_widget.update_board(msg)
                self.check_victory(msg)
            else:
                self.info_label.setText(msg)
            self.server.receivedMessage = ""

    def reset_game(self):
        self.elapsed = 0
        self.steps = 0
        self.timer_label.setText("Time: 0s")
        self.step_label.setText("Steps: 0")
        self.info_label.setText("已重置")
        self.board_widget.selected_id = '1'
        self.board_widget.update_board(self.current_board)
        self.server.send_string(f"set@{self.current_board}")

    def choose_level(self):
        dialog = LevelDialog(self.set_level)
        dialog.exec_()

    def set_level(self, board_str):
        self.current_board = board_str
        self.best_time = float('inf')
        self.best_steps = float('inf')
        self.record_label.setText("Best: ∞s / ∞ steps")
        self.reset_game()

    def check_victory(self, board_str):
        if board_str[17] == '1' and board_str[18] == '1':
            if self.elapsed < self.best_time or self.steps < self.best_steps:
                self.best_time = min(self.best_time, self.elapsed)
                self.best_steps = min(self.best_steps, self.steps)
                self.record_label.setText(f"Best: {self.best_time}s / {self.best_steps} steps")

            result = QMessageBox.question(self, "胜利！", "恭喜你，曹操成功逃脱！是否要重新挑战？", QMessageBox.Yes | QMessageBox.No)
            if result == QMessageBox.Yes:
                self.reset_game()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = GameWindow()
    win.show()
    sys.exit(app.exec_())