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

    # async def handle_dice_roll(self, context: Dict):
    #     """
    #     Makes api call to determine dice roll.
    #     Rolls dice
    #     Returns the full context with threshold and success
    #     """
    #     # Ask Mistral to determine the dice roll threshold
    #     llm_output: str = await self.text.determine_dice_roll(context)

    #     # Extract the integer from llm output
    #     dice_threshold = self.convert_dice_threshold_to_int(llm_output)

    #     # Roll the dice
    #     dice_success = self.player_rolls_dice(dice_threshold)

    #     # Add DICE_SUCCESS to context
    #     context["current_scene"]["dice_threshold"] = dice_threshold
    #     context["current_scene"]["dice_success"] = dice_success

    #     return context

    # async def move_scenes(self, context: Dict, story: str):
    #     """
    #     Moves the context to the previous scene
    #     Might be deprecated lmao
    #     """
    #     # Define CURRENT scene as variable
    #     current_scene = {
    #         "story": story,
    #         "action": context["current_scene"]["action"],
    #         "dice_threshold": context["current_scene"]["dice_threshold"],
    #         "dice_success": context["current_scene"]["dice_success"],
    #     }

    #     # Append the CURRENT scene to PREVIOUS scenes in context
    #     context["previous_scenes"].append(current_scene)
    #     # ALso append it to the scene history
    #     self.previous_stories.append(current_scene)

    #     # Remove the oldest story if there are more than 10
    #     if len(context["previous_scenes"]) > 10:
    #         oldest_story = context["story"]["previous"].pop(0)
    #         self.previous_stories.append(oldest_story)

    #     # Clear the CURRENT story
    #     for key, value in context["current_scene"].items():
    #         context["current_scene"][key] = None

    #     return context

    # async def append_to_previous_scenes(self, context):
    #     pass

    # async def remove_oldest_story(self, context):
    #     pass

    # async def build_current_scene(self, context: Dict):
    #     """Builds the current scene"""
    #     current_story = await self.text.generate_story(context)
    #     img_prompt = await self.text.generate_img_prompt(context)
    #     image = await self.image.stable_diffusion_call(img_prompt)
    #     # mood = await self.text.analyze_mood(current_story)
    #     # music = await self.sound.fetch_music(mood)
    #     # speech = await self.sound.generate_speech(current_story)

    #     return {
    #         "story": current_story,
    #         "image": image,
    #         "mood": None,
    #         "music": None,
    #         "speech": None,
    #     }

    # def convert_dice_threshold_to_int(self, llm_output: str) -> int:
    #     """
    #     Converts the dice threshold to an int
    #     """

    #     # Replaces any non digit characters with an empty string
    #     dice_threshold = re.sub(r"[^0-9]", "", str(llm_output))

    #     # Lets give them a free pass if the LLM fucks up and doesnt give a number.
    #     if dice_threshold == "":
    #         print("Giving free pass")
    #         dice_threshold = 0

    #     # Typecast threshold into an int
    #     dice_threshold = int(dice_threshold)

    #     # Make sure the threshold is not greater than 20
    #     if dice_threshold > 20:
    #         dice_threshold = 20

    #     return dice_threshold

    # def player_rolls_dice(self, dice_threshold: int):
    #     """Prompts user to interact with dice and rolls the dice"""
    #     # Needs replacing obviously
    #     print(f"DICE THRESHOLD: {dice_threshold}")
    #     input("Press Enter to roll the dice...")

    #     # Roll dice
    #     roll = random.randint(1, 20)
    #     dice_success = roll >= dice_threshold

    #     if dice_success:
    #         print("DICE SUCCESS")
    #     else:
    #         print("DICE FAILURE")

    #     return dice_success

    # def gather_new_user_information(self) -> Dict:
    #     """
    #     Is called when a user wants to start a new game.
    #     We should get protagonist name, one item in inventory and their initial story.
    #     """
    #     # Take user input and return formatted like the context dict
    #     # protagonist_name = input("Enter your protagonist name: ")
    #     # inventory = input("Enter an item in your inventory: ")
    #     # location = input("Where are you? ")
    #     protagonist_name = "Felix"
    #     inventory = "knife"
    #     location = "Busy London street"

    #     context = {
    #         "protagonist_name": protagonist_name,
    #         "inventory": [inventory],
    #         "current_scene": {
    #             "story": f"The protagonist {protagonist_name} is in {location}.",
    #             "action": None,
    #             "dice_threshold": None,
    #             "dice_success": None,
    #         },
    #         "previous_scenes": [],
    #         "mood": None,
    #     }

    #     return context

    # REFACTOR STARTS HERE
    # REFACTOR STARTS HERE
    # REFACTOR STARTS HERE
    # REFACTOR STARTS HERE
    # REFACTOR STARTS HERE
    # REFACTOR STARTS HERE
    # REFACTOR STARTS HERE

    def pick_initial_story(self) -> Dict:
        """
        The user picks the starting story
        """
        return {
            "protagonist_name": "Felix",
            "inventory": [],
            "current_scene": {
                "story": "You are sitting in a dark room, coding away, making a stupid game. You contemplate on wether or not you should smash your keyboard because this is starting to become a real shitstorm of a project.",
                "action": None,
                "dice_threshold": None,
                "dice_success": None,
                "image": None,
                "mood": None,
                "music": None,
                "speech": None,
            },
            "previous_scenes": [],
        }

    async def generate_image(self, context: Dict) -> str:
        """
        Calls both mistral for img prompt and sd for image.
        Returns the image as a Base64 encoded string
        """
        img_prompt = await self.text.generate_img_prompt(context)
        base_64_image = await self.image.stable_diffusion_call(img_prompt)
        context["current_scene"]["image"] = base_64_image

        return context

    async def render_scene(self, context: Dict):
        """Renders the current scene"""
        # Show text in terminal
        print("=" * 50)
        print("THE GENERATED STORY:")
        print(context["current_scene"]["story"])
        print("=" * 50)

        # Show image in new window
        image_data = BytesIO(
            base64.b64decode(context["current_scene"]["image"])
        )
        image = Image.open(image_data)
        image.show()

    async def move_scenes(self, context: Dict) -> Dict:
        """
        Moves current scene to previous scenes
        Empties current scene
        Compresses most previous story
        Moves oldest story to instance variable if there are more than 10.
        """
        # Get current scene subset
        current_scene_subset = {
            "story": context["current_scene"]["story"],
            "action": context["current_scene"]["action"],
            "dice_success": context["current_scene"]["dice_success"],
        }

        # Move current to previous
        context["previous_scenes"].append(current_scene_subset)

        # Empty current scene
        for key, value in context["current_scene"].items():
            context["current_scene"][key] = None

        # Compress most previous story
        context = await self.compress_previous_story(context)

        # Move scenes that are older than 10 to instance variable
        if len(context["previous_scenes"]) > 10:
            self.previous_stories.append(context["previous_scenes"].pop(0))

        # Return updated context
        return context

    async def compress_previous_story(self, context: Dict) -> Dict:
        """Uses Mistral API to compress and alter the most previous story"""
        # Get the most previous story
        newest_story = context["previous_scenes"][-1]["story"]

        # Call mistral to compress story
        compressed_story = await self.text.compress_story(story=newest_story)

        # Reassemble the context
        context["previous_scenes"][-1]["story"] = compressed_story

        # Return updated context
        return context

    async def take_user_input(self, context: Dict):
        """Takes user input and stores to context"""
        context["current_scene"]["action"] = input("Your next action: ")
        return context

    async def handle_dice_roll(self, context: Dict):
        """Handles the process of rolling the dice"""
        # We should:
        # - Call mistral to determine threshold
        # - Call function to typecast into int
        # - Roll dice
        # - Add dice_threshold and dice_success to context
        # - Return the updated context

        # Prepare arguments and call Minstral for dice threshold
        story = context["previous_scenes"][-1]["story"]
        action = context["current_scene"]["action"]
        llm_output = await self.text.determine_dice_threshold(story, action)

        # Typecast threshold
        dice_threshold: int = await self.convert_dice_threshold_to_int(
            llm_output
        )

        # Roll dice
        dice_success: bool = random.randint(1, 20) >= dice_threshold

        # Add dice_threshold and dice_success to context
        context["current_scene"]["dice_threshold"] = dice_threshold
        context["current_scene"]["dice_success"] = dice_success

        return context

    async def convert_dice_threshold_to_int(self, llm_output: str) -> int:
        """
        Converts Mistrals output into an integer
        representing the dice threshold for a player action.
        """
        # Replaces any non digit characters with an empty string
        threshold: str = re.sub(r"[^0-9]", "", str(llm_output))

        # Lets give them a free pass if the LLM fucks up and doesnt give a number.
        if threshold == "":
            print("Giving free pass")
            threshold = 0

        # Typecast threshold into an int
        threshold: int = int(threshold)

        # Make sure the threshold is not greater than 20
        if threshold > 20:
            threshold = 20

        # Return the threshold
        return threshold

    async def generate_new_story(self, context: Dict):
        """Generates a new story"""
        story = await self.text.generate_story(context)
        context["current_scene"]["story"] = story
        return context
