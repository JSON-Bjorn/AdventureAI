from typing import Dict
from src.api.generative_apis import (
    TextGeneration,
    ImageGeneration,
    SoundGeneration,
)
from src.game.game_functionality import GameFunctionality


class ContextManager:
    def __init__(self):
        # Game functionality
        self.game_functionality = GameFunctionality()

        # APIs
        self.text = TextGeneration()
        self.image = ImageGeneration()
        self.sound = SoundGeneration()

        # Variables
        self.previous_stories = []

    async def handle_dice_roll(self, context: Dict):
        """
        Makes api call to determine dice roll.
        Rolls dice
        Returns the full context with threshold and success
        """
        # Ask Mistral to determine the dice roll threshold
        llm_output: str = await self.text.determine_dice_roll(context)

        # Extract the integer from llm output
        dice_threshold = (
            self.game_functionality.convert_dice_threshold_to_int(llm_output)
        )

        # Roll the dice
        dice_success = self.game_functionality.player_rolls_dice(
            dice_threshold
        )

        # Add DICE_SUCCESS to context
        context["current_scene"]["dice_threshold"] = dice_threshold
        context["current_scene"]["dice_success"] = dice_success

        return context

    async def move_scenes(self, context: Dict, story: str):
        """
        Moves the context to the previous scene
        Might be deprecated lmao
        """
        # Define CURRENT scene as variable
        current_scene = {
            "story": story,
            "action": context["current_scene"]["action"],
            "dice_threshold": context["current_scene"]["dice_threshold"],
            "dice_success": context["current_scene"]["dice_success"],
        }

        # Append the CURRENT scene to PREVIOUS scenes in context
        context["previous_scenes"].append(current_scene)
        # ALso append it to the scene history
        self.previous_stories.append(current_scene)

        # Remove the oldest story if there are more than 10
        if len(context["previous_scenes"]) > 10:
            oldest_story = context["story"]["previous"].pop(0)
            self.previous_stories.append(oldest_story)

        # Clear the CURRENT story
        for key, value in context["current_scene"].items():
            context["current_scene"][key] = None

        return context

    async def append_to_previous_scenes(self, context):
        pass

    async def remove_oldest_story(self, context):
        pass

    async def build_current_scene(self, context: Dict):
        """Builds the current scene"""
        current_story = await self.text.generate_story(context)
        img_prompt = await self.text.generate_img_prompt(context)
        image = await self.image.stable_diffusion_call(img_prompt)
        # mood = await self.text.analyze_mood(current_story)
        # music = await self.sound.fetch_music(mood)
        # speech = await self.sound.generate_speech(current_story)

        return {
            "story": current_story,
            "image": image,
            "mood": None,
            "music": None,
            "speech": None,
        }
