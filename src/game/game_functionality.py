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


def roll_dice(threshhold: int):
    """
    Rolls a dice and returns a boolean

    Args:
        dice_threshhold: The threshold for the dice roll.

    Returns:
        True if the roll is more than or equal to the threshold,
        False if the roll is less than the threshold.
    """
    # Make sure threshhold is a valid non-negative number
    if not re.match(r"^[0-9]+$", str(threshhold)):
        raise ValueError("Threshold must be a non-negative number")

    # Typecast threshhold into an int
    threshhold = int(threshhold)

    if threshhold > 20:
        threshhold = 20

    roll = random.randint(1, 20)
    return roll >= threshhold


async def render_scene(scene: Dict):
    """Renders the current scene"""
    # Show text in terminal
    print("=" * 50)
    print(scene["story"])
    print("=" * 50)

    # Show image in new window
    image_data = BytesIO(base64.b64decode(scene["image"]))
    image = Image.open(image_data)
    image.show()


async def take_user_input():
    """Takes user input and stores to context"""
    return input("Your next action: ")


def gather_new_user_information() -> Dict:
    """
    Is called when a user wants to start a new game.
    We should get protagonist name, one item in inventory and their initial story.
    """
    # Take user input and return formatted like the context dict
    protagonist_name = input("Enter your protagonist name: ")
    inventory = input("Enter an item in your inventory: ")
    location = input("Where are you? ")

    context = {
        "protagonist_name": protagonist_name,
        "inventory": [inventory],
        "current_scene": {
            "story": f"The protagonist {protagonist_name} is in {location}.",
            "action": None,
            "dice_threshhold": None,
            "dice_success": None,
        },
        "previous_scenes": [],
        "mood": None,
    }

    return context


def format_prompt(contents: list[str]) -> str:
    """
    Formats a list of strings into a single string.
    """

    pass
