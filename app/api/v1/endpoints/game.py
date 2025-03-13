# External imports
from fastapi import APIRouter, Depends
from typing import Dict
from sqlalchemy.orm import Session

# Internal imports
from app.db_setup import get_db
from app.api.v1.game.game_loop import SceneGenerator
from app.api.v1.database.operations import DatabaseOperations
from app.api.v1.validation.schemas import (
    StartingStory,
    StoryActionSegment,
    GameSession,
)

router = APIRouter(tags=["game"])


@router.post("/fetch_story")
async def fetch_story(
    story: StartingStory, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Fetches a starting story from the database."""
    db_ops = DatabaseOperations()
    story_id = story.starting_story
    starting_story = db_ops.get_story(story_id)
    return starting_story


@router.post("/roll_dice")
async def roll_dice(story: StoryActionSegment) -> Dict[str, str | int | bool]:
    """Rolls dice on a story/action segmentand returns the result."""
    game = SceneGenerator()
    dice_info = await game.get_dice_info(story)
    return dice_info


@router.post("/generate_new_scene")
async def generate_new_scene(game_session: GameSession) -> Dict[str, str]:
    """Generates a new scene based on the previous one."""
    game = SceneGenerator()
    scene = await game.get_next_scene(game_session)
    return scene


@router.post("/save_game")
async def save_game(
    game_session: GameSession, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Saves stories and user input to the database."""
    # Save the game_session stories to the database under game_session table
    # Save the users input to the database under users.inputs
    return {"message": "Our backend dev is on vacation"}


@router.get("/load_game")
async def load_game(
    game_session: GameSession, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Loads a game session from the database."""
    # Do the thing
    return {"message": "Our backend dev is on vacation"}
