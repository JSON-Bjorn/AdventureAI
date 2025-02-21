"""
Holds generic game functinality that does not
need to be in game loop or doesnt rely on API.

I also put stuff here that i dont know where we should put it.
Sorry future us.
"""

import random
from typing import Dict
from PIL import Image
import base64
from io import BytesIO
import re


class GameFunctionality:
    def pick_initial_story(self) -> Dict:
        """
        The user picks the starting story
        Currently just returns a hardcoded context
        """
        context = {
            "protagonist_name": "Linus Torvalds",
            "inventory": ["Materialized Linux kernel"],
            "current_scene": {
                "story": "You are sitting in a dark room, coding away, making a stupid game. You contemplate on wether or not you should use the knife in your inventory because this is starting to become a real shitstorm of a project.",
                "action": None,
                "dice_threshold": None,
                "dice_success": None,
            },
            "previous_scenes": [],
        }

    def convert_dice_threshold_to_int(self, llm_output: str) -> int:
        """
        Converts the dice threshold to an int
        """

        # Replaces any non digit characters with an empty string
        dice_threshold = re.sub(r"[^0-9]", "", str(llm_output))

        # Lets give them a free pass if the LLM fucks up and doesnt give a number.
        if dice_threshold == "":
            print("Giving free pass")
            dice_threshold = 0

        # Typecast threshold into an int
        dice_threshold = int(dice_threshold)

        # Make sure the threshold is not greater than 20
        if dice_threshold > 20:
            dice_threshold = 20

        return dice_threshold

    def player_rolls_dice(self, dice_threshold: int):
        """Prompts user to interact with dice and rolls the dice"""
        # Needs replacing obviously
        print(f"DICE THRESHOLD: {dice_threshold}")
        input("Press Enter to roll the dice...")

        # Roll dice
        roll = random.randint(1, 20)
        dice_success = roll >= dice_threshold

        if dice_success:
            print("DICE SUCCESS")
        else:
            print("DICE FAILURE")

        return dice_success

    async def render_scene(self, scene: Dict):
        """Renders the current scene"""
        # Show text in terminal
        print("=" * 50)
        print("THE GENERATED STORY:")
        print(scene["story"])
        print("=" * 50)

        # Show image in new window
        image_data = BytesIO(base64.b64decode(scene["image"]))
        image = Image.open(image_data)
        image.show()

    async def take_user_input(self, context: Dict):
        """Takes user input and stores to context"""
        context["current_scene"]["action"] = input("Your next action: ")
        return context

    def gather_new_user_information(self) -> Dict:
        """
        Is called when a user wants to start a new game.
        We should get protagonist name, one item in inventory and their initial story.
        """
        # Take user input and return formatted like the context dict
        # protagonist_name = input("Enter your protagonist name: ")
        # inventory = input("Enter an item in your inventory: ")
        # location = input("Where are you? ")
        protagonist_name = "Felix"
        inventory = "knife"
        location = "Busy London street"

        context = {
            "protagonist_name": protagonist_name,
            "inventory": [inventory],
            "current_scene": {
                "story": f"The protagonist {protagonist_name} is in {location}.",
                "action": None,
                "dice_threshold": None,
                "dice_success": None,
            },
            "previous_scenes": [],
            "mood": None,
        }

        return context
