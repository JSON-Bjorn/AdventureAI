from typing import Dict, Tuple
from src.api.generative_apis import (
    TextGeneration,
    ImageGeneration,
    SoundGeneration,
)
from src.api.prompt_builder import PromptBuilder
import random
import re
from io import BytesIO
from PIL import Image
import base64


class GameContextManager:
    def __init__(self):
        # Instances
        self.text = TextGeneration()
        self.image = ImageGeneration()
        self.sound = SoundGeneration()
        self.prompt = PromptBuilder()

        # Variables
        self.previous_stories = []

    async def roll_dice(self, recent_scene: Dict) -> Tuple[int, int, bool]:
        """Determines dice threshold androlls dice"""
        # Get dice threshold from the story and action
        prompt = self.prompt.get_dice_prompt(recent_scene)
        llm_output = await self.text.api_call(prompt)

        # Get threshold and roll
        threshold: int = await self._convert_dice_threshold_to_int(llm_output)
        roll: int = random.randint(1, 20)
        success: bool = roll >= threshold

        return (threshold, roll, success)

    async def _convert_dice_threshold_to_int(self, llm_output: str) -> int:
        """Converts LLM output to integer dice threshold"""
        # Remove non-digit characters
        threshold = re.sub(r"[^0-9]", "", str(llm_output))

        # Default to 0 if no number found
        if threshold == "":
            print("No threshold found, defaulting to 0")
            return 0

        # Convert to int and cap at 20
        threshold = int(threshold)
        if threshold > 20:
            threshold = 20

        return threshold

    async def new_story(self, all_scenes: Dict, dice: Tuple) -> Dict:
        """Gets prompt and makes API call"""
        # Get prompt and make API call
        prompt = self.prompt.get_story_prompt(all_scenes, dice)
        new_story = await self.text.api_call(prompt)

        return new_story

    async def compress(self, story: str) -> str:
        """Uses LLM API to shorten the story"""
        prompt = self.prompt.get_compress_prompt(story)
        compressed_story = await self.text.api_call(prompt)

        return compressed_story

    async def generate_image(self, story: str) -> str:
        """Generates image for the current story"""
        prompt = await self.prompt.get_img_prompt(story)
        image = await self.image.api_call(prompt)

        return image

    async def analyze_mood(self, story: str) -> str:
        """Analyzes the mood of the story"""
        prompt = self.prompt.get_mood_prompt(story)
        mood = await self.text.api_call(prompt)

        return mood
