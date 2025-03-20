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
from app.api.logger.logger import get_logger


logger = get_logger("app.api.endpoints.game")

router = APIRouter(tags=["game"])


@router.post("/fetch_story")
async def fetch_story(story: StartingStory) -> Dict[str, str]:
    """Fetches a starting story from the database."""
    logger.info(
        f"Fetch story endpoint requested with story ID: {story.starting_story}"
    )
    db_ops = DatabaseOperations()
    story_id = story.starting_story
    starting_story = db_ops.get_story(story_id)
    logger.info("Successfully fetched starting story")
    return starting_story


@router.post("/roll_dice")
async def roll_dice(story: StoryActionSegment) -> Dict[str, str | int | bool]:
    """Rolls dice on a story/action segmentand returns the result."""
    logger.info(f"Roll Dice-endpoint requested for action: {story.action}")
    game = SceneGenerator()
    dice_info = await game.get_dice_info(story)
    logger.info(f"Dice rolled: {dice_info}")
    return dice_info


@router.post("/generate_new_scene")
async def generate_new_scene(game_session: GameSession) -> Dict[str, str]:
    """Generates a new scene based on the previous one."""
    logger.info("Generate New Scene-endpoint was requested.")
    game = SceneGenerator()
    scene = await game.get_next_scene(game_session)
    logger.info("Successfully generated new scene.")
    return scene


@router.post("/save_game")
async def save_game(game_session: GameSession) -> Dict[str, str]:
    """Saves stories and user input to the database."""
    logger.info("Saving game session")
    # Save the game_session stories to the database under game_session table
    # Save the users input to the database under users.inputs
    logger.warning("Game saving not implemented yet")
    return {"message": "Our backend dev is on vacation"}


@router.get("/load_game")
async def load_game(
    game_session: GameSession, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Loads a game session from the database."""
    logger.info("Load Game-endpoint was requested.")
    # Do the thing
    logger.warning("Game loading not implemented yet")
    return {"message": "Our backend dev is on vacation"}
