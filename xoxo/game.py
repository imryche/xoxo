import math
from enum import Enum


class BoardStatus(Enum):
    ACTIVE = "active"
    TIE = "tie"
    WON = "won"
    LOST = "lost"


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


def make_move(board, move, player):
    if board[move[0]][move[1]] is None:
        board[move[0]][move[1]] = player
    else:
        raise ValueError(f"Cell ({move[0]},{move[1]}) is occupied.")


def undo_move(board, move):
    board[move[0]][move[1]] = None


def cells_score(cells):
    if all(cell == cells[0] and cell is not None for cell in cells):
        return 10 if cells[0] else -10


def board_score(board, depth=0):
    for row in board:
        if score := cells_score(row):
            return score

    size = len(board)
    for col_idx in range(size):
        col = [board[row][col_idx] for row in range(size)]
        if score := cells_score(col):
            return score

    diagonals = [
        [board[i][i] for i in range(size)],
        [board[i][size - 1 - i] for i in range(size)],
    ]

    for diagonal in diagonals:
        if score := cells_score(diagonal):
            return score

    if not get_possible_moves(board):
        return 0


def check_board_status(board):
    score = board_score(board)
    if score == 10:
        return BoardStatus.WON
    elif score == -10:
        return BoardStatus.LOST
    elif score == 0:
        return BoardStatus.TIE

    return BoardStatus.ACTIVE


def get_possible_moves(board):
    moves = []
    size = len(board)
    for row in range(size):
        for col in range(size):
            if board[row][col] is None:
                moves.append((row, col))
    return moves


def minimax(board, depth, is_maximizing):
    score = board_score(board, depth)
    if score is not None:
        return score

    if is_maximizing:
        best_score = -math.inf
        for move in get_possible_moves(board):
            make_move(board, move, True)
            score = minimax(board, depth + 1, True)
            undo_move(board, move)
            best_val = max([score, best_score])
        return best_val
    else:
        best_score = math.inf
        for move in get_possible_moves(board):
            make_move(board, move, False)
            score = minimax(board, depth + 1, False)
            undo_move(board, move)
            best_val = min([score, best_score])
        return best_val


def find_best_move(board):
    best_move = None
    best_score = -math.inf

    for move in get_possible_moves(board):
        make_move(board, move, True)
        score = minimax(board, 0, False)
        undo_move(board, move)
        if score > best_score:
            best_score = score
            best_move = move

    return best_move
