# External imports
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Internal imports
from app.api.v1.routers import router as game_router
from app.db_setup import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(game_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
