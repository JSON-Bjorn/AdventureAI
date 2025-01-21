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
from utils.display_manager import DisplayManager
import pygame
import asyncio
import sys


async def instantialize_agents():
    dice_roller = DiceRoller()
    author = TextAgent()
    narrator = SoundAgent()
    illustrator = IllustratorAgent()
    dungeon_master = await TriageAgent.create(author, narrator, illustrator)

    display = DisplayManager()

    await game_loop(dice_roller, dungeon_master, display)
    illustrator.cleanup()


async def game_loop(dice_roller, dungeon_master, display):
    game_active = True
    clock = pygame.time.Clock()

    while game_active:
        await dungeon_master.next_story()

        # Update display with new story and image
        display.update_story(dungeon_master.get_text())
        display.update_image(dungeon_master.get_image())

        # Handle audio if implemented
        audio = dungeon_master.get_voiceover()
        if audio:
            play_voiceover(audio)

        # Input handling loop
        player_choice = None
        while player_choice is None and game_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_active = False
                    break

                player_choice = display.handle_input(event)

            display.render()
            clock.tick(60)

        if not game_active or player_choice.lower().strip() == "exit":
            break

        # Store the player's choice in the dungeon master
        dungeon_master.player_choice = player_choice

        # Handle dice rolls
        dice_roll_needed = dice_roller.assess_situation(
            dungeon_master.current_story, player_choice
        )

        if dice_roll_needed:
            # Clear and show dice roll requirement
            roll_text = (
                f"To do that, you must roll {dice_roll_needed}\n\n"
                "Press any key to roll the dice!"
            )
            display.update_story(roll_text)
            display.render()

            # Wait for any key press to roll
            waiting_for_roll = True
            while waiting_for_roll:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        waiting_for_roll = False
                    elif event.type == pygame.QUIT:
                        game_active = False
                        waiting_for_roll = False
                clock.tick(60)

            if game_active:
                (success, player_roll) = dice_roller.roll_dice(
                    dice_roll_needed
                )
                # Clear and show roll result
                roll_result = f"You rolled a: {player_roll}!"
                display.update_story(roll_result)
                display.render()

                # Update dungeon master with roll result
                dungeon_master.success = success

                # Brief pause to show roll result
                pygame.time.wait(1000)
        else:
            # If no roll needed, consider it a success
            dungeon_master.success = True


def play_voiceover(audio):
    # Implement audio playback here if needed
    pass


if __name__ == "__main__":
    try:
        asyncio.run(instantialize_agents())
    finally:
        pygame.quit()
        sys.exit()
