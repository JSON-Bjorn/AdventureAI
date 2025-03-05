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

    async def api_call(self, prompt: str, max_tokens: int = 1000):
        """Using OpenAI because computer slow"""
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

    async def _mistral_call_old(self, prompt: str, max_tokens: int = 100):
        """THIS IS MISTRAL"""
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

    async def analyze_mood(self, context: Dict):
        """Analyzes the mood of the story"""
        # Boilerplate code
        prompt = "Format prompt here with instructions and context"
        mood = await self._mistral_call(prompt)
        return mood


class ImageGeneration:
    """Everything image-related"""

    def __init__(self) -> None:
        # The endpoint for the image generation API
        self.endpoint = "http://localhost:8001/generate"

    async def api_call(self, prompt: str):
        """
        Requests the /generate endpoint of the Stable Diffusion API

        Args:
        prompt(str): The prompt for image generation

        Returns:
        byte64_image(str): The image in base64 format
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
