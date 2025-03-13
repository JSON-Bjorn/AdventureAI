from typing import Dict, List, Tuple

# Internal imports
from app.api.v1.game.instructions import instructions
from app.api.v1.validation.schemas import StoryActionSegment, GameSession


class PromptBuilder:
    """Class that handles all prompt building before a LLM-call"""

    def __init__(self):
        self.instructions = instructions

    async def get_dice_prompt(self, recent_scene: StoryActionSegment):
        """Builds the prompt for the dice roll"""
        # Dissect context and get instructions
        instructions = self.instructions["determine_dice_roll"]
        story = recent_scene.story
        action = recent_scene.action

        prompt = (
            f"Instructions: {instructions}\n\n"
            f"Story: {story}\n"
            f"Action: {action}\n"
        )
        return prompt

    def get_story_prompt(self, game_session: GameSession) -> str:
        """Builds the prompt for new stories"""
        # Define variables
        instructions: str = self.instructions["generate_story"]
        name: str = game_session.protagonist_name
        inv: str = ", ".join(game_session.inventory)
        scenes: List[Dict] = game_session.scenes
        action: str = scenes[-1]["action"]
        success: bool = scenes[-1]["dice_success"]

        # Format the prompt
        prompt = (
            f"Instructions: {instructions}\n\n"
            f"Protagonist name: {name}\n"
            f"Protagonist's inventory: {inv}\n\n"
            "The story so far:\n"
        )
        # Add all previous stories in chronological order
        for i, scene in enumerate(scenes, 1):
            prompt += f"Story {i}: {scene['story']}\n\n"
            # Add logic that only allows 10 stories to be added
            # Cant pick them from the  top, must pick from bottom
            # Maybe just splice before?

        # Add the current action and its success (this is what we're generating a story for)
        prompt += f"Protagonist's action based on the last story: {action}\n"
        prompt += f"Action successful: {success}\n\n"
        prompt += f"Story {len(scenes) + 1}: Please write this story based on what just happened.\n\n"

        return prompt

    async def get_compress_prompt(self, story: str):
        """Builds the prompt for compressing a story"""
        instructions = self.instructions["compress_story"]
        prompt = f"Instructions: {instructions}\n" f"Story: {story}"
        return prompt

    async def get_img_prompt(self, story: str):
        """Build the prompt for image generation"""
        # Get instructions and prompt
        instructions = self.instructions["image_prompt"]
        prompt = f"""
            Instructions: {instructions}

            Story: {story}
        """
        return prompt

    async def get_mood_prompt(self, story: str):
        """Build the prompt for mood analysis"""
        # Get isntructions and prompt
        instructions = self.instructions["analyze_mood"]
        prompt = f"Instructions: {instructions}\nStory: {story}"

        # Validate prompt
        validated_prompt = self._validate_mood_prompt(prompt)
        return validated_prompt

    def _validate_mood_prompt(self, prompt: str) -> str:
        """Validates the mood prompt"""
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
            parts = prompt.split("/")

            if len(parts) == 2:
                first, second = parts
            else:
                return "calm/adventerous"

            first = first.lower()
            second = second.lower()

            if second not in valid_combinations[first]:
                return "calm/adventerous"

            return prompt
        except Exception:
            # Yes this should be broad.
            return "calm/adventerous"
