# External imports
from typing import Dict, List
from difflib import get_close_matches

# Internal imports
from app.api.v1.game.instructions import instructions
from app.api.v1.validation.schemas import StoryActionSegment, GameSession
from app.api.logger.loggable import Loggable


class PromptBuilder(Loggable):
    """Class that handles all prompt building before a LLM-call"""

    def __init__(self):
        super().__init__()  # self.logger
        self.instructions = instructions
        self.logger.info("PromptBuilder initialized")

    async def get_dice_prompt(self, recent_scene: StoryActionSegment):
        """Builds the prompt for the dice roll"""
        self.logger.info(
            f"Building dice prompt for action: {recent_scene.action}"
        )
        # Dissect context and get instructions
        instructions = self.instructions["determine_dice_roll"]
        story = recent_scene.story
        action = recent_scene.action

        prompt = (
            f"Instructions: {instructions}\n\n"
            f"Story: {story}\n"
            f"Action: {action}\n"
        )
        self.logger.debug(f"Dice prompt built (prompt length: {len(prompt)})")
        return prompt

    def get_story_prompt(self, game_session: GameSession) -> str:
        """Builds the prompt for new stories"""
        self.logger.info("Building story prompt")
        # Define variables
        instructions: str = self.instructions["generate_story"]
        name: str = game_session.protagonist_name
        inv: str = ", ".join(game_session.inventory)
        recent_scenes: List[Dict] = game_session.scenes[-10:]
        action: str = recent_scenes[-1]["action"]
        success: bool = recent_scenes[-1]["dice_success"]

        # Format the prompt
        prompt = (
            f"Instructions: {instructions}\n\n"
            f"Protagonist name: {name}\n"
            f"Protagonist's inventory: {inv}\n\n"
            "The story so far:\n"
        )
        # Add the 10 last stories in chronological order to prompt
        for i, scene in enumerate(recent_scenes, 1):
            prompt += f"Story {i}: {scene['story']}\n\n"

        # Add the current action and its success (this is what we're generating a story for)
        prompt += f"Protagonist's action based on the last story: {action}\n"
        prompt += f"Action successful: {success}\n\n"
        prompt += f"Story {len(recent_scenes) + 1}: Please write this story based on what just happened.\n\n"

        self.logger.debug(f"Story prompt built with length: {len(prompt)})")
        return prompt

    async def get_compress_prompt(self, story: str):
        """Builds the prompt for compressing a story"""
        self.logger.info(
            f"Building compression prompt for story with length: {len(story)})"
        )
        instructions = self.instructions["compress_story"]
        prompt = f"Instructions: {instructions}\n" f"Story: {story}"
        self.logger.debug(
            f"Compression prompt built with length: {len(prompt)})"
        )
        return prompt

    async def get_img_prompt(self, story: str):
        """Build the prompt for image generation"""
        self.logger.info(
            f"Building image prompt for story with length: {len(story)})"
        )
        # Get instructions and prompt
        instructions = self.instructions["image_prompt"]
        prompt = f"""
            Instructions: {instructions}

            Story: {story}
        """
        self.logger.debug(f"Image prompt built with length: {len(prompt)})")
        return prompt

    async def get_mood_prompt(self, story: str):
        """Build the prompt for mood analysis"""
        self.logger.info(
            f"Building mood analysis prompt for story with length: {len(story)})"
        )
        # Get instructions and prompt
        instructions = self.instructions["analyze_mood"]
        prompt = f"Instructions: {instructions}\nStory: {story}"

        # Validate prompt
        validated_prompt = self._validate_mood_prompt(prompt)
        self.logger.debug(
            f"Mood analysis prompt built and validated (prompt length: {len(validated_prompt)})"
        )
        return validated_prompt

    def _validate_mood_prompt(self, prompt: str) -> str:
        """Validates the mood prompt"""
        self.logger.debug(f"Validating mood prompt: {prompt[:100]}...")
        # Mood-map
        valid_combinations = {
            "calm": ["adventerous", "dreamy", "mystical", "serene"],
            "medium": [
                "lurking",
                "nervous",
                "ominous",
                "playful",
                "quirky",
                "upbeat",
            ],
            "intense": ["chaotic", "combat", "epic", "scary"],
        }

        try:
            # Split the prompt
            parts = prompt.split("/")
            if len(parts) == 2:
                first, second = parts
            else:
                self.logger.warning(
                    f"Invalid mood prompt format: {prompt}, using default"
                )
                return "calm/adventerous"

            # Lowercase the parts
            first = first.lower()
            second = second.lower()

            # Check for close matches using difflib
            first_results = get_close_matches(
                first, valid_combinations.keys()
            )
            if first_results:
                first = first_results[0]
                self.logger.debug(
                    f"Matched first part '{first}' to valid mood intensity"
                )
            else:
                self.logger.warning(
                    f"No match found for mood intensity '{first}', using default"
                )
                first = "calm"

            second_results = get_close_matches(
                second, valid_combinations[first]
            )
            if second_results:
                second = second_results[0]
                self.logger.debug(
                    f"Matched second part '{second}' to valid mood type"
                )
            else:
                self.logger.warning(
                    f"No match found for mood type '{second}', using default"
                )
                second = valid_combinations[first][0]

            # Check if the second part is valid
            if second not in valid_combinations[first]:
                self.logger.warning(
                    f"Invalid mood combination: {first}/{second}, using default"
                )
                second = valid_combinations[first][0]

            validated_mood = f"{first}/{second}"
            self.logger.info(f"Validated mood: {validated_mood}")
            return validated_mood

        except Exception as e:
            self.logger.error(f"Error validating mood prompt: {str(e)}")
            return "calm/adventerous"
