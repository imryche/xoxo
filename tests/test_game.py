import pytest
from xoxo.game import (
    BoardStatus,
    board_score,
    cells_score,
    check_board_status,
    find_best_move,
    get_possible_moves,
    make_move,
    undo_move
)


def test_maximizing_makes_move():
    board = [
        [True, None, True],
        [None, False, True],
        [False, None, False]
    ]
    make_move(board, (0, 1), True)
    assert board == [
        [True, True, True],
        [None, False, True],
        [False, None, False]
    ]


def test_non_maximizing_makes_move():
    board = [
        [True, None, True],
        [None, False, True],
        [False, None, False]
    ]
    make_move(board, (2, 1), False)
    assert board == [
        [True, None, True],
        [None, False, True],
        [False, False, False]
    ]


def test_makes_forbidden_move():
    board = [
        [True, None, True],
        [None, False, True],
        [False, None, False]
    ]
    with pytest.raises(ValueError):
        make_move(board, (0, 0), False)


def test_undoes_move():
    board = [
        [True, None, True],
        [None, False, True],
        [False, None, False]
    ]
    undo_move(board, (1, 1))
    assert board[1][1] is None


def test_cells_have_positive_score():
    cells = [True, True, True]
    assert cells_score(cells) == 10


def test_cells_have_negative_score():
    cells = [False, False, False]
    assert cells_score(cells) == -10


def test_cells_have_no_score():
    cells = [False, None, True]
    assert cells_score(cells) is None


def test_horizontal_true_win():
    board = [
        [False, None, None],
        [True, True, True],
        [False, None, False]
    ]
    assert board_score(board) == 10


def test_horizontal_false_win():
    board = [
        [True, None, None],
        [False, False, False],
        [True, None, True]
    ]
    assert board_score(board) == -10


def test_vertical_true_win():
    board = [
        [False, None, True],
        [None, False, True],
        [None, False, True]
    ]
    assert board_score(board) == 10


def test_vertical_false_win():
    board = [
        [True, None, False],
        [None, True, False],
        [None, True, False]
    ]
    assert board_score(board) == -10


def test_diagonal_one_win():
    board = [
        [True, None, False],
        [None, True, None],
        [None, False, True]
    ]
    assert board_score(board) == 10


def test_diagonal_two_win():
    board = [
        [True, None, False],
        [None, False, None],
        [False, True, True]
    ]
    assert board_score(board) == -10


def test_tie():
    board = [
        [True, True, False],
        [False, False, True],
        [True, False, True]
    ]
    assert board_score(board) == 0


def test_nobody_won():
    board = [
        [True, None, False],
        [None, True, None],
        [None, True, False]
    ]
    assert board_score(board) is None


def test_board_status_is_active():
    board = [
        [True, None, False],
        [None, True, None],
        [None, True, False]
    ]
    assert check_board_status(board) == BoardStatus.ACTIVE


def test_board_status_is_won():
    board = [
        [True, True, False],
        [None, True, None],
        [None, True, False]
    ]
    assert check_board_status(board) == BoardStatus.WON


def test_board_status_is_lost():
    board = [
        [True, True, False],
        [None, True, False],
        [None, None, False]
    ]
    assert check_board_status(board) == BoardStatus.LOST


def test_board_status_is_tie():
    board = [
        [True, True, False],
        [False, True, True],
        [True, False, False]
    ]
    assert check_board_status(board) == BoardStatus.TIE


def test_possible_moves():
    board = [
        [True, None, False],
        [False, None, None],
        [False, True, True]
    ]
    assert get_possible_moves(board) == [
        (0, 1), (1, 1), (1, 2)
    ]


def test_no_possible_moves_left():
    board = [
        [True, False, True],
        [False, False, True],
        [False, True, False]
    ]
    assert get_possible_moves(board) == []


def test_find_obvious_moves():
    board = [
        [False, False, None],
        [False, True, None],
        [True, None, None]
    ]
    assert find_best_move(board) == (0, 2)

    board = [
        [False, True, None],
        [None, True, None],
        [None, None, None]
    ]
    assert find_best_move(board) == (2, 1)

    board = [
        [False, True, False],
        [True, True, None],
        [True, False, None]
    ]
    assert find_best_move(board) == (1, 2)

    board = [
        [False, False, None],
        [True, True, False],
        [True, None, None]
    ]
    assert find_best_move(board) == (0, 2)
