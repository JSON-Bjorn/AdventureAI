from typing import Dict, List, Tuple

# Internal imports
from src.api.instructions import instructions


class PromptBuilder:
    """Class that handles all prompt building before a LLM-call"""

    def __init__(self):
        self.instructions = instructions

    async def get_dice_prompt(self, recent_scene: Dict):
        """Builds the prompt for the dice roll"""
        # Dissect context and get instructions
        instructions = self.instructions["determine_dice_roll"]
        story = recent_scene["story"]
        action = recent_scene["action"]

        prompt = (
            f"Instructions: {instructions}\n\n"
            f"Story: {story}\n"
            f"Action: {action}\n"
        )
        return prompt

    def get_story_prompt(
        self, game_session: Dict, dice: Tuple[int, int, bool]
    ) -> str:
        """Builds the prompt for new stories"""
        print("generate_story - method called")

        # Define variables
        instructions: str = self.instructions["generate_story"]
        name: str = game_session["protagonist_name"]
        inv: str = ", ".join(game_session["inventory"])
        prev_scene: List[Dict] = game_session["scenes"]
        action: str = game_session["scenes"][-1]["action"]
        success: bool = dice[2]

        # Format the prompt
        prompt = (
            f"Instructions: {instructions}\n\n"
            f"Protagonist name: {name}\n"
            f"Protagonist's inventory: {inv}\n\n"
            "The story so far:\n"
        )
        # Add all previous stories in chronological order
        for i, scene in enumerate(prev_scene, 1):
            prompt += f"Story {i}: {scene['story']}\n\n"

        # Add the current action and its success (this is what we're generating a story for)
        prompt += f"Protagonist's action based on the last story: {action}\n"
        prompt += f"Action successful: {success}\n\n"
        prompt += f"Story {len(prev_scene) + 1}: Please write this story based on what just happened.\n\n"

        return prompt

    async def get_compress_prompt(self, story: str):
        """Builds the prompt for compressing a story"""
        instructions = self.instructions["compress_story"]
        prompt = f"Instructions: {instructions}\n" f"Story: {story}"
        return prompt

    async def get_img_prompt(self, story: str):
        """Build the prompt for image generation"""
        # Get instructions and prompt
        instructions = self.instructions["generate_prompt"]
        prompt = f"""
            Instructions: {instructions}

            Story: {story}
        """

        # Spice up the prompt
        spicy_prompt = (
            "highly detailed, masterpiece, 8k resolution, photorealistic, "
            "sharp focus, volumetric lighting, professional color grading, "
            "cinematic lighting, perfect composition, " + prompt
        )

        return spicy_prompt

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
            return "calm/adventerous"
