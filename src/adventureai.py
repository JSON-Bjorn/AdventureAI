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

import sys
import os
import asyncio
import pygame
import traceback

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.agents import (
    TextAgent,
    SoundAgent,
    IllustratorAgent,
    TriageAgent,
    MoodAnalyzer,
)
from src.utils.database import Database
from src.utils.dice_roller import DiceRoller
from src.utils.display_manager import DisplayManager


async def instantialize_agents():
    try:
        # Initialize display first
        display = DisplayManager()

        # Initial loading screen
        display.render_loading("Gathering the party...")
        pygame.display.flip()
        await asyncio.sleep(0.1)

        # Initialize basic components
        dice_roller = DiceRoller()
        author = TextAgent()
        narrator = SoundAgent()

        # Initialize illustrator
        display.render_loading("Summoning the illustrator...")
        pygame.display.flip()
        await asyncio.sleep(0.1)
        illustrator = IllustratorAgent()

        # Initialize mood analyzer
        display.render_loading("Consulting the sages...")
        pygame.display.flip()
        await asyncio.sleep(0.1)
        mood_analyzer = MoodAnalyzer()

        # Initialize dungeon master
        display.render_loading("Awakening the dungeon master...")
        pygame.display.flip()
        await asyncio.sleep(0.1)
        dungeon_master = await TriageAgent.create(
            author, narrator, illustrator, mood_analyzer
        )

        # Generate initial story
        display.render_loading("Writing your story's beginning...")
        pygame.display.flip()
        await dungeon_master.next_story()  # Generate first story segment

        # Update display with initial story and image
        display.update_story(dungeon_master.get_text())

        display.render_loading("Creating the first scene...")
        pygame.display.flip()
        display.update_image(dungeon_master.get_image())

        # Play initial voiceover and music
        display.render_loading("Setting the mood...")
        pygame.display.flip()
        voiceover = dungeon_master.get_voiceover()
        if voiceover:
            voiceover.play_audio()

        # Clear loading status and render initial state
        display.set_loading_status("")
        display.render()
        pygame.display.flip()

        print("Starting game loop...")

        # Start the game loop
        try:
            await game_loop(dice_roller, dungeon_master, display)
        except Exception as e:
            print(f"Error in game loop: {e}")
            raise

    except Exception as e:
        print("\nError during initialization:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()

    finally:
        if "illustrator" in locals():
            await illustrator.cleanup()
        pygame.quit()


async def game_loop(dice_roller, dungeon_master, display):
    game_active = True
    clock = pygame.time.Clock()

    try:
        while game_active:
            # Clear any previous loading status
            display.set_loading_status("")

            # Input handling loop
            player_choice = None
            while player_choice is None and game_active:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_active = False
                        display.save_window_position()
                        break

                    player_choice = display.handle_input(event)

                display.render()
                clock.tick(60)

            if not game_active or player_choice.lower().strip() == "exit":
                break

            # Store the player's choice in the dungeon master
            dungeon_master.player_choice = player_choice

            # Check if action needs a dice roll
            display.set_loading_status("Evaluating action difficulty...")
            dice_roll_needed = dice_roller.assess_situation(
                dungeon_master.current_story, player_choice
            )

            if dice_roll_needed:
                # First, show the required roll and prompt
                roll_text = (
                    f"To do that, you need to roll {dice_roll_needed} or higher.\n\n"
                    "Press SPACE or click the dice to roll!"
                )
                display.update_story(roll_text)
                display.set_dice_button_active(True)
                display.set_loading_status("Awaiting your roll...")
                display.render()

                # Wait for spacebar or dice button click
                waiting_for_roll = True
                while waiting_for_roll and game_active:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            game_active = False
                            waiting_for_roll = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                waiting_for_roll = False
                        else:
                            result = display.handle_input(event)
                            if result == "ROLL_DICE":
                                waiting_for_roll = False
                    display.render()
                    clock.tick(60)

                # Hide dice button
                display.set_dice_button_active(False)

                if game_active:
                    display.set_loading_status("Rolling the dice...")
                    display.update_story("Rolling the dice...")
                    display.render()
                    pygame.time.wait(500)

                    # Now roll and show result
                    (success, player_roll) = dice_roller.roll_dice(
                        dice_roll_needed
                    )
                    roll_result = (
                        f"You rolled a {player_roll}!\n"
                        f"(Needed {dice_roll_needed} or higher)\n\n"
                        f"{'Success!' if success else 'Failed!'}"
                    )
                    display.update_story(roll_result)
                    display.render()

                    # Update dungeon master with roll result
                    dungeon_master.success = success

                    # Pause to show result before continuing
                    pygame.time.wait(2000)
            else:
                # If no roll needed, consider it a success
                dungeon_master.success = True

            # Generate next story segment
            display.set_loading_status("Writing the next chapter...")
            await dungeon_master.next_story()

            # Generate image for the new scene
            display.set_loading_status("Painting the scene...")
            display.update_story(dungeon_master.get_text())
            display.update_image(dungeon_master.get_image())

            # Generate audio
            display.set_loading_status("Creating voice narration...")
            voiceover = dungeon_master.get_voiceover()
            if voiceover:
                voiceover.play_audio()

            # Clear loading status when everything is ready
            display.set_loading_status("")

            # Now that everything is ready, clear the input
            display.clear_input()

    finally:
        # Ensure window position is saved even if there's an error
        display.save_window_position()


def play_voiceover(audio):
    # Implement audio playback here if needed
    pass


if __name__ == "__main__":
    try:
        # Set up asyncio event loop policy for Windows
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy()
            )

        print("Starting AdventureAI...")
        asyncio.run(instantialize_agents())

    except Exception as e:
        print("\nCritical error:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()

    finally:
        print("\nCleaning up...")
        if "narrator" in locals():
            narrator.stop_background_music()
        pygame.quit()

        # Keep window open if there was an error
        if sys.exc_info()[0] is not None:
            input("\nPress Enter to exit...")

        sys.exit()
