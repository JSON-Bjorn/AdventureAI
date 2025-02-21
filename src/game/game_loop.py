import os
import asyncio
import uuid
from typing import Optional, List, Dict
from io import BytesIO
import pprint

from src.api.generative_apis import (
    TextGeneration,
    ImageGeneration,
    SoundGeneration,
)
from src.game.game_functionality import GameFunctionality
from src.game.context_manager import ContextManager
# from src.database.database_operations import DatabaseOperations


class GameSession:
    def __init__(self, user_id: str, new_game: bool):
        # Object for database operations
        # self.db_ops = DatabaseOperations()

        # User and gameplay data
        self.context = {}

        # Functionality classes
        self.context_manager = ContextManager()
        self.game_functionality = GameFunctionality()

        # APIs
        self.text = TextGeneration()
        self.image = ImageGeneration()
        self.sound = SoundGeneration()

        # Get or create new context
        if new_game:
            self.context = (
                self.game_functionality.gather_new_user_information()
            )
        else:
            self.context = self.db_ops.load_game(self.user_id)

    # -- MAIN GAME METHODS --
    async def game_loop(self):
        """Main game loop"""
        while self.game_active is True:
            print_context_state(self.context)  # DEBUG

            # Define the CURRENT action
            self.context = await self.game_functionality.take_user_input(
                context=self.context
            )

            print_context_state(self.context)  # DEBUG

            # Define the CURRENT dice roll (threshold and success)
            self.context = await self.context_manager.handle_dice_roll(
                context=self.context
            )
            # CURRENT SCENE IS NOW COMPLETE

            # Move CURRENT to PREVIOUS
            self.context = (
                await self.context_manager.append_to_previous_stories(
                    context=self.context
                )
            )

            print_context_state(self.context)  # DEBUG

            # Define the NEW scene
            scene = await self.context_manager.build_current_scene(
                context=self.context
            )
            await self.game_functionality.render_scene(scene)

            # Compress the CURRENT story
            self.context = await self.text.compress_current_story(
                context=self.context
            )

            print_context_state(self.context)  # DEBUG

    async def game_loop_2(self):
        """Main game loop"""
        self.context = self.game_functionality.pick_initial_story()
        while self.game_active is True:
            # Generate story from context
            await self.image.generate_image(self.context)
            await self.game_functionality.render_scene(self.context)


# THIS IS OUTSIDE OF CLASS
def print_context_state(context: Dict):
    """I dont know how to use the debugger"""
    print("\n" + "=-" * 10 + " CONTEXT STATE " + "=-" * 10)
    pprint.pprint(f"Current context state: {context}")
    print("=-" * 10 + " CONTEXT STATE " + "=-" * 10 + "\n")
