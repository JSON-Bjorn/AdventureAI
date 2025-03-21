# External imports
from fastapi import APIRouter, Depends
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session

# Internal imports
from app.db_setup import get_db
from app.api.v1.game.game_loop import SceneGenerator
from app.api.v1.database.operations import DatabaseOperations
from app.api.v1.validation.schemas import (
    StartingStory,
    StoryActionSegment,
    GameSession,
    SaveGame,
    LoadGame,
)
from app.api.logger.logger import get_logger


logger = get_logger("app.api.endpoints.game")

router = APIRouter(tags=["game"])


@router.post("/fetch_story")
async def fetch_story(
    story: StartingStory, db: Session = Depends(get_db)
) -> Dict[str, Optional[str]]:
    """Fetches a starting story from the database."""
    logger.info(
        f"Fetch story endpoint requested with story ID: {story.starting_story}"
    )
    db_ops = DatabaseOperations(db)
    try:
        starting_story = db_ops.get_start_story(story.starting_story)
    except Exception as e:
        logger.error(f"Error fetching story: {str(e)}")
        raise ValueError(f"Error fetching story: {str(e)}")
    logger.info("Returning starting story to client")
    return {"story": starting_story.story, "id": None}


@router.post("/roll_dice")
async def roll_dice(
    story: StoryActionSegment, db: Session = Depends(get_db)
) -> Dict[str, str | int | bool]:
    """Rolls dice on a story/action segmentand returns the result."""
    logger.info(f"Roll Dice-endpoint requested for action: {story.action}")
    game = SceneGenerator(db)
    dice_info = await game.get_dice_info(story)
    logger.info(f"Dice rolled: {dice_info}")
    return dice_info


@router.post("/generate_new_scene")
async def generate_new_scene(
    game_session: GameSession, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Generates a new scene based on the previous one."""
    logger.info("Generate New Scene-endpoint was requested.")
    game = SceneGenerator(db)
    scene = await game.get_next_scene(game_session)
    logger.info("Successfully generated new scene.")
    return scene


@router.post("/save_game")
async def save_game(
    game_session: SaveGame, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Saves stories and user input to the database."""
    logger.info("Saving a game session")
    # Save the game_session stories to the database under game_session table
    # Save the users input to the database under users.inputs
    db_ops = DatabaseOperations(db)
    # db_ops.save_game(game_session.dict())  # Uncomment when implemented
    logger.warning("Game saving not implemented yet")
    return {"message": "Our backend dev is on vacation"}


@router.post("/load_game")
async def load_game(
    payload: LoadGame, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Loads a game session from the database."""
    logger.info("Load Game-endpoint was requested.")
    token = payload.token
    db_ops = DatabaseOperations(db)
    # game_data = db_ops.load_game(payload.game_id)  # Uncomment when implemented
    # Do the databse thing here
    logger.warning("Game loading not implemented yet")
    return {"Nothing here yet": "absolutely nothing"}
