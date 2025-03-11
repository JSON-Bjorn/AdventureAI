# External imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import uvicorn

# Internal imports
from src.game.game_loop import SceneGenerator
from src.database.database_operations import DatabaseOperations
from src.schemas.schemas import (
    StartingStory,
    StoryActionSegment,
    GameSession,
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/fetch_story")
async def fetch_story(story: StartingStory):
    """
    Fetches a starting story from the database.

    Args:
        story(Dict): The story to fetch.

    Returns:
        story_value(Dict): The fetched story.
    """
    db_ops = DatabaseOperations()
    story_id = story.starting_story
    story_value = db_ops.get_story(story_id)
    return story_value


@app.post("/roll_dice")
async def roll_dice(story: StoryActionSegment):
    """
    Rolls dice and returns the result.

    Args:
        story(StoryActionSegment): The story and action to roll the dice on.

    Returns:
        dice_info(Dict): Threshold: int, roll: int, success: bool.
    """
    game = SceneGenerator()
    dice_info = await game.get_dice_info(story)
    return dice_info


@app.post("/generate_new_scene")
async def generate_new_scene(game_session: GameSession):
    """
    Generates a new scene based on the previous one.

    Args:
        game_session(Dict): The current game session. Contains story and action.

    Returns:
        scene(Dict): The new scene. Contains story, musicpath, image, and compressed story.
    """
    game = SceneGenerator()
    scene = await game.get_next_scene(game_session)
    return scene


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
