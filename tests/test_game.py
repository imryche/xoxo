import pytest
from game import (
    find_best_move,
    get_possible_board,
    get_possible_moves,
    get_score,
    move
)


def test_maximizing_makes_move():
    board = [
        [True, None, True],
        [None, False, True],
        [False, None, False]
    ]
    move(board, 0, 1, True)
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
    move(board, 2, 1, False)
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
        move(board, 0, 0, False)


def test_horizontal_win():
    board = [
        [False, None, None],
        [True, True, True],
        [False, None, False]
    ]
    assert get_score(board) == 10


def test_vertical_win():
    board = [
        [True, None, False],
        [None, True, False],
        [None, True, False]
    ]
    assert get_score(board) == -10


def test_diagonal_one_win():
    board = [
        [True, None, False],
        [None, True, None],
        [None, False, True]
    ]
    assert get_score(board) == 10


def test_diagonal_two_win():
    board = [
        [True, None, False],
        [None, False, None],
        [False, True, True]
    ]
    assert get_score(board) == -10


def test_nobody_won():
    board = [
        [True, None, False],
        [None, True, None],
        [None, True, False]
    ]
    assert get_score(board) == 0


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


def test_possible_board_created():
    board = [
        [True, None, None],
        [False, False, True],
        [False, True, False]
    ]
    possible_board = get_possible_board(board, (0, 1), is_maximizing=True)
    assert possible_board == [
        [True, True, None],
        [False, False, True],
        [False, True, False]
    ]
    assert board is not possible_board


def test_find_obvious_moves():
    board = [
        [True, False, True],
        [False, False, True],
        [None, None, None]
    ]
    assert find_best_move(board) == (2, 2)

    board = [
        [True, False, False],
        [None, False, None],
        [None, True, True]
    ]
    assert find_best_move(board) == (2, 0)

    board = [
        [True, False, True],
        [True, False, False],
        [None, None, False]
    ]
    assert find_best_move(board) == (2, 0)

    board = [
        [True, False, True],
        [False, False, None],
        [None, None, True]
    ]
    assert find_best_move(board) == (1, 2)
