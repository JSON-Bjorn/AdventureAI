from typing import Dict
from src.api.generative_apis import (
    TextGeneration,
    ImageGeneration,
    SoundGeneration,
)
import random
import re
from io import BytesIO
from PIL import Image
import base64


class GameContextManager:
    def __init__(self):
        # APIs
        self.text = TextGeneration()
        self.image = ImageGeneration()
        self.sound = SoundGeneration()

        # Variables
        self.previous_stories = []

    def pick_initial_story(self) -> Dict:
        """Creates the initial context with starting story"""
        return {
            "protagonist_name": "Felix",
            "inventory": [],
            "current_scene": {
                "story": None,
                "action": None,
                "dice_threshold": None,
                "dice_success": None,
                "image": None,
            },
            "previous_scenes": [
                {
                    "story": "You are sitting in a dark room, coding away, making a stupid game. You contemplate on wether or not you should smash your keyboard because this is starting to become a real shitstorm of a project.",
                    "action": None,
                }
            ],
        }

    async def generate_image(self, context: Dict) -> Dict:
        """Generates image for the current story"""
        # Get the most recent story from previous_scenes
        current_story = context["previous_scenes"][-1]["story"]

        # Create a temporary context with both current scene and previous scenes
        temp_context = {
            "current_scene": {
                "story": current_story,
                "action": context["current_scene"]["action"],
            },
            "previous_scenes": context[
                "previous_scenes"
            ],  # Include previous_scenes
        }

        img_prompt = await self.text.generate_img_prompt(temp_context)
        base_64_image = await self.image.stable_diffusion_call(img_prompt)
        context["current_scene"]["image"] = base_64_image
        return context

    async def render_scene(self, context: Dict):
        """Renders the current scene's story and image"""
        # Get the most recent story from previous_scenes
        current_story = context["previous_scenes"][-1]["story"]

        # Show text in terminal
        print("=" * 50)
        print("THE STORY:")
        print(current_story)
        print("=" * 50)

        # Show image in new window if it exists
        if context["current_scene"]["image"]:
            image_data = BytesIO(
                base64.b64decode(context["current_scene"]["image"])
            )
            image = Image.open(image_data)
            image.show()

    async def take_user_input(self, context: Dict) -> Dict:
        """Takes user input as action in response to the current story"""
        context["current_scene"]["action"] = input("What do you do? ")
        return context

    async def handle_dice_roll(self, context: Dict) -> Dict:
        """Determines if action needs dice roll and handles the roll"""
        # Get dice threshold from the story and action
        story = context["current_scene"]["story"]
        action = context["current_scene"]["action"]
        llm_output = await self.text.determine_dice_threshold(story, action)

        # Convert to integer threshold
        threshold = await self.convert_dice_threshold_to_int(llm_output)

        # Roll dice
        dice_success = random.randint(1, 20) >= threshold

        # Add results to context
        context["current_scene"]["dice_threshold"] = threshold
        context["current_scene"]["dice_success"] = dice_success

        # Show results to user
        print(f"Required roll: {threshold}")
        print("Success!" if dice_success else "Failure!")

        return context

    async def move_scenes(self, context: Dict) -> Dict:
        """Moves completed current scene to previous_scenes"""
        # Create subset of current scene
        current_scene = {
            "story": context["current_scene"]["story"],
            "action": context["current_scene"]["action"],
        }

        # Append current scene to end of previous_scenes (newer events at bottom)
        context["previous_scenes"].append(current_scene)

        # Clear current scene
        context["current_scene"] = {
            "story": None,
            "action": None,
            "dice_threshold": None,
            "dice_success": None,
            "image": None,
        }

        return context

    async def generate_new_story(self, context: Dict) -> Dict:
        """Generates new story based on previous action"""
        new_story = await self.text.generate_story(context)
        context["current_scene"]["story"] = new_story
        return context

    async def convert_dice_threshold_to_int(self, llm_output: str) -> int:
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
