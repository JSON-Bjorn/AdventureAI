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
        pygame.mixer.init()

    async def generate_speech(self, text: str) -> bool:
        """Generate speech from text using OpenAI's TTS"""
        try:
            # Generate speech using OpenAI's TTS
            response = self.client.audio.speech.create(
                model="tts-1",  # or "tts-1-hd" for higher quality
                voice="coral",  # Must be lowercase: coral, nova, shimmer, echo, onyx, fable, alloy
                input=text,
            )

            # Create a new BytesIO object and write the audio data
            audio_buffer = io.BytesIO()
            audio_buffer.write(response.content)
            audio_buffer.seek(0)  # Reset buffer position to start

            self.current_audio = audio_buffer
            return True

        except Exception as e:
            print(f"Error generating speech: {e}")
            return False

    def play_audio(self):
        """Play the current audio file"""
        if self.current_audio and not self.is_playing:
            try:
                # Reset audio position to start
                self.current_audio.seek(0)

                # Create a new thread for audio playback
                self.is_playing = True
                thread = threading.Thread(target=self._play_audio_thread)
                thread.daemon = True
                thread.start()
            except Exception as e:
                print(f"Error starting audio playback: {e}")
                self.is_playing = False

    def _play_audio_thread(self):
        """Internal method to play audio in a separate thread"""
        try:
            # Ensure we're at the start of the audio data
            self.current_audio.seek(0)

            # Load and play the audio
            try:
                pygame.mixer.music.load(self.current_audio)
            except Exception as e:
                print(f"Error loading audio: {e}")
                self.is_playing = False
                return

            try:
                pygame.mixer.music.play()

                # Wait for the audio to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)

            except Exception as e:
                print(f"Error during audio playback: {e}")

        except Exception as e:
            print(f"Error in audio thread: {e}")

        finally:
            self.is_playing = False
            # Reset the buffer position for next play
            if self.current_audio:
                self.current_audio.seek(0)

    def stop_audio(self):
        """Stop any currently playing audio"""
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
