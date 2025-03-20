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
from app.api.logger.loggable import Loggable


class GameContextManager(Loggable):
    def __init__(self):
        super().__init__()  # Initialize the logger
        # Instances
        self.text = TextGeneration()
        self.image = ImageGeneration()
        self.sound = SoundGeneration()
        self.prompt = PromptBuilder()

        # Variables
        self.previous_stories = []
        self.logger.info("GameContextManager initialized")

    async def roll_dice(self, recent_scene: StoryActionSegment) -> Dict:
        """Determines dice threshold androlls dice"""
        self.logger.info(f"Rolling dice for action: {recent_scene.action}")
        # Get dice threshold from the story and action
        prompt = await self.prompt.get_dice_prompt(recent_scene)
        self.logger.debug(f"Dice threshold prompt: {prompt}")
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
        self.logger.info(
            f"Dice results: threshold={threshold}, roll={roll}, success={success}"
        )

        return dice_results

    async def _convert_dice_threshold_to_int(self, llm_output: str) -> int:
        """Converts LLM output to integer dice threshold"""
        self.logger.debug(f"Converting LLM output to integer: '{llm_output}'")
        # Remove non-digit characters
        threshold = sub(r"[^0-9]", "", str(llm_output))

        # Default to 0 if no number found
        if threshold == "":
            self.logger.warning(
                f"No number found in LLM output: '{llm_output}', defaulting to 0"
            )
            return 0

        # Convert to int and cap at 20
        threshold = int(threshold)
        if threshold > 20:
            self.logger.debug(
                f"Threshold {threshold} exceeds maximum (20), capping at 20"
            )
            threshold = 20

        return threshold

    async def new_story(self, game_session: GameSession) -> Dict:
        """Gets prompt and makes API call"""
        self.logger.info("Generating new story")
        # Get prompt and make API call
        prompt = self.prompt.get_story_prompt(game_session)
        new_story = await self.text.api_call(prompt)
        self.logger.info(f"New story generated (length: {len(new_story)})")

        return new_story

    async def compress(self, story: str) -> str:
        """Uses LLM API to shorten the story"""
        self.logger.info(f"Compressing story (original length: {len(story)})")
        prompt = await self.prompt.get_compress_prompt(story)
        compressed_story = await self.text.api_call(prompt)
        self.logger.info(
            f"Story compressed (new length: {len(compressed_story)})"
        )

        return compressed_story

    async def generate_image(self, story: str) -> str:
        """Builds prompt and returns image"""
        self.logger.info("Generating image for story")
        # Build the prompt for the LLM
        prompt_for_llm = await self.prompt.get_img_prompt(story)

        # Get the prompt optimized for stable diffusion
        prompt_for_sd = await self.text.api_call(prompt_for_llm)
        self.logger.debug(
            f"Stable diffusion prompt(non-spicy) received: {prompt_for_sd}"
        )

        # Spice up the prompt with generic goodness
        spicy_prompt = (
            "highly detailed, masterpiece, 8k, photorealistic, "
            "sharp focus, volumetric lighting, professional color grading, "
            "cinematic lighting, perfect composition, " + prompt_for_sd
        )

        # Get the image (byte64 encoded)
        self.logger.debug("Sending request to image generation API")
        image = await self.image.api_call(spicy_prompt)
        self.logger.info("Image successfully generated")

        return image

    async def analyze_mood(self, story: str) -> str:
        """Analyzes the mood of the story and returns path to appropriate music"""
        self.logger.info("Analyzing mood of story for music selection")
        prompt = await self.prompt.get_mood_prompt(story)
        mood = await self.text.api_call(prompt)
        self.logger.debug(f"Mood analysis LLM output: {mood}")

        music_path = await self.sound.api_call(mood)
        self.logger.info(f"Music path after validation: {music_path}")

        return music_path
