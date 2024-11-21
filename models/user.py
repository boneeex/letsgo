from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    password: str
    ac_creation_time: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    points: Optional[int] = 0
    quizes_done: Optional[str] = ''
    ach_done: Optional[str] = ''
    likes: Optional[int] = 0
    dislikes: Optional[int] = 0
    films_watched: Optional[int] = 0
    streak_days: Optional[int] = 0


class UserLoginRequest(BaseModel):
    username: str | None = None
    password: str | None = None