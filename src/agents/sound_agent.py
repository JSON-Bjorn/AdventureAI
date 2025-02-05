from openai import OpenAI
import io
import os
from dotenv import load_dotenv
import random
from pathlib import Path


class SoundAgent:
    def __init__(self):
        load_dotenv(override=True)
        self.client = OpenAI()
        self.current_audio = None
        self.music_root = Path("osrs music")
        self.current_intensity = None
        self.current_mood = None

    async def generate_speech(self, text: str) -> bool:
        """Generate speech from text using OpenAI's TTS"""
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="onyx",
                input=text,
            )
            self.current_audio = response.content
            return True
        except Exception as e:
            print(f"Error generating speech: {e}")
            return False

    def save_audio(self, filepath: str) -> bool:
        """Save the current audio to a file"""
        if self.current_audio:
            try:
                with open(filepath, "wb") as f:
                    f.write(self.current_audio)
                return True
            except Exception as e:
                print(f"Error saving audio: {e}")
        return False

    def get_background_music_path(
        self, intensity: int = None, mood: str = None
    ) -> str:
        """Get a random background music file path matching the scene intensity and mood"""
        try:
            # Update current settings if provided
            if intensity is not None:
                self.current_intensity = intensity
            if mood is not None:
                self.current_mood = mood

            # Construct path to appropriate music folder
            music_dir = (
                self.music_root
                / f"{self.current_intensity}. {self._get_intensity_name()}"
                / self.current_mood
            )

            music_files = list(music_dir.glob("*.ogg"))
            if not music_files:
                print(f"No music files found in {music_dir}")
                return None

            music_file = random.choice(music_files)
            return str(music_file)

        except Exception as e:
            print(f"Error getting background music path: {e}")
            return None

    def _get_intensity_name(self) -> str:
        """Convert intensity number to folder name"""
        return {1: "calm", 2: "medium", 3: "intense"}[self.current_intensity]
