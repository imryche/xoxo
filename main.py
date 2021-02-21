from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from xoxo.game import (
    BoardStatus,
    check_board_status,
    find_best_move,
    make_move,
    print_board
)


class Action(BaseModel):
    row: Optional[int] = None
    col: Optional[int] = None

    def has_move(self):
        return all(v is not None for v in (self.row, self.col))


app = FastAPI()
board = [[None, None, None], [None, None, None], [None, None, None]]


@app.post("/play/")
async def play(action: Action):
    status = BoardStatus.ACTIVE
    if action.has_move():
        status = make_move(board, (action.row, action.col), True)
        status = check_board_status(board)

    if status not in (BoardStatus.WON, BoardStatus.TIE):
        ai_move = find_best_move(board)
        status = make_move(board, ai_move, False)

    if status != BoardStatus.ACTIVE:
        return {"status": status, "move": ai_move}

    print_board(board)

    return {"status": status, "move": ai_move, "board": board}
