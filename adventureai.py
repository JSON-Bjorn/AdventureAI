"""
AdventureAI - An AI-Powered Choose Your Own Adventure Game

Main Game Architecture and Flow Controller

Core Components:
    Text Generation:
        - Uses Swarm agents to generate a story.
        - Takes previous stories into context when generatting new ones.

    Image Generation:
        - Stable Diffusion 1.5
        - Comic panel style
        - Character portraits
        - Scene visualization

    Sound Generation:
        - Bark/AudioCraft integration
        - Voice synthesis
        - Sound effects
        - Ambient audio

    Database:
        - PostgreSQL with pg_embeddings
        - SQLAlchemy ORM
        - State persistence
        - Media caching

Game Flow:
    1. Character Creation:
        - Description input
        - Stats generation
        - Portrait creation
        - Database initialization

    2. Story Progression:
        - Scene generation
        - Visual rendering
        - Audio production
        - Player interaction
        - State updates

    3. Action Resolution:
        - Probability calculation
        - Outcome determination
        - Multi-modal feedback
        - State persistence

    4. Death Handling:
        - Death scene creation
        - State cleanup
        - Game over processing
        - Save management

Technical Features:
    - Asynchronous processing
    - Resource optimization
    - Error recovery
    - State management
    - Media caching
    - Performance monitoring

Usage:
    Run directly to start game:
    `python adventureai.py`

Requirements:
    - Python 3.8+
    - PostgreSQL 12+
    - GPU recommended
    - 16GB+ RAM
    - See requirements.txt
"""

from agents import (
    TextAgent,
    SoundAgent,
    IllustratorAgent,
    TriageAgent,
)
from utils.database import Database
from utils.dice_roller import DiceRoller
from PIL import Image


def instantialize_agents():
    dice_roller = DiceRoller()
    author = TextAgent()
    narrator = SoundAgent()
    illustrator = IllustratorAgent()
    dungeon_master = TriageAgent(author, narrator, illustrator)
    game_loop(dice_roller, dungeon_master)


async def game_loop(dice_roller, dungeon_master):
    """
    Main game loop that initializes and coordinates all components.

    Flow:
    1. Initialize database and utilities
    2. Start agent services
    3. Begin character creation
    4. Start main game loop
    5. Process player input
    6. Generate appropriate responses
    7. Update game state
    8. Handle game over conditions
    """

    game_active = True
    while game_active:
        dungeon_master.next_story()

        text = dungeon_master.get_text()
        show_text(text)
        audio = dungeon_master.get_voiceover()
        play_voiceover(audio)
        image = dungeon_master.get_image()
        show_image(image)

        player_choice: str = dungeon_master.player_turn()
        if player_choice.lower().strip() == "exit":
            game_active = True
            continue

        dice_roll_needed: int = dice_roller.assess_situation(
            dungeon_master.current_story, player_choice
        )

        if dice_roll_needed:
            show_text(f"\nTo do that, you must roll {dice_roll_needed}")
            input("Roll dice!\n")
            (success, player_roll) = dice_roller.roll_dice(dice_roll_needed)
            show_text(f"You rolled a: {player_roll}!\n")


def show_text(text):
    print("\n" * 20)
    print(f"\n{text}")


def play_voiceover(audio):
    pass


def show_image(image):
    Image.open(image)
    image.show()
    image.close()


if __name__ == "__main__":
    instantialize_agents()
