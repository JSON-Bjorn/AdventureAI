import os
import asyncio
import uuid
from typing import Optional, List, Dict
from io import BytesIO
import pprint
import copy

from src.api.generative_apis import (
    TextGeneration,
    ImageGeneration,
    SoundGeneration,
)
from src.game.game_functionality import GameFunctionality
from src.game.context_manager import GameContextManager
# from src.database.database_operations import DatabaseOperations


class GameSession:
    def __init__(self, user_id: str, new_game: bool):
        # Object for database operations
        # self.db_ops = DatabaseOperations()

        # User and gameplay data
        self.context = {}

        # Functionality classes
        self.manager = GameContextManager()

        # APIs
        self.text = TextGeneration()
        self.image = ImageGeneration()
        self.sound = SoundGeneration()

        # Get or create new context
        if new_game:
            self.context = self.manager.pick_initial_story()
        else:
            self.context = self.db_ops.load_game(self.user_id)

    # -- MAIN GAME METHODS --

    async def game_loop(self):
        """Main game loop"""
        game_active = True
        while game_active is True:
            # Story already exists in context/current scene
            # Generate image, put it in current scene
            self.context = await self.manager.generate_image(self.context)
            # Also here is where we need to get tts, the music and so on..
            print_context_state(self.context)

            # Render current scene
            await self.manager.render_scene(self.context)
            print_context_state(self.context)

            # Move current scene to previous
            self.context = await self.manager.move_scenes(self.context)
            print_context_state(self.context)

            # Take user input, add to current scene
            self.context = await self.manager.take_user_input(self.context)
            print_context_state(self.context)

            # Check for exit command
            if self.context["current_scene"]["action"] == "quit":
                game_active = False
            print_context_state(self.context)

            # Roll dice, add to current scene
            self.context = await self.manager.handle_dice_roll(self.context)
            print_context_state(self.context)

            # Generate story, add to current scene
            self.context = await self.manager.generate_new_story(self.context)
            print_context_state(self.context)


# THIS IS OUTSIDE OF CLASS
def print_context_state(context: Dict):
    """I dont know how to use the debugger"""
    debug_context = copy.deepcopy(context)
    debug_context["current_scene"]["image"] = (
        "BING BONG CHING CHONG mvh deepseek AB"
    )
    print("\n" + "=-" * 10 + " CONTEXT STATE " + "=-" * 10)
    pprint.pprint(f"Current context state: {debug_context}")
    print("=-" * 10 + " CONTEXT STATE " + "=-" * 10 + "\n")
