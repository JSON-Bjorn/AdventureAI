import os
import asyncio
import uuid
from typing import Optional, List, Dict, Tuple
from io import BytesIO
import pprint
import copy

from src.api.generative_apis import (
    TextGeneration,
    ImageGeneration,
    SoundGeneration,
)
from src.game.context_manager import GameContextManager
from src.database.database_operations import DatabaseOperations


class GameSession:
    def __init__(self):
        # Instances
        self.db_ops = DatabaseOperations()
        self.manager = GameContextManager()

    async def get_next_scene(self, game_session: Dict):
        """
        Takes context as input and sends new context as output
        """
        # Dissect the game session
        # name = game_session["protagonist_name"]
        # inv = game_session["inventory"]
        all_scenes: List[Dict] = game_session["scenes"]
        recent_scene: Dict[str] = all_scenes[-1]

        # Roll dice on players action
        starting_point = recent_scene.get("starting_point", False)
        if starting_point is True:
            dice = (threshold, roll, success) = (0, 1, True)
        elif starting_point is False:
            dice = (threshold, roll, success) = await self.manager.roll_dice(
                recent_scene
            )

        # Generate a new story and compress it
        new_story: str = await self.manager.new_story(game_session, dice)
        compressed_story: str = await self.manager.compress(story=new_story)

        # Image
        image: str = await self.manager.generate_image(new_story)

        # Mood
        music_path: str = await self.manager.analyze_mood(new_story)

        # Build the return response
        return_response = {
            "story": new_story,
            "compressed_story": compressed_story,
            "image": image,
            "music": music_path,
            "dice_threshold": threshold,
            "dice_success": success,
            "dice_roll": roll,
        }

        return return_response

    async def save_game(self, game_session: Dict):
        """Saves the game to the database"""
        pass
