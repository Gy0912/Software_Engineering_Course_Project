import NetClient
import time
import copy

class HuarongDaoGame:
    def __init__(self):
        self.board = None  # 当前棋盘（1D list，长度20）
        self.history = []  # 历史记录（用于 undo）

    def set_board(self, format_str):
        if len(format_str) != 20:
            return '', 'Invalid initialization string!'
        self.board = list(format_str)
        self.history = []
        return self.get_board_str(), 'Initialization complete!'

    def move_piece(self, name, direction):
        name_to_id = {
            'Zhangfei': '0', 'Caocao': '1', 'Machao': '2', 'Huangzhong': '3',
            'Guanyu': '4', 'Zhaoyun': '5',
            'Zu1': '6', 'Zu2': '7', 'Zu3': '8', 'Zu4': '9'
        }
        width, height = 4, 5
        
        if name not in name_to_id:
            return self.get_board_str(), f'Invalid move! Unknown piece {name}'

        pid = name_to_id[name]
        positions = [i for i, v in enumerate(self.board) if v == pid]
        if not positions:
            return self.get_board_str(), f'Invalid move! Piece {name} not on board'

        xs = [p % width for p in positions]
        ys = [p // width for p in positions]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        dx, dy = 0, 0
        if direction == 'Left': dx = -1
        elif direction == 'Right': dx = 1
        elif direction == 'Up': dy = -1
        elif direction == 'Down': dy = 1
        else:
            return self.get_board_str(), f'Invalid move! Unknown direction {direction}'

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                idx = y * width + x
                if self.board[idx] == pid:
                    new_x, new_y = x + dx, y + dy
                    if not (0 <= new_x < width and 0 <= new_y < height):
                        return self.get_board_str(), 'Invalid move!'
                    new_idx = new_y * width + new_x
                    if self.board[new_idx] != pid and self.board[new_idx] != '#':
                        return self.get_board_str(), 'Invalid move!'

        # 保存历史，仅在合法移动时
        self.history.append(copy.deepcopy(self.board))

        new_board = self.board.copy()
        ordered_ys = range(max_y, min_y - 1, -1) if dy >= 0 else range(min_y, max_y + 1)
        ordered_xs = range(max_x, min_x - 1, -1) if dx >= 0 else range(min_x, max_x + 1)
        for y in ordered_ys:
            for x in ordered_xs:
                idx = y * width + x
                if self.board[idx] == pid:
                    new_idx = (y + dy) * width + (x + dx)
                    new_board[new_idx] = pid
                    new_board[idx] = '#'

        self.board = new_board
        return self.get_board_str(), 'Valid move!'

    def undo(self):
        if self.history:
            self.board = self.history.pop()
        return self.get_board_str(), 'Undo complete!'
        # else:
        #     return self.get_board_str(), 'Nothing to undo!'

    def get_board_str(self):
        return ''.join(self.board)

def is_received_new_message(oldTimeStamp, oldServerMessage, zmqThread):
    return not (oldTimeStamp == zmqThread.messageTimeStamp and oldServerMessage == zmqThread.receivedMessage)

if __name__ == '__main__':
    identity = 'Team8'
    zmqThread = NetClient.ZmqClientThread(identity=identity)
    game = HuarongDaoGame()

    timeStamp = -1
    serverMessage = ''

    while True:
        if is_received_new_message(timeStamp, serverMessage, zmqThread):
            timeStamp = zmqThread.messageTimeStamp
            serverMessage = zmqThread.receivedMessage

            if serverMessage.startswith('set@'):
                format_str = serverMessage[4:]
                board_str, response = game.set_board(format_str)
                zmqThread.sendMsg(board_str)
                zmqThread.sendMsg(response)

            elif serverMessage.startswith('move@'):
                move_cmd = serverMessage[5:]
                if '#' in move_cmd:
                    name, direction = move_cmd.split('#')
                    board_str, response = game.move_piece(name, direction)
                    zmqThread.sendMsg(board_str)
                    zmqThread.sendMsg(response)
                else:
                    zmqThread.sendMsg(game.get_board_str())
                    zmqThread.sendMsg('Invalid move!')

            elif serverMessage == 'undo':
                board_str, response = game.undo()
                zmqThread.sendMsg(board_str)
                zmqThread.sendMsg(response)

            else:
                zmqThread.sendMsg(game.get_board_str())
                zmqThread.sendMsg('Unknown command!')

        time.sleep(0.01)

        # # self.server.send_string("set@9#82#112611530753044")
        # self.server.send_string("set@24432673011501158##9")
# python Development\Frontend\main_with_random.py
# python Development\YourCodeExample\main.py

# Classic
# void init_board() {
#   for (i : int[0,ROWS*COLS-1]) board[i] = -1;

#   // Set board contents from string "01150115244327836##9"
#   board[0] = 0;  board[1] = 1;  board[2] = 1;  board[3] = 5;
#   board[4] = 0;  board[5] = 1;  board[6] = 1;  board[7] = 5;
#   board[8] = 2;  board[9] = 4;  board[10] = 4; board[11] = 3;
#   board[12] = 2; board[13] = 7; board[14] = 8; board[15] = 3;
#   board[16] = 6; board[17] = -1; board[18] = -1; board[19] = 9;

#   // Initialize positions manually:
#   positions[0] = 0;   // ZhangFei at (0,0)
#   positions[1] = 1;   // CaoCao at (0,1)
#   positions[2] = 8;   // MaChao at (2,0)
#   positions[3] = 11;  // HuangZhong at (2,3)
#   positions[4] = 9;   // GuanYu at (2,1)
#   positions[5] = 3;   // ZhaoYun at (0,3)
#   positions[6] = 16;  // Soldier 6 at (4,0)
#   positions[7] = 13;  // Soldier 7 at (3,1)
#   positions[8] = 14;  // Soldier 8 at (3,2)
#   positions[9] = 19;  // Soldier 9 at (4,3)

#   main_check();
# }

# Simple test
# void init_board() {
#   for (i : int[0,ROWS*COLS-1]) board[i] = -1;

#   // Set board contents from string "24432673011501158##9"
#   board[0] = 2;  board[1] = 4;  board[2] = 4;  board[3] = 3;
#   board[4] = 2;  board[5] = 6;  board[6] = 7;  board[7] = 3;
#   board[8] = 0;  board[9] = 1;  board[10] = 1; board[11] = 5;
#   board[12] = 0; board[13] = 1; board[14] = 1; board[15] = 5;
#   board[16] = 8; board[17] = -1; board[18] = -1; board[19] = 9;

#   // Manually assign each piece's top-left position
#   positions[0] = 8;   // ZhangFei
#   positions[1] = 9;   // CaoCao
#   positions[2] = 0;   // MaChao
#   positions[3] = 3;   // HuangZhong
#   positions[4] = 1;   // GuanYu
#   positions[5] = 11;  // ZhaoYun
#   positions[6] = 5;   // Soldier
#   positions[7] = 6;   // Soldier
#   positions[8] = 16;  // Soldier
#   positions[9] = 19;  // Soldier

#   main_check();
# }

# Move test
# void init_board() {
#   for (i : int[0, ROWS * COLS - 1]) board[i] = -1;

#   // Set board contents from string "0235023511441167#89#"
#   board[0]  = 0; board[1]  = 2; board[2]  = 3; board[3]  = 5;
#   board[4]  = 0; board[5]  = 2; board[6]  = 3; board[7]  = 5;
#   board[8]  = 1; board[9]  = 1; board[10] = 4; board[11] = 4;
#   board[12] = 1; board[13] = 1; board[14] = 6; board[15] = 7;
#   board[16] = -1; board[17] = 8; board[18] = 9; board[19] = -1;

#   // Assign positions
#   positions[0] = 0;   // 张飞
#   positions[1] = 8;   // 曹操
#   positions[2] = 1;   // 马超
#   positions[3] = 2;   // 黄忠
#   positions[4] = 10;  // 关羽
#   positions[5] = 3;   // 赵云
#   positions[6] = 14;  // 兵
#   positions[7] = 15;  // 兵
#   positions[8] = 17;  // 兵
#   positions[9] = 18;  // 兵
#   main_check();
# }