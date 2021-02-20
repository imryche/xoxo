import math
import copy


def print_board(board):
    for row in board:
        for cell in row:
            if cell is None:
                symbol = "_"
            else:
                symbol = "x" if cell else "o"
            print(symbol, end="")
        print("")
    print()


def move(board, row, col, maximizing):
    if board[row][col] is None:
        board[row][col] = maximizing
    else:
        raise ValueError("cell is occupied")


def cells_score(cells, depth):
    if len(cells) > 0 and all(cell == cells[0] for cell in cells):
        if cells[0]:
            return 10 - depth
        return depth - 10


def board_score(board, depth=0):
    for row in board:
        if (score := cells_score(row, depth)) is not None:
            return score

    size = len(board)
    for col_idx in range(size):
        col = [board[row][col_idx] for row in range(size)]
        if (score := cells_score(col, depth)) is not None:
            return score

    diagonals = [
        [board[i][i] for i in range(size)],
        [board[i][size - 1 - i] for i in range(size)],
    ]

    for diagonal in diagonals:
        if (score := cells_score(diagonal, depth)) is not None:
            return score

    return 0


def get_possible_moves(board):
    moves = []
    size = len(board)
    for row in range(size):
        for col in range(size):
            if board[row][col] is None:
                moves.append((row, col))
    return moves


def get_possible_board(board, move, is_maximizing):
    board = copy.deepcopy(board)
    board[move[0]][move[1]] = is_maximizing
    return board


def minimax(board, depth, is_maximizing):
    score = board_score(board, depth)
    if score:
        return score

    possible_moves = get_possible_moves(board)
    if not possible_moves:
        return 0

    depth += 1

    def get_best_value(best_val, func):
        for move in possible_moves:
            possible_board = get_possible_board(board, move, not is_maximizing)
            val = minimax(possible_board, depth, not is_maximizing)
            best_val = func([best_val, val])
        return best_val

    if is_maximizing:
        return get_best_value(-math.inf, max)
    else:
        return get_best_value(math.inf, min)


def find_best_move(board):
    best_move = None
    best_val = -math.inf
    for move in get_possible_moves(board):
        possible_board = get_possible_board(board, move, True)
        val = minimax(possible_board, 0, True)
        if val > best_val:
            best_val = val
            best_move = move

    return best_move
