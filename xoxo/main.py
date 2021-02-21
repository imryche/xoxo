from datetime import timedelta

import sqlalchemy as sa
from fastapi import Depends, FastAPI, Form, HTTPException
from fastapi import status as http_status
from fastapi.security import OAuth2PasswordRequestForm

from xoxo.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    oauth2_scheme,
)
from xoxo.db import create_user, database, get_user, moves
from xoxo.game import (
    BoardStatus,
    check_board_status,
    find_best_move,
    make_move,
    print_board,
)
from xoxo.schemas import PlayerMove, User

ACCESS_TOKEN_EXPIRE_MINUTES = 60


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/play/")
async def play(player_move: PlayerMove, current_user: User = Depends(get_current_user)):
    query = moves.select().order_by(sa.desc(moves.c.created_at))
    last_board = await database.fetch_one(query)
    board = None
    if last_board and last_board["status"] == BoardStatus.ACTIVE.value:
        board = last_board["board"]
    else:
        board = [[None, None, None], [None, None, None], [None, None, None]]

    status = BoardStatus.ACTIVE
    if player_move.has_move():
        make_move(board, (player_move.row, player_move.col), True)
        status = check_board_status(board)
        print("player:", status)

        query = moves.insert().values(
            row=player_move.row,
            col=player_move.col,
            is_ai=False,
            status=status.value,
            board=board,
            user_id=current_user.id,
        )
        await database.execute(query)

    if status not in (BoardStatus.WON, BoardStatus.TIE):
        ai_move = find_best_move(board)
        make_move(board, ai_move, False)
        status = check_board_status(board)
        print("ai:", status)

        query = moves.insert().values(
            row=ai_move[0],
            col=ai_move[1],
            is_ai=True,
            status=status.value,
            board=board,
            user_id=current_user.id,
        )
        await database.execute(query)

    if status != BoardStatus.ACTIVE:
        return {"status": status, "move": ai_move}

    print_board(board)

    return {"status": status, "move": ai_move, "board": board}


@app.get("/moves")
async def read_moves(token: str = Depends(oauth2_scheme)):
    query = moves.select()
    return await database.fetch_all(query)


@app.post("/login/")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register/", status_code=http_status.HTTP_201_CREATED)
async def register(
    username: str = Form(..., min_length=3, max_length=50),
    password: str = Form(..., min_length=3, max_length=50, regex=r"^\w+$"),
):
    if await get_user(username):
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists.",
        )

    await create_user(username, password)


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user