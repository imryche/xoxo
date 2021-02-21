from typing import Optional, List

import databases
import sqlalchemy as sa
from fastapi import FastAPI
from pydantic import BaseModel

from xoxo.game import (
    BoardStatus,
    check_board_status,
    find_best_move,
    make_move,
    print_board,
)


DATABASE_URL = "sqlite:///xoxo.db"

database = databases.Database(DATABASE_URL)

metadata = sa.MetaData()

moves = sa.Table(
    "moves",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("row", sa.Integer),
    sa.Column("col", sa.Integer),
    sa.Column("is_user", sa.Boolean),
)


engine = sa.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)


class Action(BaseModel):
    row: Optional[int] = None
    col: Optional[int] = None

    def has_move(self):
        return all(v is not None for v in (self.row, self.col))


class Move(BaseModel):
    id: int
    row: int
    col: int
    is_user: bool


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


board = [[None, None, None], [None, None, None], [None, None, None]]


@app.post("/play/")
async def play(action: Action):
    status = BoardStatus.ACTIVE
    if action.has_move():
        make_move(board, (action.row, action.col), True)
        status = check_board_status(board)
        print("player:", status)

        query = moves.insert().values(row=action.row, col=action.col, is_user=True)
        await database.execute(query)

    if status not in (BoardStatus.WON, BoardStatus.TIE):
        ai_move = find_best_move(board)
        make_move(board, ai_move, False)
        status = check_board_status(board)
        print("ai:", status)

        query = moves.insert().values(row=ai_move[0], col=ai_move[1], is_user=False)
        await database.execute(query)

    if status != BoardStatus.ACTIVE:
        return {"status": status, "move": ai_move}

    print_board(board)

    return {"status": status, "move": ai_move, "board": board}


@app.get("/moves/", response_model=List[Move])
async def read_moves():
    query = moves.select()
    return await database.fetch_all(query)
