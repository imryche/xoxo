import os
from datetime import datetime, timedelta
from typing import Optional

import databases
import sqlalchemy as sa
from fastapi import Depends, FastAPI, HTTPException, Form
from fastapi import status as http_status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import ARRAY

from xoxo.game import (
    BoardStatus,
    check_board_status,
    find_best_move,
    make_move,
    print_board,
)

DATABASE_URL = os.environ["DATABASE_URL"]
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


database = databases.Database(DATABASE_URL)

metadata = sa.MetaData()

users = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("username", sa.String, nullable=False),
    sa.Column("password", sa.String, nullable=False),
)

moves = sa.Table(
    "moves",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("row", sa.Integer, nullable=False),
    sa.Column("col", sa.Integer, nullable=False),
    sa.Column("is_ai", sa.Boolean, nullable=False),
    sa.Column("status", sa.String, nullable=False),
    sa.Column("board", ARRAY(sa.Boolean), nullable=False),
    sa.Column(
        "created_at", sa.DateTime, server_default=sa.sql.functions.now(), nullable=False
    ),
)


engine = sa.create_engine(DATABASE_URL)
metadata.create_all(engine)


class PlayerMove(BaseModel):
    row: Optional[int] = None
    col: Optional[int] = None
    size: Optional[int] = 3

    def has_move(self):
        return all(v is not None for v in (self.row, self.col))


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str


class UserInDB(User):
    password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username):
    query = users.select().where(users.c.username == username)
    user = await database.fetch_one(query)
    if user:
        return UserInDB(**user)


async def create_user(username, password):
    hashed_password = get_password_hash(password)
    query = users.insert().values(username=username, password=hashed_password)
    await database.execute(query)


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False

    if not verify_password(password, user.password):
        return False

    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=http_status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await get_user(token_data.username)
    if user is None:
        raise credentials_exception

    return user


def fake_hash_password(password: str):
    return "fakehashed" + password


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/play/")
async def play(player_move: PlayerMove):
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
        )
        await database.execute(query)

    if status not in (BoardStatus.WON, BoardStatus.TIE):
        ai_move = find_best_move(board)
        make_move(board, ai_move, False)
        status = check_board_status(board)
        print("ai:", status)

        query = moves.insert().values(
            row=ai_move[0], col=ai_move[1], is_ai=True, status=status.value, board=board
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
