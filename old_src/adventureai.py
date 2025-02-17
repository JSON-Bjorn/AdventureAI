"""
AdventureAI - An AI-Powered Choose Your Own Adventure Game

Main Game Architecture and Flow Controller

Core Components:
    Text Generation: OpenAI GPT for story generation
    Image Generation: Stable Diffusion for scene visualization
    Sound Generation: Background music and effects based on mood
    State Management: Maintains game state and story context

Game Flow:
    1. Story Generation: Creates narrative based on context
    2. Image Generation: Visualizes the current scene
    3. Action Resolution: Processes player choices
    4. State Updates: Maintains game progression

Usage:
    This module is used by the FastAPI server to handle game logic
"""

import os
import asyncio
import uuid
from typing import Optional, List, Dict
from io import BytesIO

from agents import (
    TextAgent,
    SoundAgent,
    TriageAgent,
    MoodAnalyzer,
)
from utils import ResourceManager
from utils.dice_roller import DiceRoller


class AdventureGame:
    def __init__(self):
        self.dice_roller = DiceRoller()
        self.author = TextAgent()
        self.narrator = SoundAgent()
        self.mood_analyzer = MoodAnalyzer()
        self.dungeon_master = None
        self.current_story = ""
        self.current_image_url = ""
        self.current_audio_url = ""
        self.current_mood = ""
        self.player_choice = None
        self.success = True
        self.previous_stories = []

    async def initialize_resources(self):
        """Initialize models and GPU but don't start the game"""
        # Get the pre-initialized illustrator
        illustrator = ResourceManager.get_illustrator()
        if not illustrator:
            raise RuntimeError(
                "IllustratorAgent not initialized. Server startup failed."
            )

        self.dungeon_master = await TriageAgent.create(
            self.author, self.narrator, illustrator, self.mood_analyzer
        )

    async def start_game(self):
        """Start the actual game by generating the first scene"""
        await self.generate_next_scene()

    async def generate_next_scene(self) -> Dict:
        """Generate the next scene including story, image, and audio"""
        # Generate next story segment
        await self.dungeon_master.next_story()

        # Get the story text
        self.current_story = self.dungeon_master.get_text()

        # Get and save the image
        image_data = self.dungeon_master.get_image()
        if image_data:
            # Convert Pillow Image to bytes
            img_byte_arr = BytesIO()
            image_data.save(img_byte_arr, format="PNG")
            img_byte_arr = img_byte_arr.getvalue()

            image_filename = f"{uuid.uuid4()}.png"
            image_path = os.path.join("static", "images", image_filename)
            with open(image_path, "wb") as f:
                f.write(img_byte_arr)
            self.current_image_url = f"/static/images/{image_filename}"

        # Get and save the audio
        voiceover = self.dungeon_master.get_voiceover()
        if voiceover:
            audio_filename = f"{uuid.uuid4()}.mp3"
            audio_path = os.path.join("static", "audio", audio_filename)
            voiceover.save_audio(audio_path)
            self.current_audio_url = f"/static/audio/{audio_filename}"

        # Get the mood
        self.current_mood = self.dungeon_master.get_mood()

        # Add current story to previous stories
        self.previous_stories.append(self.current_story)
        if len(self.previous_stories) > 5:  # Keep only last 5 stories
            self.previous_stories.pop(0)

        return self.get_current_state()

    def get_current_state(self) -> Dict:
        """Get the current game state"""
        return {
            "story": self.current_story,
            "image_url": self.current_image_url,
            "audio_url": self.current_audio_url,
            "mood": self.current_mood,
            "needs_dice_roll": False,
            "required_roll": None,
        }

    def assess_action_difficulty(self, action: str) -> Optional[int]:
        """Assess if an action requires a dice roll and return the required roll if needed"""
        return self.dice_roller.assess_situation(self.current_story, action)

    def process_dice_roll(self, required_roll: int) -> bool:
        """Process a dice roll and return whether it was successful"""
        success, _ = self.dice_roller.roll_dice(required_roll)
        self.success = success
        return success

    async def process_action(self, action: str) -> Dict:
        """Process a player action and return the new game state"""
        self.player_choice = action
        required_roll = self.assess_action_difficulty(action)

        if required_roll:
            return {
                "story": f"To do that, you need to roll {required_roll} or higher.",
                "image_url": self.current_image_url,
                "audio_url": None,
                "mood": self.current_mood,
                "needs_dice_roll": True,
                "required_roll": required_roll,
            }

        self.success = True
        return await self.generate_next_scene()

    async def cleanup(self):
        """Cleanup game state but not global resources"""
        self.current_story = ""
        self.current_image_url = ""
        self.current_audio_url = ""
        self.current_mood = ""
        self.player_choice = None
        self.success = True
        self.previous_stories = []
