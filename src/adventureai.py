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
    MoodAnalyzer,
)
from utils.database import Database
from utils.dice_roller import DiceRoller
from utils.display_manager import DisplayManager
import pygame
import asyncio
import sys
import traceback


async def instantialize_agents():
    try:
        display = DisplayManager()
        display.render_loading("Gathering the party...")
        pygame.display.flip()

        dice_roller = DiceRoller()
        author = TextAgent()
        narrator = SoundAgent()

        display.render_loading("Summoning the illustrator...")
        pygame.display.flip()
        illustrator = IllustratorAgent()

        display.render_loading("Consulting the sages...")
        pygame.display.flip()
        mood_analyzer = MoodAnalyzer()

        display.render_loading("Awakening the dungeon master...")
        pygame.display.flip()
        dungeon_master = await TriageAgent.create(
            author, narrator, illustrator, mood_analyzer
        )

        display.render_loading("Opening the storybook...")
        pygame.display.flip()

        print("Starting game loop...")
        await game_loop(dice_roller, dungeon_master, display)

    except Exception as e:
        print("\nError during initialization:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()

    finally:
        if "illustrator" in locals():
            illustrator.cleanup()


async def game_loop(dice_roller, dungeon_master, display):
    game_active = True
    clock = pygame.time.Clock()

    try:
        while game_active:
            display.set_loading_status("Writing the next chapter...")
            await dungeon_master.next_story()

            # Update display with new story and image
            display.update_story(dungeon_master.get_text())

            display.set_loading_status("Painting the scene...")
            display.update_image(dungeon_master.get_image())

            # Play voiceover for new story
            display.set_loading_status("Giving voice to the tale...")
            voiceover = dungeon_master.get_voiceover()
            if voiceover:
                voiceover.play_audio()

            # Clear loading status when everything is ready
            display.set_loading_status("")

            # Input handling loop
            player_choice = None
            while player_choice is None and game_active:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_active = False
                        # Save window position before breaking
                        display.save_window_position()
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
                # First, show the required roll and prompt
                roll_text = (
                    f"To do that, you need to roll {dice_roll_needed} or higher.\n\n"
                    "Press SPACE or click the dice to roll!"
                )
                display.update_story(roll_text)
                display.set_dice_button_active(True)  # Show dice button
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
                    # Show rolling animation/text
                    display.update_story("Rolling the dice...")
                    display.render()
                    pygame.time.wait(500)  # Brief pause for drama

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

                    # Show that we're generating the next part
                    display.set_loading_status("Writing the next chapter...")
                    display.render()
            else:
                # If no roll needed, consider it a success
                dungeon_master.success = True

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
