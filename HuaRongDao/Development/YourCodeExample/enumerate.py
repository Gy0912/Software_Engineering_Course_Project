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

def count_boards():
    board = [['.' for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
    count = [0]  # 用列表包一层以便在递归中修改

    def backtrack(pieces, index):
        if index == len(pieces):
            empty_count = sum(row.count('.') for row in board)
            if empty_count == 2:
                count[0] += 1
            return

        name, (w, h) = pieces[index]
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if can_place(board, x, y, w, h):
                    place_piece(board, x, y, w, h, name[0])
                    backtrack(pieces, index + 1)
                    remove_piece(board, x, y, w, h)

    piece_list = list(PIECES.items())
    backtrack(piece_list, 0)
    return count[0]

# 运行计数
total = count_boards()
print(f"总共有 {total} 种合法摆放方案")
