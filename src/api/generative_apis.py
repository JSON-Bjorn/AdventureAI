"""This file could hold all of the agents"""

# External imports
from typing import Dict
import requests
import os

# Internal imports
import json
# from src.game.game_functionality import


class TextGeneration:
    """Everything LLM-related"""

    def __init__(self) -> None:
        # Load the instructions
        with open("src/api/instructions.json", "r") as f:
            self.instructions = json.load(f)

        # Set the endpoint
        self.endpoint = "http://localhost:8000/"

        # List for previous stories
        self.previous_stories = []

    async def _mistral_call(self, prompt: Dict | str, max_tokens: int = 100):
        """Makes a call to the mistral model"""
        try:
            response = requests.post(
                f"{self.endpoint}generate",
                json={"prompt": prompt, "max_tokens": max_tokens},
            )
            if response.status_code == 200:
                return response.json()["text"]
            else:
                print(f"Error: Received status code {response.status_code}")
                return None
        except Exception as e:
            print(f"Error generating text: {e}")
            return None

    async def generate_story(self, context: Dict):
        """Generated a new story based on the context"""
        # Format the prompt for story generation
        formatted_prompt = f"""
            Instructions: {self.instructions['generate_story']}

            Protagonist: {context['protagonist_name']}
            Inventory: {', '.join(context['inventory'])}

            Previous scenes:
            """
        # Add scenes in sequence, current scene will be the last one
        for scene in context["previous_scenes"]:
            formatted_prompt += f"- Story: {scene['story']}\n"
            formatted_prompt += f"  Protagonist action: {scene['action']}\n\n"
            formatted_prompt += f"  Acton success: {context['current_scene']['dice_success']}\n\n"

        # Add current scene
        formatted_prompt += f"- Story: {context['current_scene']['story']}\n"
        formatted_prompt += (
            f"Protagonist action: {context['current_scene']['action']}\n\n"
        )
        formatted_prompt += (
            f"Action success: {context['current_scene']['dice_success']}\n\n"
        )

        # Print statement for clarity during development
        print("\nSending this prompt to API:")
        print("=" * 50)
        print(formatted_prompt)
        print("=" * 50 + "\n")

        # Make the call with formatted prompt
        next_story = await self._mistral_call(formatted_prompt)
        return next_story

    async def generate_prompt(self, context: Dict):
        """Generates a prompt for the image agent"""
        # Boilerplate code
        current_scene = context["current_scene"]["story"]
        prompt = await self._mistral_call(current_scene)
        return prompt

    async def determine_dice_roll(self, context: str):
        """
        Uses mistral API to determine if we need a dice roll
        and what the threshhold should be.

        Args:
            context: The context to determine the dice roll for

        Returns:
            A dictionary with the following keys:
            - "needed": Whether a dice roll is needed
            - "required_roll": The required roll
        """
        # Dissect context and get instructions
        instructions = self.instructions["determine_dice_roll"]
        story = context["current_scene"]["story"]
        action = context["current_scene"]["action"]

        prompt = f"""
            Instructions: {instructions}

            Story: {story}
            Action: {action}
        """

        # API call
        print("Making call to determine dice roll")
        threshhold = await self._mistral_call(prompt, 5)
        return threshhold

    async def analyze_mood(self, context: Dict):
        """Analyzes the mood of the story"""
        # Boilerplate code
        mood = await self._mistral_call(context)
        return mood

    async def compress_context(self, context: Dict):
        """
        Compresses the current story and action
        Adds the compressed story and action to the previous stories
        Removes the oldest story if there are more than 10
        Clears the current story

        Args:
        context: The context to compress

        Returns:
        The updated context
        """
        # Dissect context and get instructions
        instructions = self.instructions["compress_context"]
        story = context["story"]["current"]["story"]
        action = context["story"]["current"]["action"]
        dice_threshhold = context["story"]["current"]["dice_threshhold"]
        dice_success = context["story"]["current"]["dice_success"]

        # API call
        compressed_story = await self._mistral_call(instructions, story)
        compressed_action = await self._mistral_call(instructions, action)

        # Update the context
        context["story"]["previous"].append(
            {
                "story": compressed_story,
                "action": compressed_action,
                "dice_threshhold": dice_threshhold,
                "dice_success": dice_success,
            }
        )

        # Remove the oldest story if there are more than 10
        if len(context["story"]["previous"]) > 10:
            oldest_story = context["story"]["previous"].pop(0)
            self.previous_stories.append(oldest_story)

        # Clear the current story
        for key, value in context["story"]["current"].items():
            context["story"]["current"][key] = None

        # Return the new full context
        return context

    async def _compress_story(self, story: str):
        """Makes an API call to the mistral model to compress the story"""
        return "I do a backflip"


class ImageGeneration:
    """Everything image-related"""

    def __init__(self) -> None:
        # The endpoint for the image generation API
        self.endpoint = "http://localhost:8001/generate"

    async def stable_diffusion_call(self, prompt: str):
        """
        Pings the /generate endpoint of the Stable Diffusion API

        Args:
        prompt: The prompt for image generation
            This string has gone through prompt optimization already

        Returns:
        byte64_image: The image in base64 format
            This is decoded in the frontend!!
        """
        try:
            response = requests.get(f"{self.endpoint}?prompt={prompt}")
            if response.status_code == 200:
                byte64_image = response.json()["image"]
                return byte64_image
            else:
                print(f"Error generating image: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error generating image: {e}")
            return None


class SoundGeneration:
    """Everything sound-related"""

    async def generate_speech(self):
        """Generates speech based on text"""
        pass

    async def fetch_music(self, mood: str):
        """Fetches music from the database"""
        pass
