"""
Holds generic game functinality that does not
need to be in game loop or doesnt rely on API.
"""

import random
from typing import Dict


def roll_dice(threshhold: int):
    """
    Rolls a dice and returns a boolean

    Args:
        dice_threshhold: The threshold for the dice roll.

    Returns:
        True if the roll is more than or equal to the threshold,
        False if the roll is less than the threshold.
    """
    # If Mistral is hallucinating.
    if threshhold is None or threshhold < 0:
        return True
    elif threshhold > 20:
        threshhold = 20

    roll = random.randint(1, 20)
    return roll >= threshhold


async def render_scene(self, scene: Dict):
    """Renders the current scene"""
    pass


async def take_user_input(self):
    """Takes user input and stores to context"""
    return input("But we get the input from the frontend")
