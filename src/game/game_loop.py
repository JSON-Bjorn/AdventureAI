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
            # 1. Generate new story based on the previous action
            # (Skip on first iteration since we already have initial story)
            if self.context["current_scene"]["action"] is not None:
                self.context = await self.manager.generate_new_story(
                    self.context
                )
                print_context_state(self.context)

                # 2. Move completed scene to previous_scenes
                # (Do this right after generating new story)
                self.context = await self.manager.move_scenes(self.context)
                print_context_state(self.context)

            # 3. Generate image for the current story
            self.context = await self.manager.generate_image(self.context)
            print_context_state(self.context)

            # 4. Render the current scene (story + image)
            await self.manager.render_scene(self.context)
            print_context_state(self.context)

            # 5. Take user input (action) in response to the story
            self.context = await self.manager.take_user_input(self.context)
            print_context_state(self.context)

            # Check for exit command
            if self.context["current_scene"]["action"] == "quit":
                game_active = False
                break

            # 6. Handle dice roll if needed for the action
            self.context = await self.manager.handle_dice_roll(self.context)
            print_context_state(self.context)


# THIS IS OUTSIDE OF CLASS
def print_context_state(context: Dict):
    """Debug helper to print current context state"""
    debug_context = copy.deepcopy(context)
    if "image" in debug_context["current_scene"]:
        debug_context["current_scene"]["image"] = "[BASE64 IMAGE DATA]"
    print("\n" + "=-" * 10 + " CONTEXT STATE " + "=-" * 10)
    pprint.pprint(debug_context)
    print("=-" * 10 + " CONTEXT STATE " + "=-" * 10 + "\n")
