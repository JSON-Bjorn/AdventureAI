# External imports
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Internal imports
from app.api.v1.routers import router as game_router
from app.db_setup import init_db
from app.api.logger.logger import get_logger

# Create main application logger
app_logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("Application starting up - initializing database")
    init_db()
    app_logger.info("Database initialized successfully")
    yield
    app_logger.info("Application shutting down")


# Create the FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)
app_logger.info("FastAPI application created")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://0.0.0.0:3000",
    ],  # Include both localhost and IP
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
app_logger.info("CORS middleware configured")

# Include the router
app.include_router(game_router)
app_logger.info("API routes registered")

if __name__ == "__main__":
    app_logger.info("Starting uvicorn server")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
