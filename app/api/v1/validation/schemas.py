from pydantic import BaseModel


class StartingStory(BaseModel):
    starting_story: str


class StoryActionSegment(BaseModel):
    story: str
    action: str


class GameSession(BaseModel):
    protagonist_name: str
    inventory: list[str]
    current_story: str
    scenes: list
