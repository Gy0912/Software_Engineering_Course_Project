import sys
import time
import random
import subprocess
from collections import deque
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QMessageBox, QDialog, QDialogButtonBox, QFormLayout)
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer, QRect
from Server import ZmqFrontendServer

PIECE_SIZES = {
    '1': (2, 2),
    '0': (1, 2), '2': (1, 2), '3': (1, 2), '5': (1, 2),
    '4': (2, 1),
    '6': (1, 1), '7': (1, 1), '8': (1, 1), '9': (1, 1)
}

BOARD_WIDTH = 4
BOARD_HEIGHT = 5

PIECES = {
    'CaoCao': (2, 2),
    'GuanYu': (2, 1),
    'ZhangFei': (1, 2),
    'MaChao': (1, 2),
    'HuangZhong': (1, 2),
    'ZhaoYun': (1, 2),
    'Bing1': (1, 1),
    'Bing2': (1, 1),
    'Bing3': (1, 1),
    'Bing4': (1, 1),
}

PIECE_KEYS = {
    'CaoCao': '1', 'GuanYu': '4', 'ZhangFei': '0', 'MaChao': '2',
    'HuangZhong': '3', 'ZhaoYun': '5', 'Bing1': '6', 'Bing2': '7',
    'Bing3': '8', 'Bing4': '9'
}

def can_place(board, x, y, w, h):
    if x + w > BOARD_WIDTH or y + h > BOARD_HEIGHT:
        return False
    for dy in range(h):
        for dx in range(w):
            if board[y + dy][x + dx] != '.':
                return False
    return True

def place_piece(board, x, y, w, h, label):
    for dy in range(h):
        for dx in range(w):
            board[y + dy][x + dx] = label

def remove_piece(board, x, y, w, h):
    for dy in range(h):
        for dx in range(w):
            board[y + dy][x + dx] = '.'

def generate_random_board():
    while True:
        board = [['.' for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        piece_list = list(PIECES.items())
        random.shuffle(piece_list)
        placed = []

        def backtrack(index):
            if index == len(piece_list):
                empty_count = sum(row.count('.') for row in board)
                return empty_count == 2
            name, (w, h) = piece_list[index]
            positions = [(x, y) for y in range(BOARD_HEIGHT) for x in range(BOARD_WIDTH)]
            random.shuffle(positions)
            for x, y in positions:
                if can_place(board, x, y, w, h):
                    place_piece(board, x, y, w, h, PIECE_KEYS[name])
                    placed.append((x, y, w, h, name))
                    if backtrack(index + 1):
                        return True
                    placed.pop()
                    remove_piece(board, x, y, w, h)
            return False

        if backtrack(0):
            return ''.join(board[y][x] for y in range(BOARD_HEIGHT) for x in range(BOARD_WIDTH))

def board_str_to_init_code(board_str):
    board = list(board_str)
    code_lines = []
    seen = {}
    print(board)
    for i, ch in enumerate(board):
        if ch == '.':
            code_lines.append(f"  board[{i}] = -1;")
        else:
            pid = int(ch)
            code_lines.append(f"  board[{i}] = {pid};")
            if pid not in seen:
                seen[pid] = i
    for pid in range(10):
        if pid in seen:
            code_lines.append(f"  positions[{pid}] = {seen[pid]};")
    code_lines.append("  add_state_to_visited(positions);")
    code_lines.append("  enqueue_state(positions);")
    code_lines.append("  main_check();")
    return '\n'.join(code_lines)

def replace_init_board(xml_path, new_code, output_path):
    with open(xml_path, 'r', encoding='utf-8') as f:
        xml_text = f.read()
    xml_text = xml_text.replace("CODE_TEMPLATE", new_code)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_text)

def run_uppaal_check(xml_file, q_file):
    result = subprocess.run([
        'verifyta', xml_file, q_file
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    output = result.stdout + result.stderr
    return "Property is satisfied" in output, output

def check_board_solution(board_str):
    new_code = board_str_to_init_code(board_str)
    replace_init_board("Check.xml", new_code, "Check_tmp.xml")
    ok, output = run_uppaal_check("Check_tmp.xml", "Check.q")
    return ok, output

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
            w, h = PIECE_SIZES.get(value, (1, 1))
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
        self.random_btn = QPushButton("随机挑战")

        self.up_btn.clicked.connect(lambda: self.send_move("Up"))
        self.down_btn.clicked.connect(lambda: self.send_move("Down"))
        self.left_btn.clicked.connect(lambda: self.send_move("Left"))
        self.right_btn.clicked.connect(lambda: self.send_move("Right"))
        self.undo_btn.clicked.connect(lambda: self.server.send_string("undo"))
        self.reset_btn.clicked.connect(self.reset_game)
        self.level_btn.clicked.connect(self.choose_level)
        self.random_btn.clicked.connect(self.random_challenge)

        move_layout.addWidget(self.up_btn, 0, 1)
        move_layout.addWidget(self.left_btn, 1, 0)
        move_layout.addWidget(self.right_btn, 1, 2)
        move_layout.addWidget(self.down_btn, 2, 1)
        move_layout.addWidget(self.undo_btn, 3, 0)
        move_layout.addWidget(self.reset_btn, 3, 2)
        move_layout.addWidget(self.level_btn, 4, 1)
        move_layout.addWidget(self.random_btn, 5, 1)

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

    def random_challenge(self):
        while True:
            board_str = generate_random_board()
            ok, _ = check_board_solution(board_str)
            if ok:
                break
        self.set_level(board_str)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = GameWindow()
    win.show()
    sys.exit(app.exec_())