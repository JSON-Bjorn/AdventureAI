# External imports
from fastapi import APIRouter

# Internal imports
from app.api.v1.endpoints import game

router = APIRouter(prefix="/v1")
router.include_router(game.router)
