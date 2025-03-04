"""This file could hold all of the agents"""

# External imports
from typing import Dict, List
import requests
import os
from openai import OpenAI

# Internal imports
import json

# from src.game.game_functionality import
from src.api.instructions import instructions

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"


class TextGeneration:
    """Everything LLM-related"""

    def __init__(self) -> None:
        # Load the instructions
        self.instructions = instructions

        # Set the endpoint
        self.endpoint = "http://localhost:8000/"

        # List for previous stories
        self.previous_stories = []

        # OPENAI because mistral is slow as fuck
        self.openai = OpenAI()

    async def _mistral_call(self, prompt: str, max_tokens: int = 1000):
        """Makes a call to the OpenAI API"""
        try:
            response = self.openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in OpenAI API call: {str(e)}")

    async def __mistral_call(self, prompt: str, max_tokens: int = 100):
        """Makes a call to the mistral model"""
        """CURRENTLY NOT ACTIVE (see double underscore and method above)"""
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
        """Builds the prompt and calls the mistral model for a new story"""
        print("generate_story - method called")

        # Define variables
        instructions: str = self.instructions["generate_story"]
        protagonist_name: str = context["protagonist_name"]
        inventory: str = ", ".join(context["inventory"])
        previous_scenes: List[Dict] = context["previous_scenes"]
        current_action = context["current_scene"]["action"]
        action_success = context["current_scene"]["dice_success"]

        # Format the prompt
        formatted_prompt = f"""
    Instructions: {instructions}
    Protagonist: {protagonist_name}
    Inventory: {inventory}

    The story so far:
    """
        # Add all previous stories in chronological order
        for i, scene in enumerate(previous_scenes, 1):
            formatted_prompt += f"Story {i}: {scene['story']}\n\n"

        # Add the current action and its success (this is what we're generating a story for)
        formatted_prompt += f"Protagonist's action based on Story {len(previous_scenes)}: {current_action}\n"
        formatted_prompt += f"Action successful: {action_success}\n\n"
        formatted_prompt += f"Story {len(previous_scenes) + 1}: Please write this story based on the previous ones.\n\n"

        # PRINT DEBUGGING
        print("=" * 50)
        print(
            f"{RED}Asked Mistral to generate story:{RESET}\n{formatted_prompt}\n"
        )
        print("=" * 50)

        # Make the call with formatted prompt
        next_story = await self._mistral_call(formatted_prompt)

        # PRINT DEBUGGING
        print("=" * 50)
        print(f"{GREEN}Generated story:{RESET}\n{next_story}\n")
        print("=" * 50)

        return next_story

    async def generate_img_prompt(self, context: Dict):
        """Generates a prompt for the image agent"""
        print("generate_prompt - method called")

        # Get the most recent story from previous_scenes
        current_story = context["previous_scenes"][-1]["story"]

        instructions = self.instructions["generate_prompt"]
        formatted_prompt = f"""
            Instructions: {instructions}

            Story: {current_story}
            Protagonist's action: {context["current_scene"]["action"]}
        """

        # Debugging prints
        print("=" * 50)
        print(
            f"{RED}Asked Mistral to generate img prompt:{RESET}\n{formatted_prompt}\n"
        )
        print("=" * 50)

        # Make the call with formatted prompt
        img_prompt = await self._mistral_call(formatted_prompt)

        # Debugging prints
        print("=" * 50)
        print(f"{GREEN}Generated img prompt:{RESET}\n{img_prompt}\n")
        print("=" * 50)

        return img_prompt

    async def determine_dice_threshold(self, story, action):
        """
        Uses mistral API to determine if we need a dice roll
        and what the threshold should be.

        Args:
            context: The context to determine the dice roll for

        Returns:
            A dictionary with the following keys:
            - "needed": Whether a dice roll is needed
            - "required_roll": The required roll
        """
        # Dissect context and get instructions
        instructions = self.instructions["determine_dice_roll"]

        prompt = f"""
            Instructions: {instructions}

            Story: {story}
            Action: {action}
        """

        # PRINT DEBUGGING
        print("=" * 50)
        print(
            f"{RED}Asked Mistral to determine dice roll:{RESET}\n{prompt}\n"
        )
        print("=" * 50)

        # API call
        threshold = await self._mistral_call(prompt, 3)

        # PRINT DEBUGGING
        print("=" * 50)
        print(f"{GREEN}Generated dice roll threshold:{RESET}\n{threshold}\n")
        print("=" * 50)

        return threshold

    async def analyze_mood(self, context: Dict):
        """Analyzes the mood of the story"""
        # Boilerplate code
        prompt = "Format prompt here with instructions and context"
        mood = await self._mistral_call(prompt)
        return mood

    async def compress_story(self, story: str):
        """
        Compresses a story

        Args:
        story: The story to compress

        Returns:
        The updated context
        """
        # Dissect context and get instructions
        instructions = self.instructions["compress_context"]

        prompt = f"""
            Instructions: {instructions}

            Story: {story}
        """

        # PRINT DEBUGGING
        print("=" * 50)
        print(f"{RED}Asked Mistral to compress story:{RESET}\n{prompt}\n")
        print("=" * 50)

        # API call
        compressed_story = await self._mistral_call(prompt)

        # PRINT DEBUGGING
        print("=" * 50)
        print(f"{GREEN}Compressed story:{RESET}\n{compressed_story}\n")
        print("=" * 50)

        return compressed_story


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
        print("=" * 50)
        print(f"{RED}Making call to stable diffusion:{RESET}\n{prompt}\n")
        print("=" * 50)
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
