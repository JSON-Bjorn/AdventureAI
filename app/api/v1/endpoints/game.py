# External imports
from fastapi import APIRouter, Depends, HTTPException, Header, Security
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

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

security = HTTPBearer()


def get_token(
    authorization: Optional[str] = Header(),
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """Extracts the token in the request"""
    logger.info("Extracting token from header")
    if authorization is None:
        raise HTTPException(
            status_code=401, detail="Authorization header missing"
        )
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return authorization


@router.post("/fetch_story")
async def fetch_story(
    story: StartingStory,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
):
    """Fetches a starting story from the database."""
    logger.info("Fetch story endpoint requested")
    db_ops = DatabaseOperations(db)

    # Check if user is logged in and get starting story
    if db_ops.validate_token(token):
        starting_story = db_ops.get_start_story(story.starting_story)
        logger.info("Returning starting story to client")
        return {"story": starting_story.story, "id": None}
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/roll_dice")
async def roll_dice(
    story: StoryActionSegment,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
) -> Dict[str, str | int | bool]:
    """Rolls dice on a story/action segmentand returns the result."""
    logger.info(f"Roll Dice-endpoint requested for action: {story.action}")
    game = SceneGenerator(db)
    dice_info = await game.get_dice_info(story)
    logger.info(f"Dice rolled: {dice_info}")
    return dice_info


@router.post("/generate_new_scene")
async def generate_new_scene(
    game_session: GameSession,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
) -> Dict[str, str]:
    """Generates a new scene based on the previous one."""
    logger.info("Generate New Scene-endpoint was requested.")
    game = SceneGenerator(db)
    scene = await game.get_next_scene(game_session)
    logger.info("Successfully generated new scene.")
    return scene


@router.post("/save_game")
async def save_game(
    game: SaveGame,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
) -> Dict[str, str]:
    """Saves stories and user input to the database."""
    logger.info("Saving a game session")
    db_ops = DatabaseOperations(db)

    # Validate user is logged in and save their game
    user_id = db_ops.validate_token(token)
    db_ops.save_game_route(game, user_id)
    return {"message": "Game saved successfully"}


@router.get("/load_game")
async def load_game(
    db: Session = Depends(get_db), token: str = Depends(get_token)
):
    """Loads a game session from the database."""
    logger.info("Load Game-endpoint was requested.")
    db_ops = DatabaseOperations(db)

    # Validate user is logged in and get their saves
    user_id = db_ops.validate_token(token)
    saves: List[GameSession] = db_ops.load_game(user_id)
    logger.warning("Returning saves to client")
    return {"saves": saves}
