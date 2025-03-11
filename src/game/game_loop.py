from typing import List, Dict

from src.api.generative_apis import (
    TextGeneration,
    ImageGeneration,
    SoundGeneration,
)
from src.game.context_manager import GameContextManager
from src.database.database_operations import DatabaseOperations
from src.schemas.schemas import StoryActionSegment, GameSession


class SceneGenerator:
    def __init__(self):
        # Instances
        self.db_ops = DatabaseOperations()
        self.manager = GameContextManager()

    async def get_dice_info(self, story: StoryActionSegment):
        """Rolls the dice and returns the result"""
        return await self.manager.roll_dice(story)

    async def get_next_scene(self, game_session: GameSession):
        """
        Takes context as input and sends new context as output
        """
        # Builds prompts, makes API calls and generates the new scene
        story: str = await self.manager.new_story(game_session)
        compressed_story: str = await self.manager.compress(story)
        image: str = await self.manager.generate_image(story)
        music_path: str = await self.manager.analyze_mood(story)

        return {
            "story": story,
            "compressed_story": compressed_story,
            "image": image,
            "music": music_path,
        }

    async def save_game(self, game_session: Dict):
        """Saves the game to the database"""
        pass
