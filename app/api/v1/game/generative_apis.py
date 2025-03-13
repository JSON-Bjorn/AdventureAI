# External imports
from typing import Dict
from requests import post, get
from os import getenv
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import HTTPException

# Internal imports
from app.api.v1.game.instructions import instructions
from app.settings import settings

"""
This file holds all the api calls made to our generative API's.

We have three classes corresponding to the three API's:
- TextGeneration, Uses OpenAI for text generation

- ImageGeneration, Uses a locally run Stable Diffusion API.

- SoundGeneration, ??
"""


class TextGeneration:
    """Everything LLM-related"""

    def __init__(self) -> None:
        # Load the instructions
        self.instructions = instructions

        # Set the endpoint
        self.endpoint = settings.MISTRAL_PORT

        # List for previous stories
        self.previous_stories = []

        # If OpenAI API is preferred
        self.openai = OpenAI(api_key=settings.OPENAI_API_KEY)

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
            raise HTTPException(
                status_code=500,
                detail=f"Error in OpenAI API call: {str(e)}",
            )

    async def _mistral_call_old(self, prompt: str, max_tokens: int = 100):
        """THIS IS MISTRAL"""
        try:
            response = post(
                f"{self.endpoint}generate",
                json={"prompt": prompt, "max_tokens": max_tokens},
            )
            if response.status_code == 200:
                return response.json()["text"]
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error: Received status code {response.status_code}",
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating text: {e}",
            )

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
        self.endpoint = settings.STABLE_DIFFUSION_PORT

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
            response = get(f"{self.endpoint}?prompt={prompt}")
            if response.status_code == 200:
                byte64_image = response.json()["image"]
                return byte64_image
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error: Stable Diffusion API gave status code: {response.status_code}",
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating image: {e}",
            )


class SoundGeneration:
    """Everything sound-related"""

    async def generate_speech(self):
        """Generates speech based on text"""
        pass

    async def fetch_music(self, mood: str):
        """Fetches music from the database"""
        pass
