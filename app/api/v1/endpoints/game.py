# External imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import uvicorn

# Internal imports
from app.api.v1.game.game_loop import SceneGenerator
from app.api.v1.database.operations import DatabaseOperations
from app.api.v1.validation.schemas import (
    StartingStory,
    StoryActionSegment,
    GameSession,
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/fetch_story")
async def fetch_story(story: StartingStory):
    """Fetches a starting story from the database."""
    db_ops = DatabaseOperations()
    story_id = story.starting_story
    story_value = db_ops.get_story(story_id)
    return story_value


@app.post("/roll_dice")
async def roll_dice(story: StoryActionSegment) -> Dict[str, str | int | bool]:
    """Rolls dice on a story/action segmentand returns the result."""
    game = SceneGenerator()
    dice_info = await game.get_dice_info(story)
    return dice_info


@app.post("/generate_new_scene")
async def generate_new_scene(game_session: GameSession) -> Dict[str, str]:
    """Generates a new scene based on the previous one."""
    game = SceneGenerator()
    scene = await game.get_next_scene(game_session)
    return scene


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
