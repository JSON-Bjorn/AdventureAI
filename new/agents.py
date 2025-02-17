"""This file could hold all of the agents"""

from typing import Dict
import requests


class TriageAgent:
    """
    Orchestrated the actions of all the other agents
    Im actually unsure if we need this. Hear me out.
    We set out to use agents in this project. Thats why we are here essentially.
    But now that we have our own apis, we could just call them directly.

    We can set specific instructions for each "agent"
    here and just call them directly from the game loop.

    Idk what works best.
    The thing with agents is that they should be able to execute functions
    that are directly associated with other agents, right?

    We could do that when mood changes, for example.
    Or when a dice roll is needed.

    We can just put the _fetch_music and _generate_speech methods
    in SoundAgent and then let Triage call them.

    This seems unnecessarily complex to me. Maybe I dont get it.

    I feel like the game loop isnt very complex, as it shouldnt be.
    Calling the methods directly from there might be our best option. Lets talk abouddit
    """

    pass


class AuthorAgent:
    """Handles story generation"""

    async def generate_story(self, context: Dict):
        """Makes an API call to generate a new story"""
        pass

    async def new_story(self):
        """Makes an API call to generate a new story"""
        # Make sure to fill out the entire context dict, not just context["story"]["current"]
        # Return the entire context, we are expecting it in the game_session class
        pass


class CompressorAgent:
    """Handles context compression"""

    async def compress_context(self, context: Dict):
        """Takes the game session context and compresses it"""
        # Compress the story and add it to the previous stories
        compressed_story = self._compress_story(context["story"]["current"])
        context["story"]["previous"].append(compressed_story)

        # Make sure the context doesnt get too long
        if len(context["story"]["previous"]) > 10:
            context["story"]["previous"].pop(0)

        return context

    async def _compress_story(self, story: str):
        """Makes an API call to the mistral model to compress the story"""
        return "I do a backflip"


class MoodAnalyzer:
    """Handles mood analysis"""

    async def analyze_mood(self):
        """Analyzes the mood of the story"""
        pass


class DiceRoller:
    """Handles dice rolls"""

    async def determine_dice_roll(self, story: str):
        """Determines if a dice roll is needed and how high"""
        # Should return the entire "dice_roll" value from context:
        # {
        #     "needed": True,
        #     "required_roll": 17,
        # }
        pass


class PromptAgent:
    """Handles prompt optimization"""

    async def generate_prompt(self):
        """Generates a prompt for the image agent"""
        pass


class ImageAgent:
    """Handles image generation"""

    def __init__(self) -> None:
        self.endpoint = "http://localhost:8000/generate"

    async def generate_image(self, prompt: str):
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


class SoundAgent:
    """Handles everything sound-related"""

    async def generate_speech(self):
        """Generates speech based on text"""
        pass

    async def fetch_music(self, mood: str):
        """Fetches music from the database"""
        pass
