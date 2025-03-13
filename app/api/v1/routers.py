# External imports
from fastapi import APIRouter

# Internal imports
from app.api.v1.endpoints import game, user

router = APIRouter(prefix="/v1")
router.include_router(game.router)
router.include_router(user.router)
