"""
AdventureAI - An AI-Powered Choose Your Own Adventure Game

Main Game Architecture and Flow Controller

Core Components:
    Text Generation:
    Image Generation:
    Sound Generation:
    Database:

Game Flow:
    1. Character Creation:
    2. Story Progression:
    3. Action Resolution:
    4. Death Handling:

Technical Features:


Usage:
    Run directly to start game:
    `python adventureai.py`

Requirements:
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
import asyncio


async def instantialize_agents():
    dice_roller = DiceRoller()
    author = TextAgent()
    narrator = SoundAgent()
    illustrator = IllustratorAgent()
    dungeon_master = await TriageAgent.create(author, narrator, illustrator)
    await game_loop(dice_roller, dungeon_master)
    illustrator.cleanup()  # Cleans the pipeline when the game loop breaks


async def game_loop(dice_roller, dungeon_master):
    game_active = True
    while game_active:
        await dungeon_master.next_story()

        text = dungeon_master.get_text()
        show_text(text)
        audio = dungeon_master.get_voiceover()
        play_voiceover(audio)
        image = dungeon_master.get_image()
        show_image(image)

        player_choice: str = dungeon_master.player_turn()

        if player_choice.lower().strip() == "exit":
            game_active = False
            continue

        dice_roll_needed: int = dice_roller.assess_situation(
            dungeon_master.current_story, player_choice
        )

        if dice_roll_needed:
            show_text(f"\nTo do that, you must roll {dice_roll_needed}")
            input("Roll dice!\n")
            (success, player_roll) = dice_roller.roll_dice(dice_roll_needed)
            show_text(f"You rolled a: {player_roll}!\n")
            dungeon_master.success = success


def show_text(text):
    print("\n" * 20)
    print(f"\n{text}")


def play_voiceover(audio):
    pass


def show_image(image):
    if image:
        image.show()
    else:
        print("No image was store in the Triage class")


if __name__ == "__main__":
    asyncio.run(instantialize_agents())
