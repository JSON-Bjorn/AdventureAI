# External imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

# Internal imports
from src.game.game_loop import GameSession

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API som påbörjat nytt spel
@app.post("/start_new_game")
async def start_new_game(game_session: Dict):
    game = GameSession()
    scene = await game.get_next_scene(game_session)
    return scene


@app.post("/save_game")
async def continue_game(game_session: Dict):
    game = GameSession()
    game.save_game(game_session)


# API som börjar gammalts spel

# API som skickar user input tillsammans med user id

# API som skapar ny användare

# API som loggar in en användare
