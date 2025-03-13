# External imports
from typing import Dict
from random import randint
from re import sub

# Internal imports
from app.api.v1.game.generative_apis import (
    TextGeneration,
    ImageGeneration,
    SoundGeneration,
)
from app.api.v1.game.prompt_builder import PromptBuilder
from app.api.v1.validation.schemas import StoryActionSegment, GameSession


class GameContextManager:
    def __init__(self):
        # Instances
        self.text = TextGeneration()
        self.image = ImageGeneration()
        self.sound = SoundGeneration()
        self.prompt = PromptBuilder()

        # Variables
        self.previous_stories = []

    async def roll_dice(self, recent_scene: StoryActionSegment) -> Dict:
        """Determines dice threshold androlls dice"""
        # Get dice threshold from the story and action
        prompt = await self.prompt.get_dice_prompt(recent_scene)
        llm_output = await self.text.api_call(prompt)

        # Get threshold and roll
        threshold: int = await self._convert_dice_threshold_to_int(llm_output)
        roll: int = randint(1, 20)
        success: bool = roll >= threshold

        # Build the return response
        dice_results = {
            "dice_threshold": threshold,
            "dice_roll": roll,
            "dice_success": success,
        }

        return dice_results

    async def _convert_dice_threshold_to_int(self, llm_output: str) -> int:
        """Converts LLM output to integer dice threshold"""
        # Remove non-digit characters
        threshold = sub(r"[^0-9]", "", str(llm_output))

        # Default to 0 if no number found
        if threshold == "":
            return 0

        # Convert to int and cap at 20
        threshold = int(threshold)
        if threshold > 20:
            threshold = 20

        return threshold

    async def new_story(self, game_session: GameSession) -> Dict:
        """Gets prompt and makes API call"""
        # Get prompt and make API call
        prompt = self.prompt.get_story_prompt(game_session)
        new_story = await self.text.api_call(prompt)

        return new_story

    async def compress(self, story: str) -> str:
        """Uses LLM API to shorten the story"""
        prompt = await self.prompt.get_compress_prompt(story)
        compressed_story = await self.text.api_call(prompt)

        return compressed_story

    async def generate_image(self, story: str) -> str:
        """Builds prompt and returns image"""
        # Build the prompt for the LLM
        prompt_for_llm = await self.prompt.get_img_prompt(story)

        # Get the prompt optimized for stable diffusion
        prompt_for_sd = await self.text.api_call(prompt_for_llm)

        # Spice up the prompt with generic goodness
        spicy_prompt = (
            "highly detailed, masterpiece, 8k, photorealistic, "
            "sharp focus, volumetric lighting, professional color grading, "
            "cinematic lighting, perfect composition, " + prompt_for_sd
        )

        # Get the image (byte64 encoded)
        image = await self.image.api_call(spicy_prompt)

        return image

    async def analyze_mood(self, story: str) -> str:
        """Analyzes the mood of the story"""
        prompt = await self.prompt.get_mood_prompt(story)
        mood = await self.text.api_call(prompt)

        return mood
