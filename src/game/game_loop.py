import os
import asyncio
import uuid
from typing import Optional, List, Dict
from io import BytesIO

from src.api.generative_apis import (
    TextGeneration,
    ImageGeneration,
    SoundGeneration,
)
from src.game.game_functionality import (
    roll_dice,
    render_scene,
    take_user_input,
    gather_new_user_information,
)
# from src.database.database_operations import DatabaseOperations


class GameSession:
    def __init__(self, user_id: str, new_game: bool):
        # Object for database operations
        # self.db_ops = DatabaseOperations()

        # User and gameplay data
        self.game_active = True
        self.user_id = user_id
        self.current_image = None
        self.current_mood = None
        self.current_audio = None
        self.current_story = None
        # If everything goes right, Linus should never be the protagonist
        self.context = {
            "protagonist_name": "Linus Torvalds",
            "inventory": ["Materialized Linux kernel"],
            "current_scene": {
                "story": "Linus Torvalds has trancended into godhood!",
                "action": "git push AGI to public repo",
                "dice_threshhold": None,
                "dice_success": None,
            },
            "previous_scenes": [
                {
                    "story": "Linus is coding",
                    "action": "I trancend into godhood",
                    "dice_threshhold": 20,
                    "dice_success": True,
                },
            ],
            "mood": {
                1: "calm",
                2: "adventerous",
            },
        }

        # APIs
        self.text = TextGeneration()
        self.image = ImageGeneration()
        self.sound = SoundGeneration()

        # Get or create new context
        if new_game:
            self.context = gather_new_user_information()
        else:
            self.context = self.db_ops.load_game(self.user_id)

    # -- MAIN GAME METHODS --
    async def game_loop(self):
        """Main game loop"""
        while self.game_active is True:
            # Check if game is over
            if self.game_active is False:
                break

            # Take user input and add to context
            self.context["current_scene"]["action"] = await take_user_input()

            # Determine dice roll threshhold and add to context
            dice_threshhold = await self.text.determine_dice_roll(
                self.context
            )
            self.context["current_scene"]["dice_threshhold"] = dice_threshhold
            print(f"RAW OUTPUT OF dice_threshhold: {dice_threshhold}")

            # Roll the dice and add to context
            # This needs to be done when user clicks button
            self.context["current_scene"]["dice_success"] = roll_dice(
                self.context["current_scene"]["dice_threshhold"]
            )

            # Below here in prod lol

            # Generate current scene
            scene = await self.build_current_scene()
            await self.render_scene(self, scene)
            self.context = await self.update_context(scene)

            # Compress the context
            self.context = self.text.compress_context(self.context)

            # Clear the current scene
            self.context["current_scene"] = {}

    async def build_current_scene(self):
        """Builds the current scene"""
        current_story = await self.text.generate_story(self.context)
        img_prompt = await self.text.generate_prompt(self.context)
        image = await self.image.stable_diffusion_call(img_prompt)
        # mood = await self.text.analyze_mood(current_story)
        # music = await self.sound.fetch_music(mood)
        # speech = await self.sound.generate_speech(current_story)

        return {
            "story": current_story,
            "image": image,
            "mood": None,
            "music": None,
            "speech": None,
        }
