from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class StartingStory(BaseModel):
    starting_story: int


class StoryActionSegment(BaseModel):
    story: str
    action: str


class GameSession(BaseModel):
    id: Optional[int] = None
    session_name: Optional[str] = None
    protagonist_name: str
    inventory: list[str]
    current_story: str
    scenes: list


class UserCreate(BaseModel):
    password: str
    email: EmailStr


class UserUpdate(BaseModel):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserEmail(BaseModel):
    email: EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class SaveGame(BaseModel):
    game_session: GameSession
    image: Optional[str] = None
