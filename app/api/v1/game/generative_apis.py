# External imports
from typing import Dict
from requests import post, get
from openai import OpenAI
from fastapi import HTTPException

# Internal imports
from app.api.v1.game.instructions import instructions
from app.settings import settings
from app.api.logger.loggable import Loggable

"""
This file holds all the api calls made to our generative API's.

We have three classes corresponding to the three API's:
- TextGeneration, Uses OpenAI for text generation

- ImageGeneration, Uses a locally run Stable Diffusion API.

- SoundGeneration, ??
"""


class TextGeneration(Loggable):
    """Everything LLM-related"""

    def __init__(self) -> None:
        super().__init__()  # self.logger
        # Load the instructions
        self.instructions = instructions
        self.logger.info("TextGeneration initialized")

        # Set the endpoint
        self.endpoint = settings.MISTRAL_PORT

        # If OpenAI API is preferred
        self.openai = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def api_call(self, prompt: str, max_tokens: int = 1000):
        """Using OpenAI because computer slow"""
        self.logger.info(
            f"Making OpenAI API call with max_tokens={max_tokens}"
        )
        self.logger.debug(f"Prompt length: {len(prompt)}")
        try:
            response = self.openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=max_tokens,
            )
            result = response.choices[0].message.content
            self.logger.info(
                f"OpenAI API call successful, received {len(result)} characters"
            )
            return result
        except Exception as e:
            self.logger.error(f"Error in OpenAI API call: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error in OpenAI API call: {str(e)}",
            )

    async def _mistral_call_old(self, prompt: str, max_tokens: int = 100):
        """THIS IS MISTRAL"""
        self.logger.info(
            f"Making Mistral API call with max_tokens={max_tokens}"
        )
        self.logger.debug(f"Prompt length: {len(prompt)}")
        try:
            response = post(
                f"{self.endpoint}generate",
                json={"prompt": prompt, "max_tokens": max_tokens},
            )
            if response.status_code == 200:
                result = response.json()["text"]
                self.logger.info(
                    f"Mistral API call successful, received {len(result)} characters"
                )
                return result
            else:
                self.logger.error(
                    f"Mistral API error: status code {response.status_code}"
                )
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error: Received status code {response.status_code}",
                )
        except Exception as e:
            self.logger.error(f"Error in Mistral API call: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating text: {e}",
            )


class ImageGeneration(Loggable):
    """Everything image-related"""

    def __init__(self) -> None:
        super().__init__()  # Initialize the logger
        # The endpoint for the image generation API
        self.endpoint = settings.STABLE_DIFFUSION_PORT
        self.logger.info(
            "ImageGeneration initialized with endpoint: {self.endpoint}"
        )

    async def api_call(self, prompt: str):
        """
        Requests the /generate endpoint of the Stable Diffusion API

        Args:
        prompt(str): The prompt for image generation

        Returns:
        byte64_image(str): The image in base64 format
            This is decoded in the frontend!!
        """
        self.logger.info("Making Stable Diffusion API call")
        self.logger.debug(f"Image prompt length: {len(prompt)}")
        try:
            response = get(f"{self.endpoint}?prompt={prompt}")
            if response.status_code == 200:
                byte64_image = response.json()["image"]
                image_size = len(byte64_image) / 1000
                self.logger.info(
                    f"Image generation successful, received {image_size} KB"
                )
                return byte64_image
            else:
                self.logger.error(
                    f"Stable Diffusion API error: status code {response.status_code}"
                )
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error: Stable Diffusion API gave status code: {response.status_code}",
                )
        except Exception as e:
            self.logger.error(f"Error in Stable Diffusion API call: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating image: {e}",
            )


class SoundGeneration(Loggable):
    """Everything sound-related"""

    def __init__(self) -> None:
        super().__init__()  # self.logger
        self.logger.info("SoundGeneration initialized")

    async def generate_speech(self):
        """Generates speech based on text"""
        pass

    async def fetch_music(self, mood: str):
        """Fetches music from the database"""
        pass
