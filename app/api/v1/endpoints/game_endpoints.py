# External imports
from fastapi import APIRouter, Depends
from typing import Dict, List
from sqlalchemy.orm import Session
from uuid import UUID

# Internal imports
from app.db_setup import get_db
from app.api.logger.logger import get_logger
from app.api.v1.game.game_loop import SceneGenerator
from app.api.v1.database.operations import DatabaseOperations
from app.api.v1.endpoints.token_validation import get_token, requires_auth
from app.api.v1.validation.schemas import (
    StartingStory,
    StoryActionSegment,
    GameSession,
    SaveGame,
)

logger = get_logger("app.api.endpoints.game")
router = APIRouter(tags=["game"])


@router.post("/fetch_story")
@requires_auth(get_id=True)
async def fetch_story(
    story: StartingStory,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
    user_id: UUID = None,
):
    """Fetches a starting story from the database."""
    logger.info(
        f"User ID: {str(user_id)[:5]}... "
        "was granted access to /fetch_story"
    )
    starting_story = DatabaseOperations(db).get_start_story(
        story.starting_story
    )
    logger.info("Returning starting story to client")
    return {"story": starting_story.story, "id": None}


@router.post("/roll_dice")
@requires_auth(get_id=True)
async def roll_dice(
    story: StoryActionSegment,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
    user_id: UUID = None,
) -> Dict[str, str | int | bool]:
    """Rolls dice on a story/action segment"""
    logger.info(
        f"User ID: {str(user_id)[:5]}... " "was granted access to /roll_dice"
    )
    dice_info = await SceneGenerator(db).get_dice_info(story)
    logger.info(f"Dice rolled: {dice_info}")
    return dice_info


@router.post("/generate_new_scene")
@requires_auth(get_id=True)
async def generate_new_scene(
    game_session: GameSession,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
    user_id: UUID = None,
) -> Dict[str, str]:
    """Generates a new scene based on the previous one."""
    logger.info(
        f"User ID: {str(user_id)[:5]}... "
        "was granted access to /generate_new_scene"
    )
    scene = await SceneGenerator(db).get_next_scene(game_session)
    logger.info("Successfully generated new scene.")
    return scene


@router.post("/save_game")
@requires_auth(get_id=True)
async def save_game(
    game: SaveGame,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
    user_id: int = None,
) -> Dict[str, str]:
    """Saves stories and user input to the database."""
    logger.info(
        f"User ID: {str(user_id)[:5]}... was granted access to /save_game"
    )
    DatabaseOperations(db).save_game_route(game, user_id)
    return {"message": "Game saved successfully"}


@router.get("/load_game")
@requires_auth(get_id=True)
async def load_game(
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
    user_id: int = None,
):
    """Loads a game session from the database."""
    logger.info(
        f"User ID: {str(user_id)[:5]}... was granted access to /load_game"
    )
    saves: List[GameSession] = DatabaseOperations(db).load_game(user_id)
    logger.info("Returning saves to client")
    return {"saves": saves}
