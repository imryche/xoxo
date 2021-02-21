from typing import Optional
from pydantic import BaseModel


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
    id: int
    username: str


class UserInDB(User):
    password: str
