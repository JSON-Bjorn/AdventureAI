import os
import asyncio
import uuid
from typing import Optional, List, Dict
from io import BytesIO

from agents import (
    TriageAgent,
    AuthorAgent,
    CompressorAgent,
    MoodAnalyzer,
    DiceRoller,
    PromptAgent,
    ImageAgent,
    SoundAgent,
)
from utils import ResourceManager
from utils.dice_roller import DiceRoller
from database_operations import DatabaseOperations

# Det här är basically BARA game loop


class GameSession:
    def __init__(self, user_id: str, new_game: bool):
        # Object for database operations
        self.db_ops = DatabaseOperations()

        # User and gameplay data
        self.game_active = True
        self.user_id = user_id
        self.current_image = None
        self.current_mood = None
        self.current_audio = None
        self.current_story = None
        self.context = {
            "protagonist_name": "Linus Torvalds",
            "action": "Saving the world one open source project at a time",
            "inventory": ["Materialized Linux kernel"],
            "story": {
                "current": "Our protagonist is sitting alone in a gloomy, dank room. Typing away on their keyboard.",
                "previous": [],
            },
            "dice_roll": {
                "needed": False,
                "required_roll": 0,
            },
            "mood": {
                1: "calm",
                2: "adventerous",
            },
        }

        # Agents
        self.triage = TriageAgent()  # Mistral
        self.author = AuthorAgent()  # Mistral
        self.compressor = CompressorAgent()  # Mistral
        self.mood = MoodAnalyzer()  # Mistral
        self.dice = DiceRoller()  # Mistral
        self.prompter = PromptAgent()  # Mistral
        self.image = ImageAgent()  # Stable Diffusion
        self.sound = SoundAgent()  # TTS and music

        # Get or create new context
        if new_game:
            self.initialize_context()
        else:
            self.db_ops.load_game(self.game_id)

    # -- MAIN GAME METHODS --
    async def game_loop(self):
        """Main game loop"""
        while self.game_active is True:
            # Gather information for the scene
            await self.take_user_input()
            await self.dice.determine_dice_roll(self.context["story"][0])

            # Check if game is over
            if self.game_active is False:
                break

            # Generate current scene
            scene = await self.build_current_scene()
            await self.render_scene(self, scene)
            await self.process_context(scene)

            # Compress the context
            self.context = self.compressor.compress_context(self.context)

    async def build_current_scene(self):
        """Builds the current scene"""
        current_story = self.context["story"][
            "current"
        ] = await self.author.generate_story(self.context)
        prompt = await self.prompter.generate_prompt(current_story)
        image = await self.image.generate_image(prompt)
        mood = await self.mood.analyze_mood(current_story)
        music = await self.sound.fetch_music(mood)
        speech = await self.sound.generate_speech(current_story)
        return {
            "story": current_story,
            "image": image,
            "music": music,
            "speech": speech,
        }

    async def render_scene(self, scene: Dict):
        """Renders the current scene"""
        pass

    async def take_user_input(self):
        """Takes user input and stores to context"""
        # Could we just wait here until an endpoint is pinged and then return that??

        # take user input
        # self.context["action"] = user_input
        pass

    # -- GET/POST RELATED METHODS --

    async def initialize_context(self):
        """Prompts the user to fill out the context dict"""

        context = {}
        self.context = context
