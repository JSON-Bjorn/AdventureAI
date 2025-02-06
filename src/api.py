from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import time

from .adventureai import AdventureGame
from .utils import ResourceManager

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for static files if they don't exist
os.makedirs("static/images", exist_ok=True)
os.makedirs("static/audio", exist_ok=True)

# Mount static directories
app.mount("/static", StaticFiles(directory="static"), name="static")


# Pydantic models for request/response
class PlayerAction(BaseModel):
    action: str
    previous_stories: Optional[List[str]] = []


class GameState(BaseModel):
    story: str
    image_url: str
    needs_dice_roll: bool
    required_roll: Optional[int] = None
    mood: Optional[str] = None
    audio_url: Optional[str] = None


# Global variables
game: Optional[AdventureGame] = None
last_game_start: float = 0
GAME_START_COOLDOWN = 2.0  # Minimum seconds between game starts


@app.on_event("startup")
async def startup_event():
    """Initialize global resources and models on server startup"""
    print("\n=== Server Startup ===")
    print("1. Initializing global resources...")
    await ResourceManager.initialize()
    print("2. Creating initial game instance...")
    global game
    game = AdventureGame()
    await game.initialize_resources()
    print("Server initialized and ready for games!\n")


@app.post("/start-game")
async def start_game():
    """Start a new game when the user clicks play"""
    global game, last_game_start
    current_time = time.time()

    # Prevent rapid consecutive calls
    if current_time - last_game_start < GAME_START_COOLDOWN:
        print(
            f"Ignoring start-game request - cooldown active ({GAME_START_COOLDOWN - (current_time - last_game_start):.1f}s remaining)"
        )
        if game:
            return game.get_current_state()
        raise HTTPException(
            status_code=429, detail="Please wait before starting a new game"
        )

    print("\n=== Starting New Game ===")
    try:
        if game is None:
            print("1. Creating new game instance...")
            game = AdventureGame()
            await game.initialize_resources()
        else:
            print("1. Resetting existing game...")
            await game.cleanup()
            game = AdventureGame()
            await game.initialize_resources()

        print("2. Starting game loop...")
        await game.start_game()
        last_game_start = current_time
        print("=== Game Started Successfully ===\n")
        return game.get_current_state()
    except Exception as e:
        print(f"Error starting game: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/player-action")
async def process_action(action: PlayerAction):
    global game
    if game is None:
        raise HTTPException(status_code=400, detail="Game not initialized")

    try:
        return await game.process_action(action.action)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/roll-dice/{required_roll}")
async def roll_dice(required_roll: int):
    global game
    if game is None:
        raise HTTPException(status_code=400, detail="Game not initialized")

    try:
        success = game.process_dice_roll(required_roll)
        game.success = success
        return await game.generate_next_scene()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup all resources when server shuts down"""
    print("\n=== Server Shutdown ===")
    global game
    if game:
        print("1. Cleaning up game state...")
        await game.cleanup()
    print("2. Cleaning up global resources...")
    await ResourceManager.cleanup()
    print("Server shutdown complete\n")
