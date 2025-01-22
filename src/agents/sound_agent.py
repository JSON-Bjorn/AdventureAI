from openai import OpenAI
import pygame
import io
import threading
from dotenv import load_dotenv
import os


class SoundAgent:
    def __init__(self):
        load_dotenv(override=True)
        self.client = OpenAI()
        self.current_audio = None
        self.is_playing = False

        # Initialize pygame mixer for audio playback
        pygame.mixer.init()

    async def generate_speech(self, text: str) -> bool:
        """Generate speech from text using OpenAI's TTS"""
        try:
            # Generate speech using OpenAI's TTS
            response = self.client.audio.speech.create(
                model="tts-1",  # or "tts-1-hd" for higher quality
                voice="onyx",  # Options: alloy, echo, fable, onyx, nova, shimmer
                input=text,
            )

            # Convert response to audio data
            audio_data = io.BytesIO(response.content)
            self.current_audio = audio_data
            return True

        except Exception as e:
            print(f"Error generating speech: {e}")
            return False

    def play_audio(self):
        """Play the current audio file"""
        if self.current_audio and not self.is_playing:
            try:
                # Create a new thread for audio playback
                self.is_playing = True
                thread = threading.Thread(target=self._play_audio_thread)
                thread.start()
            except Exception as e:
                print(f"Error playing audio: {e}")
                self.is_playing = False

    def _play_audio_thread(self):
        """Internal method to play audio in a separate thread"""
        try:
            # Load and play the audio
            pygame.mixer.music.load(self.current_audio)
            pygame.mixer.music.play()

            # Wait for the audio to finish
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)

        except Exception as e:
            print(f"Error in audio playback: {e}")
        finally:
            self.is_playing = False

    def stop_audio(self):
        """Stop any currently playing audio"""
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
