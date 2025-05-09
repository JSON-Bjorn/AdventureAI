# External imports
from fastapi import APIRouter, Depends, Request
from typing import Dict, List
from sqlalchemy.orm import Session
from uuid import UUID

# Internal imports
from app.db_setup import get_db
from app.api.logger.logger import get_logger
from app.api.v1.game.game_loop import SceneGenerator
from app.api.v1.database.operations import DatabaseOperations
from app.api.v1.endpoints.token_validation import get_token, requires_auth
from app.api.v1.endpoints.rate_limiting import rate_limit
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
@rate_limit(authenticated_limit=10, unauthenticated_limit=10)
async def fetch_story(
    request: Request,
    story: StartingStory,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
    user_id: UUID = None,
):
    """Fetches a starting story from the database."""
    from fastapi import HTTPException

    raise HTTPException(
        status_code=500,
        detail="Fetching stories is not available at this time",
    )
    logger.info(
        f"User ID: {str(user_id)[:5]}... "
        "was granted access to /fetch_story"
    )
    response = DatabaseOperations(db).get_start_story(story.story_id)
    logger.info("Returning starting story to client")
    return response


@router.post("/roll_dice")
@requires_auth(get_id=True)
@rate_limit(authenticated_limit=10, unauthenticated_limit=10)
async def roll_dice(
    request: Request,
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
@rate_limit(authenticated_limit=6, unauthenticated_limit=6)
async def generate_new_scene(
    request: Request,
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
@rate_limit(authenticated_limit=20, unauthenticated_limit=20)
async def save_game(
    request: Request,
    game: SaveGame,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
    user_id: int = None,
) -> Dict[str, int]:
    """Saves stories and user input to the database."""
    logger.info(
        f"User ID: {str(user_id)[:5]}... was granted access to /save_game"
    )
    game_id = DatabaseOperations(db).save_game_route(game, user_id)
    return {"game_id": game_id}


@router.get("/load_game")
@requires_auth(get_id=True)
@rate_limit(authenticated_limit=10, unauthenticated_limit=10)
async def load_game(
    request: Request,
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
